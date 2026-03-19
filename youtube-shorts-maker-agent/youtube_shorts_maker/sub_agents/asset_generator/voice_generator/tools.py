import base64
from google.genai import types
from openai import OpenAI
from google.adk.tools.tool_context import ToolContext
from typing import List, Dict, Any

client = OpenAI()


async def generate_narrations(
    tool_context: ToolContext,
    voice: str,
    voice_instructions: List[Dict[str, Any]],
):
    """
    OpenAI TTS API를 사용하여 나레이션 오디오를 생성하는 도구입니다.

    Args:
        tool_context (ToolContext): 도구 실행에 필요한 컨텍스트 정보
        voice (str): 선택한 목소리 (예: "alloy", "echo", "fable", "onyx", "nova", "shimmer")
        voice_instructions (List[Dict[str, Any]]): 각 장면에 대한 나레이션 텍스트와 지침이 포함된 딕셔너리 목록
            - input: 해당 장면에서 말할 정확한 텍스트
            - instructions: 장면 지속 시간과 내용에 맞는 속도 및 톤 지침
            - scene_id: 장면 번호

    Returns:
        생성된 나레이션 오디오 파일의 정보가 포함된 딕셔너리 목록
    """
    existing_artifacsts = await tool_context.list_artifacts()

    generated_narrations = []

    for instruction in voice_instructions:
        text_input = instruction.get("input")
        instructions = instruction.get("instructions")
        scene_id = instruction.get("scene_id")

        filename = f"scene_{scene_id}_narration.mp3"

        if filename in existing_artifacsts:
            generated_narrations.append(
                {
                    "scene_id": scene_id,
                    "filename": filename,
                    "input": text_input,
                    "instructions": instructions[:50],
                }
            )
            continue

        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            input=text_input,
            instructions=instructions,
        ) as response:
            audio_data = response.read()

        artifacts = types.Part(
            inline_data=types.Blob(
                mime_type="audio/mpeg",
                data=audio_data,
            )
        )

        await tool_context.save_artifact(filename, artifacts)

        generated_narrations.append(
            {
                "scene_id": scene_id,
                "filename": filename,
                "input": text_input,
                "instructions": instructions[:50],
            }
        )
    return {
        "success": True,
        "narrations": generated_narrations,
        "total_narrations": len(generated_narrations),
    }
