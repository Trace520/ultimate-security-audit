"""OpenAI-compatible client for running the audit skill against any
OpenAI-shaped endpoint (OpenAI, DeepSeek, Qwen, Kimi, vLLM, ...)."""

import os
from pathlib import Path

from openai import OpenAI

# --- config from environment, no hardcoded secrets -------------------------
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY 环境变量未设置。")

base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
model = os.environ.get("MODEL_NAME", "gpt-4o")

# --- locate system prompt next to this file, cross-platform -----------------
PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompt" / "system_prompt.txt"
try:
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
except FileNotFoundError as exc:
    raise FileNotFoundError(f"找不到系统提示词文件：{PROMPT_PATH}") from exc

# --- client ------------------------------------------------------------------
client = OpenAI(api_key=api_key, base_url=base_url)


def run_audit(target_content: str) -> str:
    """Run the three-stage funnel audit against *target_content*."""
    print(">>> 正在唤醒审计专家...")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    "请对以下目标执行三阶漏斗审计，并生成标准化报告：\n\n"
                    f"{target_content}"
                ),
            },
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    sample = "console.log('Hello, this is a test sample.');"
    print("\n=== 审计报告 ===\n")
    print(run_audit(sample))
