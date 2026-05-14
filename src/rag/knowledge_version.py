"""知识库版本管理 — 快照 + 回滚。"""

import json
import os
import shutil
from datetime import datetime

from utils.logger_handler import logger


class KnowledgeVersion:
    """每次 rebuild 自动创建版本快照。"""

    def __init__(self, base_dir: str = "chroma_db/versions"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def snapshot(self, label: str | None = None) -> str:
        version = label or datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = os.path.join(self.base_dir, version)
        os.makedirs(dest, exist_ok=True)

        # 复制 ChromaDB（跳过 versions 子目录）
        if os.path.exists("chroma_db"):
            for item in os.listdir("chroma_db"):
                if item == "versions":
                    continue
                src = os.path.join("chroma_db", item)
                dst = os.path.join(dest, "chroma_db", item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)

        # 复制 BM25
        if os.path.exists("chroma_db/bm25_index.pkl"):
            shutil.copy("chroma_db/bm25_index.pkl", dest)

        # 元信息
        data_files = os.listdir("data") if os.path.isdir("data") else []
        with open(os.path.join(dest, "meta.json"), "w", encoding="utf-8") as f:
            json.dump({
                "version": version,
                "created_at": datetime.now().isoformat(),
                "source_files": [f for f in data_files if not f.startswith(".")],
            }, f, ensure_ascii=False, indent=2)

        logger.info(f"[KnowledgeVersion] 快照已创建: {version}")
        return version

    def list_versions(self) -> list[dict]:
        if not os.path.isdir(self.base_dir):
            return []
        versions = []
        for v in sorted(os.listdir(self.base_dir), reverse=True):
            meta_path = os.path.join(self.base_dir, v, "meta.json")
            if os.path.exists(meta_path):
                with open(meta_path, encoding="utf-8") as f:
                    versions.append(json.load(f))
            else:
                versions.append({"version": v})
        return versions

    def restore(self, version: str) -> bool:
        src = os.path.join(self.base_dir, version, "chroma_db")
        if not os.path.exists(src):
            logger.error(f"[KnowledgeVersion] 版本不存在: {version}")
            return False

        # 覆盖 ChromaDB
        if os.path.exists("chroma_db"):
            for item in os.listdir("chroma_db"):
                if item == "versions":
                    continue
                path = os.path.join("chroma_db", item)
                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    os.remove(path)

        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join("chroma_db", item)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

        logger.info(f"[KnowledgeVersion] 已回滚到: {version}")
        return True