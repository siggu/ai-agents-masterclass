from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

MODEL = LiteLlm("openai/gpt-4o-mini")

weather_agent = Agent(
    name="WeatherAgent",
    instruction="당신은 날씨 관련 질문을 받아 사용자를 도와야 합니다.",
    model=MODEL,
)

root_agent = weather_agent
