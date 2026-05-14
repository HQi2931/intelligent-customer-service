"""ExternalDataProvider 单元测试。"""

import pytest

from agent.tools.data_provider import ExternalDataProvider


class TestExternalDataProvider:
    def test_load_and_query(self, sample_csv_path):
        provider = ExternalDataProvider(csv_path=sample_csv_path)
        record = provider.get_user_record("1001", "2025-01")

        assert record is not None
        assert record["特征"] == "65㎡| 单身 | 木地板"
        assert record["效率"] == "覆盖率:85%"
        assert record["耗材"] == "主刷:60天"
        assert record["对比"] == "优于65%"

    def test_nonexistent_user_returns_none(self, sample_csv_path):
        provider = ExternalDataProvider(csv_path=sample_csv_path)
        record = provider.get_user_record("9999", "2025-01")
        assert record is None

    def test_nonexistent_month_returns_none(self, sample_csv_path):
        provider = ExternalDataProvider(csv_path=sample_csv_path)
        record = provider.get_user_record("1001", "2024-12")
        assert record is None

    def test_lazy_loading(self, sample_csv_path):
        provider = ExternalDataProvider(csv_path=sample_csv_path)
        assert not provider.is_loaded
        provider.get_user_record("1001", "2025-01")
        assert provider.is_loaded

    def test_file_not_found(self):
        provider = ExternalDataProvider(csv_path="nonexistent.csv")
        with pytest.raises(FileNotFoundError):
            provider.get_user_record("1001", "2025-01")

    def test_instance_isolation(self, sample_csv_path, tmp_path):
        """验证不同实例的状态隔离。"""
        provider1 = ExternalDataProvider(csv_path=sample_csv_path)
        provider2 = ExternalDataProvider(csv_path=sample_csv_path)

        provider1.get_user_record("1001", "2025-01")
        # provider2 应该尚未加载
        assert not provider2.is_loaded
