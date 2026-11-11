from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

# 1. Đồng bộ Streamlit Secrets vào os.environ (cho Streamlit Community Cloud)
try:
    if hasattr(st, "secrets"):
        for k, v in st.secrets.items():
            if isinstance(v, str):
                os.environ.setdefault(k, v)
except Exception:
    pass

from env_loader import load_lab_env
from providers import make_provider
from providers.base import ToolCall
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
load_lab_env(ROOT)

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Cortex — Research Agent Workspace",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Inject CSS phong cách Cortex (Chống AI slop, màu sắc tinh tế, tương phản cao)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Reset toàn bộ theme về Light chuẩn Cortex */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        color: #111827 !important;
        background-color: #FAFAFC !important;
    }

    [data-testid="stAppViewContainer"] {
        background-color: #FAFAFC !important;
    }

    /* Ẩn deploy button và toolbar mặc định của Streamlit để giao diện sạch sẽ */
    .stDeployButton, [data-testid="stToolbar"] {
        display: none !important;
    }

    [data-testid="stHeader"] {
        background-color: rgba(250, 250, 252, 0.8) !important;
        backdrop-filter: blur(8px);
        border-bottom: 1px solid #F1F2F4;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #F8F9FA !important;
        border-right: 1px solid #E5E7EB !important;
        padding-top: 1.25rem !important;
    }
    
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-weight: 700;
        font-size: 1.25rem;
        color: #111827;
        margin-bottom: 1.25rem;
    }
    .sidebar-brand-badge {
        background: #EDE9FE;
        color: #7C3AED;
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.04em;
    }

    /* Nút New Chat: màu đen graphite pill như Cortex */
    button[kind="primary"] {
        background-color: #18181B !important;
        color: #FFFFFF !important;
        border: 1px solid #18181B !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.55rem 1rem !important;
        transition: all 0.15s ease !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
    }
    button[kind="primary"]:hover {
        background-color: #27272A !important;
        border-color: #27272A !important;
        transform: translateY(-1px);
        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.08) !important;
    }
    button[kind="primary"]:active {
        background-color: #09090B !important;
        transform: translateY(0);
    }

    /* Lịch sử chat theo mốc thời gian */
    .history-group-title {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #9CA3AF;
        margin-top: 1.25rem;
        margin-bottom: 0.45rem;
    }
    .history-item {
        padding: 0.45rem 0.65rem;
        border-radius: 8px;
        font-size: 0.825rem;
        color: #4B5563;
        margin-bottom: 0.2rem;
        cursor: pointer;
        transition: background 0.15s ease, color 0.15s ease;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .history-item:hover {
        background-color: #F3F4F6;
        color: #111827;
    }

    /* Thẻ sinh viên ở chân sidebar */
    .student-card {
        margin-top: 2rem;
        padding: 0.75rem 0.85rem;
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    }
    .student-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: #8B5CF6;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 0.85rem;
        flex-shrink: 0;
    }

    /* 3D Lavender Glass Orb (Hero Centerpiece) */
    .orb-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2.5rem 0 1.2rem 0;
    }
    .cortex-orb {
        width: 96px;
        height: 96px;
        border-radius: 50%;
        background: radial-gradient(circle at 35% 28%, #FFFFFF 0%, #F3E8FF 25%, #C084FC 55%, #8B5CF6 80%, #6D28D9 100%);
        box-shadow: 
            0 16px 36px -4px rgba(139, 92, 246, 0.35),
            inset -6px -6px 14px rgba(109, 40, 217, 0.45),
            inset 6px 6px 14px rgba(255, 255, 255, 0.95);
        animation: floatOrb 5s ease-in-out infinite;
    }
    @keyframes floatOrb {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-7px); }
    }

    /* Hero Typography */
    .hero-greeting {
        text-align: center;
        color: #8B5CF6;
        font-weight: 600;
        font-size: 1.15rem;
        margin-bottom: 0.4rem;
        letter-spacing: -0.01em;
    }
    .hero-title {
        text-align: center;
        color: #111827 !important;
        font-weight: 700;
        font-size: 2.25rem;
        letter-spacing: -0.03em;
        margin-bottom: 2.2rem;
        line-height: 1.2;
    }

    /* Suggestion Buttons styled as Cards with multiline support */
    div[data-testid="column"] button[kind="secondary"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 12px !important;
        padding: 1.1rem 1.15rem !important;
        color: #111827 !important;
        text-align: center !important;
        min-height: 110px !important;
        height: auto !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
    }
    div[data-testid="column"] button[kind="secondary"] div {
        white-space: normal !important;
        text-align: center !important;
    }
    div[data-testid="column"] button[kind="secondary"] p:first-child {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: #111827 !important;
        margin-bottom: 0.35rem !important;
        display: block !important;
        white-space: normal !important;
    }
    div[data-testid="column"] button[kind="secondary"] p:last-child {
        font-size: 0.8rem !important;
        color: #6B7280 !important;
        line-height: 1.4 !important;
        display: block !important;
        white-space: normal !important;
    }
    div[data-testid="column"] button[kind="secondary"]:hover {
        border-color: #C4B5FD !important;
        box-shadow: 0 6px 20px -2px rgba(139, 92, 246, 0.12) !important;
        transform: translateY(-2px);
        background-color: #FFFFFF !important;
    }

    /* Tool Call Inspector Box */
    .tool-execution-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin: 0.6rem 0;
    }
    .tool-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: #EDE9FE;
        color: #6D28D9;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        border: 1px solid #DDD6FE;
    }

    /* Chat bubble */
    .chat-user-msg {
        background-color: #F3F4F6;
        border: 1px solid #E5E7EB;
        border-radius: 14px 14px 2px 14px;
        padding: 0.85rem 1.15rem;
        color: #1F2937 !important;
        font-size: 0.95rem;
        margin-bottom: 0.85rem;
        margin-left: 3rem;
        line-height: 1.5;
    }
    .chat-agent-msg {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 14px 14px 14px 2px;
        padding: 1.1rem 1.35rem;
        color: #111827 !important;
        font-size: 0.95rem;
        margin-bottom: 1rem;
        margin-right: 3rem;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02);
        line-height: 1.6;
    }

    /* Expander styling for tool transparency */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 10px !important;
        margin-bottom: 0.75rem !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
    }

    /* Chat Input Bar */
    [data-testid="stChatInput"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.06) !important;
        padding: 0.35rem 0.6rem !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #111827 !important;
        background-color: transparent !important;
        font-size: 0.95rem !important;
    }
    [data-testid="stChatInput"] button {
        background-color: #8B5CF6 !important;
        color: #FFFFFF !important;
        border-radius: 50% !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return slug.strip("_") or "run"


def execute_tool_call(call: ToolCall) -> dict[str, Any]:
    func = TOOL_FUNCTIONS.get(call.name)
    if not func:
        return {
            "tool": call.name,
            "args": call.args,
            "result": {"error": "unknown_tool", "message": f"No local implementation for {call.name}"},
        }
    try:
        result = func(**call.args)
    except Exception as exc:
        result = {"error": type(exc).__name__, "message": str(exc)}
    return {"tool": call.name, "args": call.args, "result": result}


def tool_results_message(events: list[dict[str, Any]]) -> dict[str, str]:
    text = json.dumps(events, ensure_ascii=False, indent=2, default=str)
    return {
        "role": "user",
        "content": (
            "TOOL_RESULTS_JSON:\n"
            f"{text[:24000]}\n\n"
            "Use only these tool results. If the user asked for a digest and the items are ready, "
            "call the formatting tool. Otherwise answer the user directly with cited sources when available."
        ),
    }


def assistant_tool_message(response_text: str | None, calls: list[ToolCall]) -> dict[str, str]:
    call_summary = [{"name": call.name, "args": call.args} for call in calls]
    content = response_text or "I will call the selected tool(s)."
    return {
        "role": "assistant",
        "content": f"{content}\n\nTOOL_CALLS_JSON:\n{json.dumps(call_summary, ensure_ascii=False, indent=2)}",
    }


# Khởi tạo trạng thái phiên (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "transcript_id" not in st.session_state:
    st.session_state.transcript_id = f"ui_{datetime.now().strftime('%Y%m%dT%H%M%S%f')}"
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# Sidebar Content
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <span style="color:#7C3AED; font-size:1.4rem;">🔮</span> Cortex
            <span class="sidebar-brand-badge">RESEARCH AGENT</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("＋ Cuộc trò chuyện mới", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.session_state.history = []
        st.session_state.transcript_id = f"ui_{datetime.now().strftime('%Y%m%dT%H%M%S%f')}"
        st.session_state.pending_prompt = None
        st.rerun()

    st.markdown("<div style='height: 0.6rem;'></div>", unsafe_allow_html=True)
    
    # Cấu hình Artifact Version & Provider
    version_label = st.selectbox("Artifact Version", ["v5", "v4", "v3", "v2", "v1", "v0"], index=0)
    provider_name = st.selectbox("Provider", ["openrouter", "gemini", "openai"], index=0)
    model_override = st.text_input("Model (để trống = mặc định)", value="", placeholder="openai/gpt-4o-mini")

    st.markdown("<div class='history-group-title'>Lịch sử gần đây</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="history-item">🕒 Khảo sát nghiên cứu LLM Tool Use</div>
        <div class="history-item">📄 Tóm tắt công bố ArXiv 2402.0123</div>
        <div class="history-item">📡 Soạn thảo bản tin công nghệ tuần</div>
        """,
        unsafe_allow_html=True,
    )

    # Thẻ thông tin thành viên (Đoàn Anh Hùng)
    st.markdown(
        """
        <div class="student-card">
            <div class="student-avatar">AH</div>
            <div style="line-height: 1.25;">
                <div style="font-weight: 600; font-size: 0.85rem; color: #111827;">Đoàn Anh Hùng</div>
                <div style="font-size: 0.75rem; color: #6B7280;">2A202603880 · VinUni</div>
                <div style="font-size: 0.72rem; color: #10B981; font-weight: 500;">● Online (L3B Lab)</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Chuẩn bị Prompt, Tools và Provider
system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
tools_yaml_path = ARTIFACTS_DIR / "tools.yaml"

if not system_prompt_path.exists() or not tools_yaml_path.exists():
    st.error("Không tìm thấy tệp cấu hình tại starter_v0/artifacts/. Vui lòng kiểm tra lại.")
    st.stop()

system_prompt = system_prompt_path.read_text(encoding="utf-8")
tool_declarations = load_tool_declarations(tools_yaml_path)
openai_tools = to_openai_tools(tool_declarations)

try:
    provider = make_provider(provider_name)
except Exception as e:
    st.error(f"Lỗi khởi tạo provider {provider_name}: {e}")
    st.stop()

selected_model = model_override.strip() or getattr(provider, "default_model", None)
artifact_version = build_artifact_version(version_label, system_prompt_path, tools_yaml_path)

# Main Container
main_col1, main_col2, main_col3 = st.columns([1, 10, 1])
with main_col2:
    # Nếu chưa có tin nhắn nào, hiển thị Hero Header & 3D Lavender Orb
    if not st.session_state.messages:
        st.markdown(
            """
            <div class="orb-container">
                <div class="cortex-orb"></div>
            </div>
            <div class="hero-greeting">Xin chào, Research Team</div>
            <div class="hero-title">Hôm nay tôi có thể hỗ trợ gì cho bạn?</div>
            """,
            unsafe_allow_html=True,
        )

        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            if st.button("**🕒 Tóm tắt bài báo**\n\nTrích xuất các luận điểm cốt lõi của công bố khoa học qua công cụ summarize.", key="btn_s1", use_container_width=True):
                st.session_state.pending_prompt = "Hãy dùng công cụ summarize để tóm tắt văn bản sau trong 2 câu: 'Antigravity represents a leap forward in agentic workflows by coordinating specialized agents across parallel tasks. It ensures verifiable reproducibility and high-precision tool invocation without losing context.'"
                st.rerun()

        with col_s2:
            if st.button("**🔍 Tra cứu ArXiv**\n\nTìm kiếm công bố khoa học mới nhất về LLM tool-calling và đánh giá agent.", key="btn_s2", use_container_width=True):
                st.session_state.pending_prompt = "Hãy tra cứu các bài báo khoa học mới nhất trên arXiv về chủ đề 'Tool Calling Evaluation in Large Language Models'."
                st.rerun()

        with col_s3:
            if st.button("**📡 Xuất bản & Gửi tin**\n\nKiểm tra chính sách công ty và xin xác nhận trước khi đăng bài lên kênh Telegram.", key="btn_s3", use_container_width=True):
                st.session_state.pending_prompt = "Hãy soạn thảo một bản tóm tắt ngắn về các đột phá AI tuần này và đăng lên kênh Telegram cho tôi."
                st.rerun()

        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    # Hiển thị lịch sử tin nhắn trong phiên hiện tại
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user-msg"><b>Bạn:</b> {msg["content"]}</div>', unsafe_allow_html=True)
        elif msg["role"] == "assistant":
            # Nếu có tool events, hiển thị minh bạch trong expander mở sẵn (Rubric C6)
            if msg.get("tool_events"):
                with st.expander(f"🔧 Đã thực thi {len(msg['tool_events'])} lượt gọi công cụ", expanded=True):
                    for event in msg["tool_events"]:
                        st.markdown(f"<div class='tool-badge'>🔧 {event['tool']}</div>", unsafe_allow_html=True)
                        st.markdown("**Tham số truyền vào:**")
                        st.code(json.dumps(event.get("args", {}), ensure_ascii=False, indent=2), language="json")
                        st.markdown("**Kết quả trả về:**")
                        st.code(json.dumps(event.get("result", {}), ensure_ascii=False, indent=2), language="json")
            
            st.markdown(f'<div class="chat-agent-msg">{msg["content"]}</div>', unsafe_allow_html=True)

    # Xử lý input từ chat_input hoặc từ nút suggestion card
    user_input = st.chat_input("Nhập câu hỏi hoặc yêu cầu nghiên cứu của bạn...")
    prompt_to_run = user_input or st.session_state.pending_prompt

    if prompt_to_run:
        st.session_state.pending_prompt = None
        # Lưu câu hỏi của user
        st.session_state.messages.append({"role": "user", "content": prompt_to_run})
        st.rerun()

    # Nếu lượt cuối cùng là user chưa có câu trả lời của agent -> thực thi model loop
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        current_query = st.session_state.messages[-1]["content"]
        
        # Chuẩn bị working messages
        history_window = 5
        recent_history = st.session_state.history[-history_window * 2 :]
        messages = [
            {"role": "system", "content": system_prompt},
            *recent_history,
            {"role": "user", "content": current_query},
        ]

        with st.spinner("Cortex Agent đang suy luận và điều phối công cụ..."):
            working_messages = list(messages)
            rounds = []
            all_tool_events = []
            final_assistant_text = ""
            status_done = False
            max_rounds = 4

            for round_idx in range(1, max_rounds + 1):
                try:
                    response = provider.complete(working_messages, openai_tools, model=selected_model, temperature=0.0)
                except Exception as exc:
                    final_assistant_text = f"Lỗi gọi Provider ({type(exc).__name__}): {str(exc)}"
                    status_done = True
                    break

                calls = response.tool_calls
                round_record = {
                    "round": round_idx,
                    "assistant_text": response.text,
                    "tool_calls": [{"name": c.name, "args": c.args} for c in calls],
                    "tool_results": [],
                }

                if not calls:
                    final_assistant_text = response.text or "Đã hoàn thành phản hồi."
                    rounds.append(round_record)
                    status_done = True
                    break

                working_messages.append(assistant_tool_message(response.text, calls))
                non_clarification_events = []

                for call in calls:
                    event = execute_tool_call(call)
                    round_record["tool_results"].append(event)
                    all_tool_events.append(event)

                    result = event.get("result", {})
                    # Kiểm tra xem tool có yêu cầu người dùng làm rõ/xác nhận không
                    if isinstance(result, dict) and result.get("awaiting_user"):
                        question = result.get("question") or call.args.get("question") or "Vui lòng bổ sung thêm thông tin chi tiết."
                        final_assistant_text = question
                        status_done = True
                        break

                    non_clarification_events.append(event)

                rounds.append(round_record)
                if status_done:
                    break

                working_messages.append(tool_results_message(non_clarification_events))

            if not status_done and not final_assistant_text:
                final_assistant_text = f"Dừng sau {max_rounds} vòng gọi công cụ."

        # Lưu câu trả lời của agent vào session state
        st.session_state.messages.append({
            "role": "assistant",
            "content": final_assistant_text,
            "tool_events": all_tool_events,
        })
        st.session_state.history.append({"role": "user", "content": current_query})
        st.session_state.history.append({"role": "assistant", "content": final_assistant_text})

        # Lưu bản ghi transcript tương thích Rubric C6
        transcript_file = TRANSCRIPTS_DIR / f"{safe_slug(version_label)}_{safe_slug(provider_name)}_{st.session_state.transcript_id}.transcript.json"
        transcript_data = {
            "transcript_id": st.session_state.transcript_id,
            **artifact_version_dict(artifact_version),
            "provider": provider_name,
            "model": selected_model,
            "system_prompt": str(system_prompt_path),
            "tools": str(tools_yaml_path),
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "turns": [
                {
                    "turn_index": idx // 2 + 1,
                    "user": st.session_state.history[idx]["content"],
                    "assistant_text": st.session_state.history[idx + 1]["content"],
                }
                for idx in range(0, len(st.session_state.history) - 1, 2)
            ],
            "all_tool_events": all_tool_events,
        }
        transcript_file.write_text(json.dumps(transcript_data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

        st.rerun()
