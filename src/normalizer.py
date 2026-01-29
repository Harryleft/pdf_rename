# -*- coding: utf-8 -*-
"""Normalize PDF filenames using regex heuristics and LLM expansion."""

import logging
import os
import re
import shutil

import fitz
from langchain_community.document_loaders import PDFPlumberLoader

from exceptions import CopyException, MoveException
from title_fixer import get_paper_title_with_deepseek
from loader import get_paper_title_with_regx

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.INFO
SUPPORTED_EXTENSION = ".pdf"
CONTENT_PREVIEW_LENGTH = 250
INVALID_FILENAME_PATTERN = r'[<>:"/\\|?*]'
VALID_PREFIX_PATTERN = r"^\d+_.*\.pdf$"

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)


def load_pdf_content(file_path):
    """Load text content from a PDF and return a short preview."""
    document_loader_mapping = {
        ".pdf": (PDFPlumberLoader, {}),
    }

    ext = os.path.splitext(file_path)[1]
    loader_tuple = document_loader_mapping.get(ext)

    if loader_tuple:
        loader_class, loader_args = loader_tuple
        try:
            loader = loader_class(file_path, **loader_args)
            documents = loader.load()
            content = "\n".join([doc.page_content for doc in documents])
            return content[:CONTENT_PREVIEW_LENGTH]
        except Exception as exc:
            logging.warning("pdfplumber 解析失败，尝试备用方案: %s", str(exc))
            return _load_pdf_content_with_fitz(file_path)

    print(file_path + f"，不支持的文档类型: '{ext}'")
    return ""


def sanitize_filename(filename):
    """Remove illegal characters from filenames."""
    return re.sub(INVALID_FILENAME_PATTERN, "", filename)


def create_output_directory(output_path):
    """Ensure the output directory exists."""
    if not os.path.exists(output_path):
        os.makedirs(output_path)


def is_valid_pdf(filename):
    """Return True if the filename has a PDF extension."""
    return filename.lower().endswith(SUPPORTED_EXTENSION)


def is_filename_valid(filename):
    """Return True when the filename already has a numeric prefix."""
    return re.match(VALID_PREFIX_PATTERN, filename)


def process_filename(filename, file_path):
    """Return a normalized filename or None when it cannot be processed."""
    try:
        processed_name = get_paper_title_with_regx(filename)
        if processed_name is None:
            pdf_text = load_pdf_content(file_path)
            original_title = os.path.splitext(filename)[0]
            paper_title = get_paper_title_with_deepseek(pdf_text, original_title)
            if paper_title:
                return sanitize_filename(paper_title) + ".pdf"
            logging.warning("无法提取标题 %s", filename)
            return None
        if processed_name == os.path.splitext(filename)[0]:
            logging.info("跳过: %s", filename)
            return None
        return processed_name + ".pdf"
    except Exception as exc:
        logging.error("处理文件名时出错 %s: %s", filename, str(exc))
        return None


def rename_pdf_files(folder_path, output_path):
    """Normalize and move/copy PDF files from folder_path to output_path."""
    create_output_directory(output_path)
    failed_files = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if is_valid_pdf(filename):
            try:
                if is_filename_valid(filename):
                    logging.info("文件名已符合要求，直接移动: %s", filename)
                    new_file_path = os.path.join(output_path, filename)
                    move_file(file_path, new_file_path)
                else:
                    new_filename = process_filename(filename, file_path)
                    if new_filename:
                        new_file_path = os.path.join(output_path, new_filename)
                        copy_file(file_path, new_file_path)
                    else:
                        logging.warning("无法处理文件: %s", filename)
                        failed_files.append(filename)
            except Exception as exc:
                logging.error("处理文件时出错 %s: %s", filename, str(exc))
                failed_files.append(filename)

    _write_failed_list(output_path, failed_files)


def move_file(file_path, new_file_path):
    """Move a file to a new path if it does not already exist."""
    try:
        if not os.path.exists(new_file_path):
            shutil.move(file_path, new_file_path)
            logging.info("成功移动: %s -> %s", file_path, new_file_path)
        else:
            logging.warning("目标文件已存在，跳过移动: %s", new_file_path)
    except MoveException as exc:
        logging.error("移动文件时出错 %s: %s", file_path, str(exc))


def copy_file(file_path, new_file_path):
    """Copy a file to a new path if it does not already exist."""
    try:
        if not os.path.exists(new_file_path):
            if not os.path.exists(os.path.dirname(new_file_path)):
                os.makedirs(os.path.dirname(new_file_path))
            shutil.copy2(file_path, new_file_path)
            logging.info("成功复制: %s -> %s", file_path, new_file_path)
        else:
            logging.warning("目标文件已存在，跳过复制: %s", new_file_path)
    except CopyException as exc:
        logging.error("复制文件时出错 %s: %s", file_path, str(exc))


def _load_pdf_content_with_fitz(file_path):
    try:
        with fitz.open(file_path) as document:
            content = "\n".join(page.get_text() for page in document)
        return content[:CONTENT_PREVIEW_LENGTH]
    except Exception as exc:
        logging.error("备用解析器失败 %s: %s", file_path, str(exc))
        return ""


def _write_failed_list(output_path, failed_files):
    if not failed_files:
        return
    failed_list_path = os.path.join(output_path, "failed_files.txt")
    with open(failed_list_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(failed_files))
