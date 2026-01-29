# -*- coding: utf-8 -*-
"""Use a DeepSeek-compatible LLM to expand incomplete PDF titles."""

import json
import logging
import os
import re

from openai import OpenAI

from config import OPENAI_API_KEY_ENV, OPENAI_BASE_URL, OPENAI_MODEL, TITLE_PATTERN
from exceptions import APIException

client = OpenAI(
    api_key=os.getenv(OPENAI_API_KEY_ENV),
    base_url=OPENAI_BASE_URL,
)


def split_title(title):
    """Split the filename title into four segments."""
    match = re.match(TITLE_PATTERN, title)
    if match:
        part1 = match.group(1)
        part2 = match.group(2)
        part3 = match.group(3)
        part4 = match.group(4)
        return part1, part2, part3, part4

    return title, "", "", ""


def get_paper_title_with_deepseek(text, original_title):
    """Return the expanded title based on extracted PDF text."""
    part1, part2, part3, _ = split_title(original_title)
    part5 = ""

    system_prompt = _build_system_prompt(part1, part2, part3, part5)
    user_prompt = _build_user_prompt(text)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            response_format={"type": "json_object"},
        )

        renamed_title = json.loads(response.choices[0].message.content)
        return renamed_title.get("title", "")

    except APIException as exc:
        logging.error("Error calling API: %s", str(exc))
        return None


def _build_system_prompt(part1, part2, part3, part5):
    return f"""
        **背景**：  
        你是一名文件命名助手，需要根据输入的论文文本内容，将标题补充完整。

        >>>>>>>>>>>>>>>>>>>>>  
        **规则：**  
        请根据以下规则从文本中补充论文的准确标题：  
        - 【只返回】最终的论文标题，【不得包含】其他任何内容。  
        - 完整标题与输入标题相似，但可能存在【省略】或【不完整】的情况。
        - 【完整提取】标题，若语义相近的标题跨越多行，说明可能存在【副标题】，请一并提取，
        使用【冒号】分隔主副标题。
        - 【不得包含】作者名、机构名、期刊名等内容。 
        - 根据从文本内容中识别到的标题，更新{part2}，更新后的{part2}中不得包含...符号。
        - 将更新后的{part2}内容放入{part5}中。
        - 注意{part3}内容输出的完整，不要忽略该部分的输出整合。
        - 最终输出标题中不得包含空格字符。
        - 输出的论文标题必须为中文。

        **输出标题：**  
        - 以JSON格式输出: ["title": "{part1}{part5}{part3}"]

    """


def _build_user_prompt(text):
    return f"""
    文本内容：
    {text}
    """
