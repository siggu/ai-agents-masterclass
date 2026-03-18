from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .prompt import CONTENT_PLANNER_DESCRIPTION, CONTENT_PLANNER_PROMPT
from .models import ContentPlanOutput


MODEL = LiteLlm("openai/gpt-4o-mini")

content_planner_agent = Agent(
    name="ContentPlannerAgent",
    model=MODEL,
    description=CONTENT_PLANNER_DESCRIPTION,
    instruction=CONTENT_PLANNER_PROMPT,
    output_key="content_planner_output",
    output_schema=ContentPlanOutput,
)

root_agent = content_planner_agent
