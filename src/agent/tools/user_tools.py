"""用户与天气相关工具（当前为 Mock 实现）。"""

import random

from langchain_core.tools import tool

USER_IDS = ["1001", "1002", "1003", "1004", "1005",
            "1006", "1007", "1008", "1009", "1010"]

MONTHS = ["2025-01", "2025-02", "2025-03", "2025-04",
          "2025-05", "2025-06", "2025-07", "2025-08",
          "2025-09", "2025-10", "2025-11", "2025-12"]


@tool(description="获取指定城市的天气信息,以字符串形式返回")
def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息。

    参数:
    city (str): 城市名称。

    返回:
    str: 包含天气信息的字符串。
    """
    # TODO: 对接真实天气 API
    return f"{city}的天气是晴朗，温度25摄氏度，湿度60%。"


@tool(description="获取用户的位置信息,以字符串形式返回")
def get_user_location() -> str:
    """
    获取用户的位置信息。

    返回:
    str: 包含位置信息的字符串。
    """
    # TODO: 对接真实定位服务
    return random.choice(["北京", "上海", "广州", "深圳"])


@tool(description="获取用户的id,以字符串形式返回")
def get_user_id() -> str:
    """
    获取用户的ID信息。

    返回:
    str: 包含用户ID的字符串。
    """
    # TODO: 对接真实用户系统
    return random.choice(USER_IDS)


@tool(description="获取当前月份,以字符串形式返回")
def get_current_month() -> str:
    """
    获取当前月份信息。

    返回:
    str: 包含当前月份的字符串。
    """
    # TODO: 使用真实日期
    return random.choice(MONTHS)
