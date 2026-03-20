import base64
from google.genai import types
from google.adk.tools.tool_context import ToolContext

# ─────────────────────────────────────────────
# 이미지 생성 제공자 설정: "openai" 또는 "genai"
IMAGE_PROVIDER = "openai"
# ─────────────────────────────────────────────


async def _generate_images_openai(tool_context: ToolContext):
    from openai import OpenAI

    client = OpenAI()

    prompt_builder_output = tool_context.state.get("prompt_builder_output")
    optimized_prompts = prompt_builder_output.get("optimized_prompts")
    existing_artifacts = await tool_context.list_artifacts()
    generated_images = []

    for prompt in optimized_prompts:
        scene_id = prompt.get("scene_id")
        enhanced_prompt = prompt.get("enhanced_prompt")
        filename = f"scene_{scene_id}_image.jpeg"

        if filename in existing_artifacts:
            generated_images.append(
                {
                    "scene_id": scene_id,
                    "prompt": enhanced_prompt[:100],
                    "filename": filename,
                }
            )
            continue

        image = client.images.generate(
            model="gpt-image-1.5",
            prompt=enhanced_prompt,
            n=1,
            quality="low",
            moderation="low",
            output_format="jpeg",
            background="opaque",
            size="1024x1536",
        )

        image_bytes = base64.b64decode(image.data[0].b64_json)

        artifact = types.Part(
            inline_data=types.Blob(mime_type="image/jpeg", data=image_bytes)
        )
        await tool_context.save_artifact(filename=filename, artifact=artifact)

        generated_images.append(
            {
                "scene_id": scene_id,
                "prompt": enhanced_prompt[:100],
                "filename": filename,
            }
        )

    return {
        "total_images": len(generated_images),
        "generated_images": generated_images,
        "status": "complete",
    }


async def _generate_images_genai(tool_context: ToolContext):
    import os
    from google import genai

    client = genai.Client(api_key=os.environ.get("GENAI_API_KEY"))

    prompt_builder_output = tool_context.state.get("prompt_builder_output")
    optimized_prompts = prompt_builder_output.get("optimized_prompts")
    existing_artifacts = await tool_context.list_artifacts()
    generated_images = []

    for prompt in optimized_prompts:
        scene_id = prompt.get("scene_id")
        enhanced_prompt = prompt.get("enhanced_prompt")
        filename = f"scene_{scene_id}_image.jpeg"

        if filename in existing_artifacts:
            generated_images.append(
                {
                    "scene_id": scene_id,
                    "prompt": enhanced_prompt[:100],
                    "filename": filename,
                }
            )
            continue

        response = client.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=f"Generate a vertical 9:16 image for YouTube Shorts: {enhanced_prompt}",
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )

        image_bytes = None
        mime_type = "image/jpeg"
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                image_bytes = part.inline_data.data
                mime_type = part.inline_data.mime_type
                break

        if not image_bytes:
            raise ValueError(f"No image returned for scene {scene_id}")

        artifact = types.Part(
            inline_data=types.Blob(mime_type=mime_type, data=image_bytes)
        )
        await tool_context.save_artifact(filename=filename, artifact=artifact)

        generated_images.append(
            {
                "scene_id": scene_id,
                "prompt": enhanced_prompt[:100],
                "filename": filename,
            }
        )

    return {
        "total_images": len(generated_images),
        "generated_images": generated_images,
        "status": "complete",
    }


# IMAGE_PROVIDER 설정에 따라 사용할 함수 선택
if IMAGE_PROVIDER == "genai":
    generate_images = _generate_images_genai
else:
    generate_images = _generate_images_openai
