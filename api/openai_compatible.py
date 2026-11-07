import os
from openai import OpenAI

# 从环境变量读取 API Key，确保无硬编码
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("未检测到 OPENAI_API_KEY 环境变量，请先配置。")

# 读取系统提示词
try:
    with open("prompt/system_prompt.txt", "r", encoding="utf-8") as f:
        system_prompt = f.read()
except FileNotFoundError:
    raise FileNotFoundError("找不到 prompt/system_prompt.txt 文件，请确保路径正确。")

# 初始化客户端（兼容 OpenAI / DeepSeek / 通义千问等兼容接口）
client = OpenAI(
    api_key=api_key,
    base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
)

def run_audit(target_content: str):
    """
    运行审计工作流
    :param target_content: 待分析的代码或抓包日志
    """
    print(">>> 正在唤醒审计专家...")
    response = client.chat.completions.create(
        model=os.environ.get("MODEL_NAME", "gpt-4o"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请对以下目标执行三阶漏斗审计，并生成标准化报告：\n\n{target_content}"}
        ],
        temperature=0.1 # 保持严谨
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    # 测试用例
    test_code = "console.log('Hello, this is a test sample.');"
    result = run_audit(test_code)
    print("\n=== 审计报告 ===\n")
    print(result)
