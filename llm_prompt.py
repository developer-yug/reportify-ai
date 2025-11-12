import os
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")

def generate_summary(task_data, workfolio_data):
    prompt = f"""
    You are a smart agent summarizing task updates.

    Task Allocation:
    {task_data}

    Workfolio Activity Summary:
    {workfolio_data}

    Derive how much time each employee spent on assigned tasks
    and provide an overall productivity summary.
    """

    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
    }

    response = httpx.post(url, headers=headers, json=payload, timeout=60)
    return response.json()["choices"][0]["message"]["content"]
