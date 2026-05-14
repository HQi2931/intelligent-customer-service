import argparse
import json
import os
import sys
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from model.factory import embed_model
from utils.config_handler import chroma_conf, rag_conf
from utils.file_handler import (
    get_file_md5_hex,
    listdir_with_allowed_type,
    pdf_loader,
    txt_loader,
)
from utils.logger_handler import logger
from utils.path_tool import get_abs_path


class VectorStoreService:
    def __init__(self):
        self.persist_directory = get_abs_path(chroma_conf["persist_directory"])
        self.md5_store_path = get_abs_path(chroma_conf["md5_hex_store"])
        self.index_meta_path = os.path.join(self.persist_directory, "index_meta.json")
        self.embedding_model_name = rag_conf["embedding_model_name"]
        self.vector_store = Chroma(
            collection_name=chroma_conf["collection_name"],
            embedding_function=embed_model,
            persist_directory=self.persist_directory,
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf["chunk_size"],
            chunk_overlap=chroma_conf["chunk_overlap"],
            separators=chroma_conf["separators"],
            length_function=len,
        )

    def get_retriever(self):
        return self.vector_store.as_retriever(
            search_kwargs={"k": chroma_conf.get("k", 3)}
        )

    def _load_index_meta(self) -> dict:
        if not os.path.exists(self.index_meta_path):
            return {}
        with open(self.index_meta_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_index_meta(self):
        os.makedirs(self.persist_directory, exist_ok=True)
        with open(self.index_meta_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "collection_name": chroma_conf["collection_name"],
                    "embedding_model_name": self.embedding_model_name,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

    def _clear_md5_store(self):
        if os.path.exists(self.md5_store_path):
            os.remove(self.md5_store_path)

    def _recreate_vector_store(self):
        self.vector_store = Chroma(
            collection_name=chroma_conf["collection_name"],
            embedding_function=embed_model,
            persist_directory=self.persist_directory,
        )

    def rebuild_index(self):
        logger.warning(
            "Rebuilding vector index for embedding model `%s`.",
            self.embedding_model_name,
        )
        self.vector_store.delete_collection()
        self._clear_md5_store()
        self._recreate_vector_store()
        self._save_index_meta()

    def check_index_compatibility(self):
        collection_count = self.vector_store._collection.count()
        if collection_count == 0:
            self._save_index_meta()
            return

        meta = self._load_index_meta()
        stored_model_name = meta.get("embedding_model_name")
        if not stored_model_name:
            raise RuntimeError(
                "Existing vector index has "
                f"{collection_count} documents but no embedding metadata. "
                "The vectors may have been built by a different embedding model. "
                "Rebuild the index with `python rag/vector_store.py --rebuild`."
            )

        if stored_model_name != self.embedding_model_name:
            raise RuntimeError(
                "Embedding model mismatch: index was built with "
                f"`{stored_model_name}`, but current config uses "
                f"`{self.embedding_model_name}`. Rebuild the index with "
                "`python rag/vector_store.py --rebuild`."
            )

    def load_documents(self, rebuild: bool = False):
        if rebuild:
            self.rebuild_index()

        self.check_index_compatibility()

        data_path = get_abs_path(chroma_conf["data_path"])
        allowed_types = tuple(
            f".{suffix.lstrip('.')}"
            for suffix in chroma_conf.get("allow_knowledge_file_type", [])
        )

        def check_md5_hex(md5_for_check: str) -> bool:
            if not os.path.exists(self.md5_store_path):
                open(self.md5_store_path, "w", encoding="utf-8").close()
                return False

            with open(self.md5_store_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip() == md5_for_check:
                        return True
            return False

        def save_md5_hex(md5_to_save: str):
            with open(self.md5_store_path, "a", encoding="utf-8") as f:
                f.write(md5_to_save + "\n")

        def get_file_documents(read_path: str) -> list[Document]:
            if read_path.endswith(".txt"):
                return txt_loader(read_path)
            if read_path.endswith(".pdf"):
                return pdf_loader(read_path)
            raise ValueError(f"Unsupported file type: {read_path}")

        allowed_file_paths = listdir_with_allowed_type(data_path, allowed_types)

        for path in allowed_file_paths:
            md5_hex = get_file_md5_hex(path)
            if not md5_hex:
                continue

            if check_md5_hex(md5_hex):
                logger.info(f"File already processed, skipping: {path}")
                continue

            try:
                documents = get_file_documents(path)
                if not documents:
                    logger.warning(f"No documents found in file: {path}")
                    continue

                for document in documents:
                    document.metadata = dict(document.metadata or {})
                    document.metadata["source"] = path

                split_documents = self.splitter.split_documents(documents)
                self.vector_store.delete(where={"source": path})
                self.vector_store.add_documents(split_documents)
                save_md5_hex(md5_hex)
                logger.info(f"Successfully processed and stored file: {path}")
            except Exception as e:
                logger.error(f"Error processing file {path}: {e}")

        self._save_index_meta()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Clear the existing Chroma collection and rebuild all document vectors.",
    )
    args = parser.parse_args()

    vs = VectorStoreService()
    vs.load_documents(rebuild=args.rebuild)
    retriever = vs.get_retriever()
    result = retriever.invoke("迷路")
    for item in result:
        print(item.page_content)
        print("===" * 20)
