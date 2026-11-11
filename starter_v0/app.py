import streamlit as st
from pathlib import Path

# Import các hàm từ file chat.py và các module có sẵn của bạn
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from chat import run_model_tool_loop, trim_history

# Khởi tạo môi trường
ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
load_lab_env(ROOT)

st.set_page_config(page_title="Research Agent", page_icon="🤖", layout="centered")

st.title("🤖 Research Agent Chat")

# 1. KHỞI TẠO SESSION STATE (Lưu trữ trạng thái hội thoại và cấu hình)
if "history" not in st.session_state:
    st.session_state.history = []

if "system_prompt" not in st.session_state:
    prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    st.session_state.system_prompt = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else "You are a helpful assistant."

if "openai_tools" not in st.session_state:
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    if tools_path.exists():
        st.session_state.openai_tools = to_openai_tools(load_tool_declarations(tools_path))
    else:
        st.session_state.openai_tools = []

# 2. THANH BÊN (SIDEBAR) ĐỂ CẤU HÌNH
with st.sidebar:
    st.header("⚙️ Cấu hình Agent")
    provider_choice = st.selectbox("Provider", ["openrouter","gemini", "openai", "anthropic", "ollama"], index=0)
    model_choice = st.text_input("Model (để trống dùng mặc định)", value="")
    max_rounds = st.slider("Max Tool Rounds", 1, 10, 4)
    history_window = st.slider("History Window", 1, 10, 5)
    
    if st.button("🗑️ Xóa lịch sử chat"):
        st.session_state.history = []
        st.rerun()

# Khởi tạo provider dựa trên lựa chọn ở sidebar
provider = make_provider(provider_choice)
model_to_use = model_choice if model_choice.strip() else getattr(provider, "default_model", None)

# 3. HIỂN THỊ LỊCH SỬ CHAT
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. XỬ LÝ KHUNG NHẬP CHAT
if user_text := st.chat_input("Nhập câu hỏi của bạn..."):
    # Hiển thị tin nhắn của user ngay lập tức
    st.session_state.history.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    # Chuẩn bị dữ liệu gửi đi (kèm system prompt và lịch sử)
    messages = [
        {"role": "system", "content": st.session_state.system_prompt},
        *trim_history(st.session_state.history[:-1], history_window),
        {"role": "user", "content": user_text},
    ]

    # Xử lý phản hồi từ Agent
    with st.chat_message("assistant"):
        with st.spinner(f"Agent đang suy nghĩ (Provider: {provider_choice})..."):
            try:
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=st.session_state.openai_tools,
                    model=model_to_use,
                    max_tool_rounds=max_rounds,
                )
                
                assistant_text = result.get("assistant_text", "Không có phản hồi.")
                st.markdown(assistant_text)
                
                # Hiển thị chi tiết các Tool đã gọi dưới dạng hộp thoại mở rộng (Expander)
                tool_events = result.get("tool_events", [])
                if tool_events:
                    with st.expander("🛠️ Xem chi tiết các Tool đã sử dụng"):
                        st.json(tool_events)

                # Lưu tin nhắn của trợ lý vào lịch sử
                st.session_state.history.append({"role": "assistant", "content": assistant_text})
                
            except Exception as e:
                st.error(f"Lỗi: {e}")