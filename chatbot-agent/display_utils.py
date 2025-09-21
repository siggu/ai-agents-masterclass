import json

import streamlit as st


def display_tool_list(message: dict):
    """'mcp_list_tools' 타입의 메시지를 받아 도구 목록을 표시합니다. (번역 기능 없음)"""
    server_label = message.get("server_label", "AI")
    expander_title = f"'{server_label}'에서 사용 가능한 도구 목록입니다."

    # expanded=False 로 설정하여 기본적으로 닫혀있도록 합니다.
    with st.expander(expander_title, expanded=False):
        tools = message.get("tools", [])
        if not tools:
            st.write("사용 가능한 도구가 정의되지 않았습니다.")
            return

        for tool in tools:
            st.markdown(f"#### 🛠️ `{tool.get('name', '이름 없음')}`")
            # 원본 설명을 그대로 표시합니다.
            st.write(tool.get("description", "설명 없음"))

            if "input_schema" in tool:
                st.caption("Parameters:")
                st.code(
                    json.dumps(tool["input_schema"], indent=2, ensure_ascii=False),
                    language="json",
                )
            st.divider()
