from google.adk.agents import Agent, LoopAgent
from google.adk.models.lite_llm import LiteLlm
from .prompt import (
    EMAIL_OPTIMIZER_DESCRIPTION,
    TONE_STYLIST_DESCRIPTION,
    CLARITY_EDITOR_DESCRIPTION,
    LITERARY_CRITIC_DESCRIPTION,
    EMAIL_SYNTHESIZER_DESCRIPTION,
    PERSUASION_STRATEGIST_DESCRIPTION,
    TONE_STYLIST_INSTRUCTION,
    CLARITY_EDITOR_INSTRUCTION,
    LITERARY_CRITIC_INSTRUCTION,
    EMAIL_SYNTHESIZER_INSTRUCTION,
    PERSUASION_STRATEGIST_INSTRUCTION,
)
from google.adk.tools.tool_context import ToolContext

MODEL = LiteLlm(model="openai/gpt-4o-mini")

clarity_agent = Agent(
    name="ClarityEditorAgent",
    model=MODEL,
    description=CLARITY_EDITOR_DESCRIPTION,
    instruction=CLARITY_EDITOR_INSTRUCTION,
    output_key="clarity_output",
)

tone_stylist_agent = Agent(
    name="ToneStylistAgent",
    model=MODEL,
    description=TONE_STYLIST_DESCRIPTION,
    instruction=TONE_STYLIST_INSTRUCTION,
    output_key="tone_output",
)

persuation_agent = Agent(
    name="PersuationAgent",
    model=MODEL,
    description=PERSUASION_STRATEGIST_DESCRIPTION,
    instruction=PERSUASION_STRATEGIST_INSTRUCTION,
    output_key="persuasion_output",
)


def escalate_email_complete(tool_context: ToolContext):
    """이메일이 괜찮을 때만 이 tool을 사용하시오."""
    tool_context.actions.escalate = True


email_synthesizer_agent = Agent(
    name="EmailSynthesizerAgent",
    model=MODEL,
    description=EMAIL_SYNTHESIZER_DESCRIPTION,
    instruction=EMAIL_SYNTHESIZER_INSTRUCTION,
    output_key="synthesized_output",
)

literary_critic_agent = Agent(
    name="LiteraryCriticAgent",
    model=MODEL,
    description=LITERARY_CRITIC_DESCRIPTION,
    instruction=LITERARY_CRITIC_INSTRUCTION,
    tools=[
        escalate_email_complete,
    ],
)

eamil_refiner_agent = LoopAgent(
    name="Email_Refiner_Agent",
    max_iterations=50,
    description=EMAIL_OPTIMIZER_DESCRIPTION,
    sub_agents=[
        clarity_agent,
        tone_stylist_agent,
        persuation_agent,
        email_synthesizer_agent,
        literary_critic_agent,
    ],
)

root_agent = eamil_refiner_agent
