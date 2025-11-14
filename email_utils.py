import os
import json
import smtplib
from typing import Dict, Any, List, Optional
from email.mime.text import MIMEText


def save_summary_json(json_text: str, path: str = "data/daily_summary.json") -> str:
	"""Save the summary JSON string to `path`. Creates parent dir if needed."""
	os.makedirs(os.path.dirname(path), exist_ok=True)
	with open(path, "w", encoding="utf-8") as f:
		f.write(json_text)
	return path


def parse_summary_json(json_text: str) -> Dict[str, Any]:
	"""Parse the JSON summary returned by the LLM into a Python dict.

	Raises `json.JSONDecodeError` if invalid.
	"""
	return json.loads(json_text)


def send_email_smtp(subject: str, body: str, to_email: str) -> None:
	"""Send a single email using SMTP credentials from environment variables.

	Required env vars: `SENDER_EMAIL`, `SENDER_PASSWORD`.
	Optional: `SMTP_HOST` (default smtp.gmail.com), `SMTP_PORT` (default 587).
	"""
	sender = os.getenv("SENDER_EMAIL")
	password = os.getenv("SENDER_PASSWORD")
	smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
	smtp_port = int(os.getenv("SMTP_PORT", "587"))

	if not sender or not password:
		raise ValueError("SMTP credentials not set. Please set SENDER_EMAIL and SENDER_PASSWORD.")

	msg = MIMEText(body, "plain")
	msg["Subject"] = subject
	msg["From"] = sender
	msg["To"] = to_email

	with smtplib.SMTP(smtp_host, smtp_port) as server:
		server.starttls()
		server.login(sender, password)
		server.send_message(msg)


def send_emails(summary: Dict[str, Any], recipient_map: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
	"""Send emails based on the parsed summary dict.

	`summary` is expected to have a top-level `emails` list where each item
	contains `employee_id`, optionally `employee_email`, `email_subject` and `email_body`.

	`recipient_map` is an optional mapping of `employee_id` -> email address
	to use when the summary does not include an email address.

	Returns a list of result objects for each attempted email send.
	"""
	results: List[Dict[str, Any]] = []

	for item in summary.get("emails", []):
		emp_id = str(item.get("employee_id", ""))
		to_email = item.get("employee_email") or (recipient_map.get(emp_id) if recipient_map else None)

		if not to_email:
			results.append({"employee_id": emp_id, "status": "skipped", "reason": "no_email"})
			continue

		subject = item.get("email_subject", "Your daily productivity summary")
		body = item.get("email_body", "")

		try:
			send_email_smtp(subject, body, to_email)
			results.append({"employee_id": emp_id, "status": "sent", "to": to_email})
		except Exception as e:
			results.append({"employee_id": emp_id, "status": "error", "error": str(e)})

	return results


__all__ = [
	"save_summary_json",
	"parse_summary_json",
	"send_email_smtp",
	"send_emails",
]
