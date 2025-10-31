from langgraph.graph import END, START, StateGraph
from langgraph.types import Send, interrupt
from typing import TypedDict
import subprocess
from openai import OpenAI
import textwrap
from langchain.chat_models import init_chat_model
from typing_extensions import Annotated
import operator
import base64
from dotenv import load_dotenv

load_dotenv()

llm = init_chat_model("openai:gpt-4o-mini")


class State(TypedDict):
    video_file: str
    audio_file: str
    transcription: str
    summaries: Annotated[list[str], operator.add]
    thumbnail_prompts: Annotated[list[str], operator.add]
    thumbnail_sketches: Annotated[list[str], operator.add]
    final_summary: str
    user_feedback: str
    chosen_prompt: str


def extract_audio(state: State):
    output_file = state["video_file"].replace("mp4", "mp3")
    command = [
        "ffmpeg",
        "-i",
        state["video_file"],
        "-filter:a",
        "atempo=2.0",
        output_file,
        "-y",
    ]
    subprocess.run(command)
    return {
        "audio_file": output_file,
    }


def transcribe_audio(state: State):
    client = OpenAI()
    with open(state["audio_file"], "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            response_format="text",
            file=audio_file,
            language="en",
            prompt="",
        )
        return {"transcription": transcription}


def dispatch_summarizer(state: State):
    transcribtion = state["transcription"]
    chunks = []

    for idx, chunk in enumerate(textwrap.wrap(transcribtion, 500)):
        chunks.append({"id": idx + 1, "chunk": chunk})

    return [Send("summarize_chunk", chunk) for chunk in chunks]


def summarize_chunk(chunk):
    chunk_id = chunk["id"]
    chunk = chunk["chunk"]

    response = llm.invoke(
        f"""
        다음의 텍스트를 요약하세요.
        
        Text: {chunk}
        """
    )
    summary = f"[Chunk {chunk_id} Summary]: {response.content}"
    return {"summaries": [summary]}


def finalize_summary(state: State):
    all_summaries = "\n".join(state["summaries"])

    prompt = f"""
    당신은 하나의 영상에서 나온 텍스트의 여러 청크들로 만든 요약본을 받았습니다.
    
    모든 핵심 포인트를 결합한 종합 요약본을 작성하세요.
    
    Individual Summaries:
    {all_summaries}
    """

    response = llm.invoke(prompt)

    return {"final_summary": response.content}


def dispatch_artists(state: State):
    return [
        Send("generate_thumbnail", {"id": i, "summary": state["final_summary"]})
        for i in [1, 2, 3]
    ]


def generate_thumbnail(args):
    concept_id = args["id"]
    summary = args["summary"]

    prompt = f"""
    이 영상 요약본을 기반으로, 유튜브 썸네일을 만드는 상세한 비주얼 프롬프트를 작성하세요.
    
    시청자들을 끌어들일 수 있도록 다음 내용을 포함시키는 상세한 썸네일 이미지 생성 프롬프트를 작성하세요. :
    - 메인 시각 요소
    - 색상 조합
    - 텍스트 오버레이
    - 전반적인 구도
    
    영상 요약본: {summary}
    """

    response = llm.invoke(prompt)

    thumbnail_prompt = response.content

    client = OpenAI()

    result = client.images.generate(
        model="gpt-image-1",
        prompt=thumbnail_prompt,
        quality="low",
        moderation="low",
        size="auto",
    )

    image_bytes = base64.b64decode(result.data[0].b64_json)

    filename = f"thumbnail_{concept_id}.png"

    with open(filename, "wb") as file:
        file.write(image_bytes)

    return {
        "thumbnail_prompts": [thumbnail_prompt],
        "thumbnail_sketches": [filename],
    }


