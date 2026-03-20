import io
import wave
from typing import Any, Dict, List

from google.genai import types
from google.adk.tools.tool_context import ToolContext

# ─────────────────────────────────────────────
# TTS 제공자 설정: "openai" 또는 "genai"
TTS_PROVIDER = "openai"
# ─────────────────────────────────────────────


async def _generate_narrations_openai(
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
    from openai import OpenAI

    client = OpenAI()

    existing_artifacts = await tool_context.list_artifacts()
    generated_narrations = []

    for instruction in voice_instructions:
        text_input = instruction.get("input")
        instructions = instruction.get("instructions")
        scene_id = instruction.get("scene_id")
        filename = f"scene_{scene_id}_narration.mp3"

        if filename in existing_artifacts:
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

        artifact = types.Part(
            inline_data=types.Blob(mime_type="audio/mpeg", data=audio_data)
        )
        await tool_context.save_artifact(filename, artifact)

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


async def _generate_narrations_genai(
    tool_context: ToolContext,
    voice: str,
    voice_instructions: List[Dict[str, Any]],
):
    """
    Gemini TTS API를 사용하여 나레이션 오디오를 생성하는 도구입니다.

    Args:
        tool_context (ToolContext): 도구 실행에 필요한 컨텍스트 정보
        voice (str): 선택한 목소리 (예: "Kore", "Puck", "Charon", "Fenrir", "Aoede")
        voice_instructions (List[Dict[str, Any]]): 각 장면에 대한 나레이션 텍스트와 지침이 포함된 딕셔너리 목록
            - input: 해당 장면에서 말할 정확한 텍스트
            - instructions: 장면 지속 시간과 내용에 맞는 속도 및 톤 지침
            - scene_id: 장면 번호

    Returns:
        생성된 나레이션 오디오 파일의 정보가 포함된 딕셔너리 목록
    """
    import os
    from google import genai

    client = genai.Client(api_key=os.environ.get("GENAI_API_KEY"))

    existing_artifacts = await tool_context.list_artifacts()
    generated_narrations = []

    for instruction in voice_instructions:
        text_input = instruction.get("input")
        instructions = instruction.get("instructions")
        scene_id = instruction.get("scene_id")
        filename = f"scene_{scene_id}_narration.wav"

        if filename in existing_artifacts:
            generated_narrations.append(
                {
                    "scene_id": scene_id,
                    "filename": filename,
                    "input": text_input,
                    "instructions": instructions[:50],
                }
            )
            continue

        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=f"[{instructions}]: {text_input}",
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice,
                        )
                    )
                ),
            ),
        )

        pcm_data = response.candidates[0].content.parts[0].inline_data.data

        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(pcm_data)

        artifact = types.Part(
            inline_data=types.Blob(mime_type="audio/wav", data=buffer.getvalue())
        )
        await tool_context.save_artifact(filename=filename, artifact=artifact)

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


# TTS_PROVIDER 설정에 따라 사용할 함수 선택
if TTS_PROVIDER == "genai":
    generate_narrations = _generate_narrations_genai
else:
    generate_narrations = _generate_narrations_openai
