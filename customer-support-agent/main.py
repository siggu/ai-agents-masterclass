import dotenv

dotenv.load_dotenv()
import asyncio
import json

import streamlit as st
from agents import Agent, InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered, Runner, SQLiteSession
from models import UserAccountContext
from my_agents.account_agent import account_agent
from my_agents.billing_agent import billing_agent
from my_agents.order_agent import order_agent
from my_agents.technical_agent import technical_agent
from my_agents.triage_agent import triage_agent
from openai import OpenAI

client = OpenAI()

# 에이전트 매핑
AGENTS = {
    "Account Agent": account_agent,
    "Billing Agent": billing_agent,
    "Order Agent": order_agent,
    "Technical Agent": technical_agent,
    "Triage Agent": triage_agent,
}

user_account_ctx = UserAccountContext(
    customer_id=1,
    name="Jeongmok",
    tier="basic",
    email="jeongmok@example.com",  # email 추가
)

if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        "chat-history",
        "customer-support-memory.db",
    )
session = st.session_state["session"]

if "agent" not in st.session_state:
    st.session_state.agent: Agent = triage_agent

if "handoff_info" not in st.session_state:
    st.session_state.handoff_info = None


async def paint_history():
    messages = await session.get_items()
    for message in messages:
        if "role" in message:
            if message["role"] == "system":
                st.info(message["content"])
                continue

            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.write(message["content"])
                else:
                    if message["type"] == "message":
                        raw_text = message["content"][0]["text"]
                        try:
                            parsed_data = json.loads(raw_text)
                            display_text = parsed_data.get("message", raw_text)
                        except json.JSONDecodeError:
                            display_text = raw_text

                        st.write(display_text.replace("$", "\$"))


asyncio.run(paint_history())


async def run_agent(message, is_handoff_continuation=False):
    with st.chat_message("ai"):
        text_placeholder = st.empty()
        response = ""

        try:
            stream = Runner.run_streamed(
                st.session_state.agent,
                message,
                session=session,
                context=user_account_ctx,
            )

            # 모든 이벤트 로깅 (디버깅용)
            async for event in stream.stream_events():
                # 디버그: 모든 이벤트 타입 확인
                if event.type not in ["raw_response_event"]:
                    print(f"DEBUG - Event type: {event.type}")

                # 텍스트 응답
                if event.type == "raw_response_event":
                    if event.data.type == "response.output_text.delta":
                        response += event.data.delta
                        text_placeholder.write(response.replace("$", "\$"))

                    # response.done 이벤트에서 tool 사용 확인
                    elif event.data.type == "response.done":
                        print(f"DEBUG - Response done event")
                        # 여기서 handoff 확인

                elif event.type == "agent_updated_stream_event":
                    if st.session_state.agent.name != event.new_agent.name:
                        st.write(
                            f"🤖 transferred from {st.session_state.agent.name} to {event.new_agent.name}"
                        )
                        st.session_state.agent = event.new_agent
                        text_placeholder = st.empty()

                        st.session_state["text_placeholder"] = text_placeholder
                        response = ""
        except OutputGuardrailTripwireTriggered as e:
            # Output guardrail이 트리거되면 출력된 텍스트를 모두 지우고 에러 메시지만 표시
            text_placeholder.empty()
            st.error(f"⚠️ Content blocked by security guardrail: {e.guardrail_result.guardrail.__class__.__name__}")
            st.info("The response was blocked because it contained inappropriate content for this agent.")
        except InputGuardrailTripwireTriggered as e:
            text_placeholder.empty()
            st.error(f"⚠️ Input blocked by security guardrail: {e.guardrail_result.guardrail.__class__.__name__}")
            st.info("Your request was blocked because it's not appropriate for this support system.")
        except Exception as e:
            if "text_placeholder" in st.session_state:
                st.session_state["text_placeholder"].empty()
            text_placeholder.empty()
            st.error(f"Error: {e}")


async def handle_user_message(message):
    """사용자 메시지 처리"""
    # 원본 메시지를 pending_handoff에 저장 (handoff 시 사용)
    if "pending_handoff" not in st.session_state:
        st.session_state.original_user_message = message

    await run_agent(message)


# 채팅 입력
message = st.chat_input("Write a message for your assistant")

if message:
    if "text_placeholder" in st.session_state:
        st.session_state["text_placeholder"].empty()

    if message:
        with st.chat_message("human"):
            st.write(message)
        asyncio.run(handle_user_message(message))

# 사이드바
with st.sidebar:
    st.title("💬 Customer Support Chat")

    reset = st.button("🔄 Reset Conversation")
    if reset:
        asyncio.run(session.clear_session())
        st.session_state.agent = triage_agent
        if "pending_handoff" in st.session_state:
            del st.session_state.pending_handoff
        if "original_user_message" in st.session_state:
            del st.session_state.original_user_message
        st.rerun()

    st.write("---")

    # 현재 에이전트 상태
    st.write("### 🤖 Agent Status")
    if "agent" in st.session_state:
        agent_name = st.session_state.agent.name

        # 에이전트별 색상/아이콘
        agent_icons = {
            "Triage Agent": "🎯",
            "Account Agent": "👤",
            "Billing Agent": "💰",
            "Order Agent": "📦",
            "Technical Agent": "🔧",
        }

        icon = agent_icons.get(agent_name, "🤖")
        st.success(f"{icon} **{agent_name}**")

        # Handoff 가능한 에이전트 표시
        if (
            hasattr(st.session_state.agent, "handoffs")
            and st.session_state.agent.handoffs
        ):
            with st.expander("Available Transfers"):
                for h in st.session_state.agent.handoffs:
                    if hasattr(h, "agent"):
                        transfer_agent = h.agent.name
                        transfer_icon = agent_icons.get(transfer_agent, "→")
                        st.write(f"{transfer_icon} {transfer_agent}")

    # Handoff 정보 표시
    if "pending_handoff" in st.session_state and st.session_state.pending_handoff:
        st.write("---")
        st.write("### 🔄 Handoff Info")
        info = st.session_state.pending_handoff
        st.write(f"**To:** {info.get('to_agent', 'N/A')}")
        st.write(f"**Reason:** {info.get('reason', 'N/A')}")
        st.write(f"**Issue:** {info.get('issue', 'N/A')}")

    st.write("---")

    # 디버그용 대화 기록 (토글)
    with st.expander("📜 Session History (Debug)"):
        history = asyncio.run(session.get_items())
        st.json(history)
