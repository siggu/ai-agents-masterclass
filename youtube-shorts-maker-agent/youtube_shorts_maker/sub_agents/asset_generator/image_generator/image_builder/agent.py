from google.adk.agents import Agent
from google.adk.models import LiteLlm
from .prompt import IMAGE_BUILDER_DESCRIPTION, IMAGE_BUILDER_PROMPT
from pydantic import BaseModel, Field
from .tools import generate_images

MODEL = LiteLlm(model="openai/gpt-4o")

image_builder_agent = Agent(
    name="ImageBuilderAgent",
    description=IMAGE_BUILDER_DESCRIPTION,
    instruction=IMAGE_BUILDER_PROMPT,
    model=MODEL,
    output_key="image_builder_output",
    tools=[generate_images],
)
