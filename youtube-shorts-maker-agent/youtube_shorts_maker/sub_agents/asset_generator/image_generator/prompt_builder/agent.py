from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .prompt import PROMPT_BUILDER_DESCRIPTION, PROMPT_BUILDER_PROMPT
from pydantic import BaseModel, Field
from typing import List

MODEL = LiteLlm(model="openai/gpt-4o-mini")


class OptimizedPrompt(BaseModel):
    scene_id: int = Field(
        description="최적화된 프롬프트가 해당하는 콘텐츠 플랜의 장면 ID입니다."
    )
    enhanced_prompt: str = Field(description="최적화된 프롬프트입니다.")


class PromptBuilderOutput(BaseModel):
    optimized_prompts: List[OptimizedPrompt] = Field(
        description="각 장면에 대한 최적화된 프롬프트의 배열입니다."
    )


prompt_builder_agent = Agent(
    name="PromptBuilderAgent",
    model=MODEL,
    description=PROMPT_BUILDER_DESCRIPTION,
    instruction=PROMPT_BUILDER_PROMPT,
    output_key="prompt_builder_output",
    output_schema=PromptBuilderOutput,
)
