"""外部数据提供者 - 实例化封装，消除模块级可变全局状态。"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.config_handler import agent_conf
from utils.logger_handler import logger
from utils.path_tool import get_abs_path


class ExternalDataProvider:
    """外部 CSV 数据加载与查询，实例级状态隔离。"""

    def __init__(self, csv_path: str | None = None):
        self._csv_path = csv_path or get_abs_path(agent_conf["external_data_path"])
        self._cache: dict[str, dict[str, dict]] = {}
        self._loaded = False

    def get_user_record(self, user_id: str, month: str) -> dict | None:
        """获取指定用户在指定月份的使用记录。"""
        if not self._loaded:
            self._load()
        try:
            return self._cache[user_id][month]
        except KeyError:
            logger.warning(
                f"[ExternalDataProvider] 未检索到用户:{user_id}在{month}的使用情况"
            )
            return None

    def _load(self):
        if not os.path.exists(self._csv_path):
            raise FileNotFoundError(f"外部数据文件 {self._csv_path} 不存在")

        with open(self._csv_path, encoding="utf-8") as f:
            for line in f.readlines()[1:]:
                arr: list[str] = line.strip().split(",")

                user_id: str = arr[0].replace('"', "")
                feature: str = arr[1].replace('"', "")
                efficiency: str = arr[2].replace('"', "")
                consumables: str = arr[3].replace('"', "")
                comparison: str = arr[4].replace('"', "")
                time: str = arr[5].replace('"', "")

                self._cache.setdefault(user_id, {})
                self._cache[user_id][time] = {
                    "特征": feature,
                    "效率": efficiency,
                    "耗材": consumables,
                    "对比": comparison,
                }

        self._loaded = True
        logger.info(f"[ExternalDataProvider] 加载外部数据完成，共 {len(self._cache)} 个用户")

    @property
    def is_loaded(self) -> bool:
        return self._loaded


# 模块级惰性单例
_data_provider: ExternalDataProvider | None = None


def get_data_provider() -> ExternalDataProvider:
    """获取 ExternalDataProvider 单例。"""
    global _data_provider
    if _data_provider is None:
        _data_provider = ExternalDataProvider()
    return _data_provider
