# -*- coding: utf-8 -*-
"""Run the PDF renaming workflow."""

import argparse
import os

from normalizer import rename_pdf_files


DEFAULT_OUTPUT_DIRNAME = "修复输出"


def main():
    args = _parse_args()

    input_dir = args.input
    output_dir = args.output or _build_default_output_dir(input_dir)

    # Normalize PDF filenames
    rename_pdf_files(input_dir, output_dir)


def _parse_args():
    parser = argparse.ArgumentParser(description="PDF 标题修复工具")
    parser.add_argument(
        "-i",
        "--input",
        dest="input",
        required=True,
        help="输入PDF文件夹路径",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        help="输出文件夹路径（可选，默认在输入目录下创建“修复输出”）",
    )
    return parser.parse_args()


def _build_default_output_dir(input_dir):
    return os.path.join(input_dir, DEFAULT_OUTPUT_DIRNAME)


if __name__ == "__main__":
    main()
