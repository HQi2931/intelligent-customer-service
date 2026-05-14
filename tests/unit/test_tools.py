"""工具函数单元测试。"""


from agent.tools.rag_tools import rag_summarize
from agent.tools.user_tools import (
    get_current_month,
    get_user_id,
    get_user_location,
    get_weather,
)


class TestWeatherTool:
    def test_returns_string_with_city(self):
        result = get_weather.invoke({"city": "北京"})
        assert isinstance(result, str)
        assert "北京" in result

    def test_different_cities_return_strings(self):
        for city in ["上海", "广州", "深圳"]:
            assert isinstance(get_weather.invoke({"city": city}), str)


class TestUserLocationTool:
    def test_returns_valid_city(self):
        result = get_user_location.invoke({})
        assert isinstance(result, str)
        assert result in {"北京", "上海", "广州", "深圳"}


class TestUserIDTool:
    def test_returns_valid_id(self):
        uid = get_user_id.invoke({})
        assert isinstance(uid, str)
        assert uid in {
            "1001", "1002", "1003", "1004", "1005",
            "1006", "1007", "1008", "1009", "1010",
        }

    def test_multiple_calls_return_strings(self):
        ids = {get_user_id.invoke({}) for _ in range(10)}
        assert all(isinstance(i, str) for i in ids)


class TestCurrentMonthTool:
    def test_returns_valid_format(self):
        month = get_current_month.invoke({})
        assert isinstance(month, str)
        assert len(month) == 7  # "YYYY-MM"
        assert month[4] == "-"

    def test_month_in_valid_range(self):
        month = get_current_month.invoke({})
        year, m = month.split("-")
        assert 2025 <= int(year) <= 2025
        assert 1 <= int(m) <= 12


class TestRagSummarizeTool:
    def test_is_tool_callable(self):
        """验证 rag_summarize 是 LangChain tool 对象。"""
        assert hasattr(rag_summarize, "name")
        assert rag_summarize.name == "rag_summarize"

    def test_has_description(self):
        assert hasattr(rag_summarize, "description")
        assert len(rag_summarize.description) > 0
