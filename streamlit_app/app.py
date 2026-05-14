"""Streamlit 前端 — 用户登录 + 多轮会话管理 + 对话。"""

from __future__ import annotations

import requests
import streamlit as st

# ── 配置 ──
API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="智能客服助手",
    page_icon="🤖",
    layout="wide",
)


# ═══════════════════════════════════════════════════════════
# Session State
# ═══════════════════════════════════════════════════════════

def init_state():
    defaults: dict[str, object] = {
        "token": None,
        "user_id": None,
        "username": None,
        "current_session_id": None,
        "messages": [],
        "sessions": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ═══════════════════════════════════════════════════════════
# API Helpers
# ═══════════════════════════════════════════════════════════

def _headers() -> dict[str, str]:
    h = {"Content-Type": "application/json"}
    if st.session_state.token:
        h["Authorization"] = f"Bearer {st.session_state.token}"
    return h


def _api_post(path: str, body: dict | None = None) -> requests.Response:
    return requests.post(f"{API_BASE}{path}", json=body, headers=_headers())


def _api_get(path: str) -> requests.Response:
    return requests.get(f"{API_BASE}{path}", headers=_headers())


def _api_delete(path: str) -> requests.Response:
    return requests.delete(f"{API_BASE}{path}", headers=_headers())


# ═══════════════════════════════════════════════════════════
# 登录/注册页
# ═══════════════════════════════════════════════════════════

def render_login_page():
    st.title("🤖 智能客服助手")
    st.caption("基于 LangChain ReAct Agent + RAG 知识库")

    tab1, tab2 = st.tabs(["登录", "注册"])

    with tab1:
        username = st.text_input("用户名", key="login_user")
        password = st.text_input("密码", type="password", key="login_pass")
        if st.button("登录", use_container_width=True, key="btn_login"):
            if not username or not password:
                st.error("请输入用户名和密码")
                return
            r = _api_post("/api/auth/login", {"username": username, "password": password})
            if r.status_code == 200:
                data = r.json()
                st.session_state.token = data["token"]
                st.session_state.user_id = data["user_id"]
                st.session_state.username = data["username"]
                st.rerun()
            else:
                st.error(r.json().get("detail", "登录失败"))

    with tab2:
        new_user = st.text_input("用户名", key="reg_user")
        new_pass = st.text_input("密码", type="password", key="reg_pass")
        new_email = st.text_input("邮箱 (可选)", key="reg_email")
        if st.button("注册", use_container_width=True, key="btn_register"):
            if len(new_user) < 3:
                st.error("用户名至少3个字符")
                return
            if len(new_pass) < 6:
                st.error("密码至少6个字符")
                return
            r = _api_post("/api/auth/register", {
                "username": new_user,
                "password": new_pass,
                "email": new_email or "",
            })
            if r.status_code == 200:
                data = r.json()
                st.session_state.token = data["token"]
                st.session_state.user_id = data["user_id"]
                st.session_state.username = data["username"]
                st.rerun()
            else:
                st.error(r.json().get("detail", "注册失败"))


# ═══════════════════════════════════════════════════════════
# 主界面
# ═══════════════════════════════════════════════════════════

def render_main_page():
    _render_sidebar()
    _render_chat_area()


def _render_sidebar():
    with st.sidebar:
        st.subheader(f"👤 {st.session_state.username}")

        if st.button("➕ 新对话", use_container_width=True):
            st.session_state.current_session_id = None
            st.session_state.messages = []
            st.rerun()

        st.divider()
        st.caption("📋 历史会话")

        # 加载会话列表
        try:
            r = _api_get("/api/sessions")
            if r.status_code == 200:
                st.session_state.sessions = r.json()
        except Exception:
            pass

        for sess in st.session_state.sessions:
            col1, col2 = st.columns([5, 1])
            with col1:
                label = sess["title"] if sess["title"] != "新对话" else f"对话 {sess['id'][:6]}"
                if st.button(
                    f"💬 {label}",
                    key=f"sess_{sess['id']}",
                    use_container_width=True,
                ):
                    st.session_state.current_session_id = sess["id"]
                    _load_session_messages(sess["id"])
                    st.rerun()
            with col2:
                if st.button("✕", key=f"del_{sess['id']}"):
                    try:
                        _api_delete(f"/api/sessions/{sess['id']}")
                    except Exception:
                        pass
                    if st.session_state.current_session_id == sess["id"]:
                        st.session_state.current_session_id = None
                        st.session_state.messages = []
                    st.rerun()

        st.divider()

        st.markdown(
            "\n".join([
                "- 知识问答",
                "- 使用报告",
                "- 多轮对话记忆",
            ])
        )

        st.divider()
        if st.button("🚪 退出登录", use_container_width=True):
            for k in ("token", "user_id", "username",
                       "current_session_id", "sessions"):
                st.session_state[k] = None
            st.session_state.messages = []
            st.rerun()


def _load_session_messages(session_id: str):
    """从后端加载指定会话的历史消息。"""
    try:
        r = _api_get(f"/api/sessions/{session_id}/messages")
        if r.status_code == 200:
            st.session_state.messages = [
                {"role": m["role"], "content": m["content"]}
                for m in r.json()
            ]
    except Exception:
        st.session_state.messages = []


def _render_chat_area():
    st.title("🤖 智能客服助手")
    st.caption("基于 LangChain ReAct Agent + RAG — 支持多轮对话")

    # 渲染历史消息
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 输入框
    prompt = st.chat_input("请输入你的问题")
    if not prompt:
        return

    # 显示用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 调用后端流式 API
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_answer: list[str] = []

        try:
            body: dict = {"query": prompt}
            if st.session_state.current_session_id:
                body["session_id"] = st.session_state.current_session_id

            with requests.post(
                f"{API_BASE}/api/chat",
                json=body,
                headers=_headers(),
                stream=True,
                timeout=90,
            ) as resp:
                if resp.status_code == 401:
                    placeholder.error("登录已过期，请重新登录")
                    _logout()
                    st.rerun()
                    return

                for line in resp.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    if line.startswith("data: "):
                        chunk = line[6:]
                        if chunk == "[DONE]":
                            break
                        full_answer.append(chunk)
                        placeholder.markdown("".join(full_answer))

        except requests.ConnectionError:
            placeholder.error("无法连接到后端服务，请确认 API 已启动")
        except Exception as exc:
            placeholder.error(f"请求失败: {exc}")

    answer = "".join(full_answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})

    # 新会话时自动获取 session_id
    if not st.session_state.current_session_id:
        try:
            r = _api_get("/api/sessions")
            if r.status_code == 200:
                sessions = r.json()
                if sessions:
                    st.session_state.current_session_id = sessions[0]["id"]
        except Exception:
            pass


def _logout():
    for k in ("token", "user_id", "username", "current_session_id", "sessions"):
        st.session_state[k] = None
    st.session_state.messages = []


# ═══════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════

def main():
    init_state()

    if not st.session_state.token:
        render_login_page()
    else:
        render_main_page()


if __name__ == "__main__":
    main()