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

    # Instruct the model to return a machine-readable JSON payload.
    # The JSON must include per-employee email subjects and bodies and an overall digest.
    prompt = f"""
    You are a productivity analyst that returns output strictly as JSON.
    You will receive two CSV inputs: Task Allocation and Workfolio Activity.

    Requirements for the JSON output:
    - Top-level keys: `emails` (list), `digest` (object).
    - Each item in `emails` must be an object with: `employee_id`, `employee_name` (if available), `email_subject`, `email_body`.
    - `digest` must contain `subject` and `body` for a company-wide summary email.
    - All times should be reported in hours (round to 1 decimal place) and include: total assigned tasks, tasks completed, total estimated time, total active time, and percentage completion.
    - Keep `email_subject` short (<= 80 chars). Make `email_body` friendly, actionable, and include 2-3 bullet highlights and a short suggestion to improve productivity.
    - Return only valid JSON (no extra prose or commentary).

    === Task Allocation CSV ===
    {task_data}

    === Workfolio Activity CSV ===
    {workfolio_data}

    Produce the JSON now.
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
