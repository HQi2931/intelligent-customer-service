import hashlib
import os

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

try:
    from utils.logger_handler import logger
except ModuleNotFoundError:
    from logger_handler import logger


def get_file_md5_hex(filepath: str):
    """Return the hex MD5 digest for a file."""
    if not os.path.exists(filepath):
        logger.error(f"[md5] File does not exist: {filepath}")
        return

    if not os.path.isfile(filepath):
        logger.error(f"[md5] Path is not a file: {filepath}")
        return

    md5_obj = hashlib.md5()
    chunk_size = 4096

    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)
        return md5_obj.hexdigest()
    except OSError as e:
        logger.error(f"Failed to calculate MD5 for {filepath}: {e}")
        return None


def listdir_with_allowed_type(path: str, allowed_types: tuple[str]):
    """Return files in a directory that match the allowed suffixes."""
    files = []

    if not os.path.isdir(path):
        logger.error(f"[listdir_with_allowed_type] Path is not a directory: {path}")
        return tuple(files)

    for filename in os.listdir(path):
        if filename.endswith(allowed_types):
            files.append(os.path.join(path, filename))

    return tuple(files)


def pdf_loader(filepath: str, passwd=None) -> list[Document]:
    return PyPDFLoader(filepath, password=passwd).load()


def txt_loader(filepath: str) -> list[Document]:
    return TextLoader(filepath, encoding="utf-8").load()
