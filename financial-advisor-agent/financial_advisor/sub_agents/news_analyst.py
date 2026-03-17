from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from tools import web_search_tool

MODEL = LiteLlm(model="openai/gpt-4o-mini")


news_analyst = Agent(
    name="NewsAnalyst",
    model=MODEL,
    description="웹 검색 도구를 사용하여 실제 웹 콘텐츠를 검색하고 수집합니다.",
    instruction="""
    당신은 웹 도구를 활용하여 최신 정보를 찾는 뉴스 분석 전문가입니다. 담당 업무:

    1. **웹 검색**: web_search_tool()을 사용하여 기업에 관한 최신 뉴스를 검색합니다.
    3. **결과 요약**: 발견한 내용과 그 관련성을 설명합니다.

    **사용 가능한 웹 도구:**
    - **web_search_tool()**: 기업 뉴스를 위한 Firecrawl 웹 검색

    외부 API를 사용하여 최신 정보를 위한 웹 콘텐츠를 검색하고 수집합니다.
    """,
    output_key="news_analysis_results",
    tools=[
        web_search_tool,
    ],
)
