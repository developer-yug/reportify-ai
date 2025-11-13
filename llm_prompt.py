import os
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")

def generate_summary(task_data, workfolio_data):
    """
    Generate a productivity summary using DeepSeek API.
    Handles API errors gracefully and returns clear error messages.
    """

    if not API_KEY:
        raise ValueError("❌ DEEPSEEK_API_KEY not found. Please set it in .env or Streamlit secrets.")

    prompt = f"""
    You are a smart productivity analyst.
    Based on the data below, summarize how much time each employee spent on assigned tasks
    and provide an overall productivity summary.

    === Task Allocation ===
    {task_data}

    === Workfolio Activity Summary ===
    {workfolio_data}

    Provide a concise, insightful report.
    """

    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()  # raises HTTPStatusError for 4xx/5xx
        data = response.json()

        # ✅ Defensive check
        if "choices" not in data:
            raise KeyError(f"API response missing 'choices' key: {data}")

        return data["choices"][0]["message"]["content"].strip()

    except httpx.HTTPStatusError as e:
        # Handles 401, 400, etc.
        error_message = e.response.text
        raise RuntimeError(f"HTTP error {e.response.status_code}: {error_message}")

    except httpx.RequestError as e:
        # Network or timeout issues
        raise RuntimeError(f"Request failed: {e}")

    except KeyError as e:
        # Handles missing 'choices'
        raise RuntimeError(f"Unexpected API response format: {e}")

    except Exception as e:
        # Catch any other issues
        raise RuntimeError(f"Error during summary generation: {e}")
