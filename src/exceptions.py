# -*- coding: utf-8 -*-
"""Custom exception types used by the PDF processing workflow."""


class APIException(Exception):
    """Raised when the LLM API cannot be reached."""

    def __init__(self, message="无法获取API"):
        self.message = message
        super().__init__(self.message)


class CopyException(Exception):
    """Raised when a file copy operation fails."""

    def __init__(self, message="复制文件时发生错误"):
        self.message = message
        super().__init__(self.message)


class MoveException(Exception):
    """Raised when a file move operation fails."""

    def __init__(self, message="移动文件时发生错误"):
        self.message = message
        super().__init__(self.message)
