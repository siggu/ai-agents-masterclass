from google.adk.tools import ToolContext

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.models.lite_llm import LiteLlm

from .sub_agents.data_analyst import data_analyst
from .sub_agents.financial_analyst import financial_analyst
from .sub_agents.news_analyst import news_analyst

from .prompt import PROMPT

MODEL = LiteLlm("openai/gpt-4o-mini")


def save_advice_report(tool_context: ToolContext, summary: str):
    state = tool_context.state
    data_analyst_result = state.get("data_analysis_results", {})
    financial_analyst_result = state.get("financial_analysis_results", {})
    news_analyst_result = state.get("news_analysis_results", {})

    report = f"""
    # Financial Advice Report
    {summary}
    
    ## Data Analysis Report:
    {data_analyst_result}
    
    ## Financial Analysis Report:
    {financial_analyst_result}
    
    ## News Analysis Report:
    {news_analyst_result}
    """
    state["report"] = report
    return {"success": True}


financial_advisor = Agent(
    name="FinancialAdvisor",
    instruction=PROMPT,
    model=MODEL,
    tools=[
        AgentTool(agent=data_analyst),
        AgentTool(agent=financial_analyst),
        AgentTool(agent=news_analyst),
        save_advice_report,
    ],
)

root_agent = financial_advisor
