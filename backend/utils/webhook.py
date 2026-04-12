import requests
import json

def send_google_chat_message(webhook_url, message):
    if not webhook_url:
        return False
    payload = {'text': message}
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
        return response.status_code == 200
    except Exception as e:
        print(f"Webhook sending failed: {e}")
        return False