def human_feedback(state: State):
    answer = interrupt(
        {
            "chosen_thumbnail_number": "어느 썸네일이 가장 마음에 드셨나요? (1, 2, 3 중 선택)",
            "user_feedback": "최종 썸네일에 원하는 피드백이나 변경사항을 제공해 주세요.",
        }
    )
    user_feedback = answer["user_feedback"]

    # --- START OF FIX ---

    # Get the user's choice. Default to "1" if it's an empty string or None.
    chosen_thumbnail_number_str = answer.get("chosen_thumbnail_number") or "1"

    try:
        # Try to convert the string to a number
        chosen_thumbnail_number = int(chosen_thumbnail_number_str)

        # Check if the number is within the valid range of prompts we have
        if not (1 <= chosen_thumbnail_number <= len(state["thumbnail_prompts"])):
            # If it's out of range (e.g., 0, 4, 5), default to 1
            chosen_thumbnail_number = 1

    except ValueError:
        # If the input wasn't a number at all (e.g., "abc"), default to 1
        chosen_thumbnail_number = 1

        # --- END OF FIX ---

    return {
        "user_feedback": user_feedback,
        # Now, chosen_thumbnail_number is guaranteed to be a valid integer (e.g., 1, 2, or 3)
        "chosen_prompt": state["thumbnail_prompts"][chosen_thumbnail_number - 1],
    }


def generate_hd_thumbnail(state: State):
    chosen_prompt = state["chosen_prompt"]
    user_feedback = state["user_feedback"]

    prompt = f"""
    당신은 전문 유튜브 썸네일 디자이너입니다. 이 원본 썸네일 프롬프트를 가지고 유저의 특정 피드백을 반영한 더 향상된 버전을 만들어 주세요.
    
    원본 프롬프트: {chosen_prompt}
    
    유저 피드백: {user_feedback}
    
    다음 요구사항을 충족하는 고해상도 썸네일 이미지를 위한 상세한 프롬프트를 작성하세요:
    향상된 프롬프트를 만듭니다:
    1. 원래 프롬프트에서 핵심 개념을 유지합니다
    2. 사용자의 피드백 요청을 구체적으로 처리하고 구현합니다
    3. 전문 YouTube 썸네일 사양을 추가합니다:
        - 높은 대비와 대담한 시각적 요소
        - 눈을 사로잡는 명확한 초점
        - 전문 조명 및 구성
        - 가장자리에서 넉넉한 여백으로 최적의 텍스트 배치와 가독성 제공
        - 눈에 띄고 주목받는 색상
        - 작은 썸네일 크기에서 잘 작동하는 요소들
        - **중요**: 텍스트와 이미지 테두리 사이에 항상 적절한 여백/패딩을 확보하세요
    """

    response = llm.invoke(prompt)

    final_thumbnail_prompt = response.content

    client = OpenAI()

    result = client.images.generate(
        model="gpt-image-1",
        prompt=final_thumbnail_prompt,
        quality="high",
        moderation="low",
        size="auto",
    )

    image_bytes = base64.b64decode(result.data[0].b64_json)

    filename = "thumbnail_final.jpg"

    with open(filename, "wb") as file:
        file.write(image_bytes)


graph_builder = StateGraph(State)

graph_builder.add_node("extract_audio", extract_audio)
graph_builder.add_node("transcribe_audio", transcribe_audio)
graph_builder.add_node("summarize_chunk", summarize_chunk)
graph_builder.add_node("finalize_summary", finalize_summary)
graph_builder.add_node("generate_thumbnail", generate_thumbnail)
graph_builder.add_node("human_feedback", human_feedback)
graph_builder.add_node("generate_hd_thumbnail", generate_hd_thumbnail)

graph_builder.add_edge(START, "extract_audio")
graph_builder.add_edge("extract_audio", "transcribe_audio")
graph_builder.add_conditional_edges(
    "transcribe_audio", dispatch_summarizer, ["summarize_chunk"]
)
graph_builder.add_edge("summarize_chunk", "finalize_summary")
graph_builder.add_conditional_edges(
    "finalize_summary", dispatch_artists, ["generate_thumbnail"]
)
graph_builder.add_edge("generate_thumbnail", "human_feedback")
graph_builder.add_edge("human_feedback", "generate_hd_thumbnail")
graph_builder.add_edge("generate_hd_thumbnail", END)

graph = graph_builder.compile(name="thumbnail_maker")
