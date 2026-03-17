from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

MODEL = LiteLlm("openai/gpt-4o-mini")


def get_weather(city: str):
    return f"{city}의 현재 날씨는 맑음입니다."


def convert_units(degrees: int):
    return f"그것은 25도 입니다."


geo_agent = Agent(
    name="GeoAgent",
    instruction="당신은 지리 관련 질문을 받아 사용자를 도와야 합니다.",
    model=MODEL,
    description="이 에이전트는 지리 관련 질문이 있다면 이 에이전트로 전달되어야 합니다.",
)

weather_agent = Agent(
    name="WeatherAgent",
    instruction="당신은 날씨 관련 질문을 받아 사용자를 도와야 합니다.",
    model=MODEL,
    tools=[
        get_weather,
        convert_units,
    ],
    sub_agents=[
        geo_agent,
    ],
)

root_agent = weather_agent
