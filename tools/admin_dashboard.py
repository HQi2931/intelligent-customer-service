"""运维看板 — 指标大盘 + 熔断状态 + 知识库版本。

启动: streamlit run admin.py --server.port 8502
"""

import requests
import streamlit as st

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="运维看板", page_icon="📊", layout="wide")
st.title("📊 智能客服助手 — 运维看板")


def fetch_json(path: str) -> dict:
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=5)
        return r.json() if r.status_code == 200 else {}
    except Exception:
        return {}


# ── 指标大盘 ──
st.header("📈 实时指标")
metrics = fetch_json("/api/metrics")

col1, col2, col3, col4 = st.columns(4)
with col1:
    chats = metrics.get("chat_requests", {})
    st.metric("对话请求", chats.get("total", 0))
with col2:
    tools = metrics.get("tool_calls", {})
    st.metric("工具调用", tools.get("total", 0),
              delta=f"{tools.get('success_rate', 0)}% 成功率")
with col3:
    llm = metrics.get("llm_calls", {})
    st.metric("Token 输入", llm.get("tokens_in", 0))
with col4:
    st.metric("运行时间", f"{metrics.get('uptime_seconds', 0):.0f}s")

# ── 熔断器状态 ──
st.header("🔌 熔断器状态")
alerts_data = fetch_json("/api/alerts")
circuits = alerts_data.get("circuit_status", {})

if circuits:
    for name, status in circuits.items():
        icon = "🔴" if status["open"] else "🟢"
        st.write(
            f"{icon} **{name}**: "
            f"failures={status['failures']}, open={status['open']}"
        )
else:
    st.info("暂无熔断器数据")

# ── 活跃告警 ──
st.header("🚨 活跃告警")
alerts = alerts_data.get("alerts", [])
if alerts:
    for a in alerts:
        level_color = "🔴" if a["level"] == "critical" else "🟡"
        st.warning(f"{level_color} [{a['source']}] {a['message']}")
else:
    st.success("无活跃告警")

# ── 知识库版本 ──
st.header("📚 知识库版本")
health = fetch_json("/api/health")
st.write(f"Agent: {'🟢' if health.get('agent_ready') else '🔴'} "
         f"向量库: {'🟢' if health.get('vector_store_ready') else '🔴'}")

# ── 缓存状态 ──
cache_size = alerts_data.get("cache_size", 0)
st.metric("缓存条目", cache_size)

# 自动刷新
st.caption("数据每 10 秒自动刷新")
st.button("🔄 手动刷新")
try:
    st.rerun()
except Exception:
    pass