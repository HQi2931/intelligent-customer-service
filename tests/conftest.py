"""共享测试 fixtures。"""

import sys
from pathlib import Path

import pytest

# 将 src 目录加入 sys.path，以便测试代码可以导入 src 下的模块
SRC_PATH = Path(__file__).resolve().parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

# 同时加入项目根目录，兼容旧路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def sample_csv_path(tmp_path):
    """生成测试用 CSV 文件。"""
    csv = tmp_path / "test_records.csv"
    csv.write_text(
        '"user_id","feature","efficiency","consumables","comparison","time"\n'
        '"1001","65㎡| 单身 | 木地板","覆盖率:85%","主刷:60天","优于65%","2025-01"\n'
        '"1001","65㎡| 单身 | 木地板","覆盖率:86%","主刷:55天","优于68%","2025-02"\n'
        '"1002","70㎡| 情侣 | 瓷砖","覆盖率:88%","边刷:中度","低于同类10%","2025-01"\n',
        encoding="utf-8",
    )
    return str(csv)


@pytest.fixture
def sample_documents():
    """生成测试用 Document 列表。"""
    from langchain_core.documents import Document
    return [
        Document(
            page_content="扫地机器人适用面积60-120㎡",
            metadata={"source": "data/选购指南.txt"},
        ),
        Document(
            page_content="宠物家庭建议每日清理主刷和边刷",
            metadata={"source": "data/维护保养.txt"},
        ),
    ]
