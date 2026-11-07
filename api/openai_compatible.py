"""OpenAI-compatible audit client.

Reads the system prompt from ../prompt/system_prompt.txt and forwards
stdin as the user message. API key is read from OPENAI_API_KEY env var.

Usage:
    set OPENAI_API_KEY=sk-xxxx
    echo code | python openai_compatible.py
"""
import os
import sys

try:
    from openai import OpenAI
except ImportError:
    print("please run: pip install openai", file=sys.stderr)
    sys.exit(1)

SYSTEM_PROMPT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "prompt", "system_prompt.txt"
)


def load_system_prompt() -> str:
    with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def main() -> None:
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.environ.get("AUDIT_MODEL", "gpt-4o")

    if not api_key:
        print("please set OPENAI_API_KEY", file=sys.stderr)
        sys.exit(1)

    user_input = sys.stdin.read()
    if not user_input.strip():
        print("usage: echo code | python openai_compatible.py", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key, base_url=base_url)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": load_system_prompt()},
            {"role": "user", "content": user_input},
        ],
        temperature=0.1,
    )
    print(resp.choices[0].message.content)


if __name__ == "__main__":
    main()
