# -*- coding: utf-8 -*-
"""Load PDF filenames and normalize titles for downstream processing."""

import glob
import os
import re

PDF_GLOB_PATTERN = "*.pdf"
TITLE_VALIDATION_PATTERN = r"^[\u4e00-\u9fa5A-Za-z0-9\s]+$"
AUTHOR_SUFFIX_PATTERN = r"_[^_]+$"
ELLIPSIS_MARKER = "..."


def get_paper_title_with_regx(filename):
    """Return a cleaned title or None when LLM expansion is needed."""
    name_without_ext = os.path.splitext(filename)[0]
    if re.match(TITLE_VALIDATION_PATTERN, name_without_ext):
        return name_without_ext

    if ELLIPSIS_MARKER in name_without_ext:
        return None

    return re.sub(AUTHOR_SUFFIX_PATTERN, "", name_without_ext)


def load_pdf_names(directory):
    """Return a list of PDF filenames (without extensions) in a directory."""
    pdf_files = _get_pdf_files(directory)
    pdf_names = [
        os.path.splitext(os.path.basename(file_path))[0] for file_path in pdf_files
    ]
    return pdf_names


def _get_pdf_files(directory):
    pdf_files = glob.glob(os.path.join(directory, PDF_GLOB_PATTERN))
    pdf_files.sort()
    return pdf_files
