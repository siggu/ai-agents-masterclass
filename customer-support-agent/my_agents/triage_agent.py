import streamlit as st
from agents import (Agent, GuardrailFunctionOutput, RunContextWrapper, Runner,
                    handoff, input_guardrail)
from agents.extensions import handoff_filters
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from models import HandoffData, InputGuardRailOutput, UserAccountContext
from my_agents.account_agent import account_agent
from my_agents.billing_agent import billing_agent
from my_agents.order_agent import order_agent
from my_agents.technical_agent import technical_agent

input_guardrail_agent = Agent(
    name="Input Guardrail Agent",
    instructions="""
    Ensure the user's request specifically pertains to User Account details, Billing inquiries, Order information, or Technical Support issues, and is not off-topic. If the request is off-topic, return a reason for the tripwire. You can make small conversation with the user, specially at the beginning of the conversation, but don't help with requests that are not related to User Account details, Billing inquiries, Order information, or Technical Support issues.
""",
    output_type=InputGuardRailOutput,
)


@input_guardrail
async def off_topic_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
    input: str,
):
    result = await Runner.run(
        input_guardrail_agent,
        input,
        context=wrapper.context,
    )

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_off_topic,
    )


def dynamic_triage_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    return f"""
    {RECOMMENDED_PROMPT_PREFIX}
    You are a friendly customer support triage specialist. You help classify customer issues and route them to the right specialist team.
    
    Customer Information:
    - Name: {wrapper.context.name}
    - Email: {wrapper.context.email}
    - Tier: {wrapper.context.tier} {'(Priority Customer)' if wrapper.context.tier in ['premium', 'enterprise'] else ''}
    
    YOUR ROLE:
    1. Greet the customer warmly by name
    2. Understand their issue clearly
    3. Classify the issue into the correct category
    4. Explain briefly that you're connecting them with the right specialist
    5. Transfer them using the appropriate handoff tool
    
    CLASSIFICATION CATEGORIES:
    
    👤 ACCOUNT MANAGEMENT - Transfer here for:
    - Login problems, can't access account
    - Password reset requests
    - Profile updates, email changes
    - Account security, two-factor authentication
    - Account deletion, data export
    Examples: "Can't log in", "Forgot password", "Change my email"
    
    💰 BILLING SUPPORT - Transfer here for:
    - Payment issues, failed charges
    - Refunds and disputes
    - Subscription changes, upgrades/downgrades
    - Cancellations
    - Invoice problems
    Examples: "I was charged twice", "Need a refund", "Cancel subscription"
    
    📦 ORDER MANAGEMENT - Transfer here for:
    - Order status and tracking
    - Shipping and delivery issues
    - Returns and exchanges
    - Missing or wrong items
    - Product availability
    Examples: "Where's my order?", "Wrong item shipped", "Want to return"
    
    🔧 TECHNICAL SUPPORT - Transfer here for:
    - Product not working, bugs, errors
    - App crashes, performance issues
    - Feature questions, how-to help
    - Integration or setup problems
    Examples: "App won't load", "Getting error message", "How do I..."
    
    HANDOFF PROCESS:
    - Be concise - don't over-explain
    - Use this format: "I understand you need help with [issue]. Let me connect you with our [Team] specialist who can assist you right away."
    - Then immediately transfer using the appropriate tool
    
    IMPORTANT:
    - Don't try to solve the issue yourself - your job is only to route
    - Don't ask too many clarifying questions - if the category is reasonably clear, transfer immediately
    - Always be warm and professional
    - For {wrapper.context.tier} customers, mention their priority status when relevant
    """


def handle_handoff(
    wrapper: RunContextWrapper[UserAccountContext],
    input_data: HandoffData,
):
    """
    Handoff 발생 시 실행되는 콜백 함수
    Session state에 handoff 정보를 저장하여 main.py에서 처리할 수 있도록 함
    """
    # Streamlit session state에 handoff 정보 저장
    if "pending_handoff" not in st.session_state:
        st.session_state.pending_handoff = {}

    # 원본 사용자 메시지 가져오기
    original_message = st.session_state.get("original_user_message", "")

    # Handoff 정보 저장
    st.session_state.pending_handoff = {
        "to_agent": input_data.to_agent_name,
        "reason": input_data.reason,
        "issue_type": input_data.issue_type,
        "issue": input_data.issue_description,
        "original_message": original_message,
    }

    # 사이드바에 handoff 정보 표시 (디버깅용)
    with st.sidebar:
        with st.expander("🔄 Latest Handoff", expanded=True):
            st.write(f"**To:** {input_data.to_agent_name}")
            st.write(f"**Reason:** {input_data.reason}")
            st.write(f"**Type:** {input_data.issue_type}")
            st.write(f"**Issue:** {input_data.issue_description}")

    return input_data


def make_handoff(agent: Agent, description: str):
    """
    Handoff 객체 생성 헬퍼 함수
    """
    return handoff(
        agent=agent,
        tool_description_override=description,
        on_handoff=handle_handoff,
        input_type=HandoffData,
        input_filter=handoff_filters.remove_all_tools,  # 이전 tool calls 제거
    )


# 각 에이전트별 설명 (LLM이 언제 handoff를 해야 하는지 이해하도록)
account_agent_description = """Transfer to Account Agent for: login problems, password resets, account access issues, profile updates, email changes, account security, two-factor authentication, account deletion, or data export requests."""

billing_agent_description = """Transfer to Billing Agent for: payment issues, failed charges, refunds, subscription questions, plan changes, upgrades, downgrades, cancellations, invoice problems, or billing disputes."""

technical_agent_description = """Transfer to Technical Agent for: product errors, bugs, app crashes, loading issues, performance problems, feature questions, how-to help, integration problems, or setup assistance."""

order_agent_description = """Transfer to Order Agent for: order status inquiries, shipping questions, delivery issues, returns, exchanges, missing items, wrong items, tracking numbers, or product availability."""


# Triage Agent 정의
triage_agent = Agent(
    name="Triage Agent",
    instructions=dynamic_triage_agent_instructions,
    input_guardrails=[
        off_topic_guardrail,
    ],
    handoffs=[
        make_handoff(account_agent, account_agent_description),
        make_handoff(billing_agent, billing_agent_description),
        make_handoff(technical_agent, technical_agent_description),
        make_handoff(order_agent, order_agent_description),
    ],
)
