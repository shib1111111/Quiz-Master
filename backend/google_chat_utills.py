import requests
import json
import time
from datetime import datetime
import pytz 
import os
from dotenv import load_dotenv


load_dotenv()
GOOGLE_CHAT_SPACE_WEBHOOK_URL = os.getenv("GOOGLE_CHAT_SPACE_WEBHOOK")

def send_group_msg_google_chat_space(message: str, webhook_url: str = GOOGLE_CHAT_SPACE_WEBHOOK_URL, max_retries: int = 3):
    print(f"Webhook URL: {webhook_url}")
    if not webhook_url or not message:
        return {"success": False, "error": "Webhook URL and message cannot be empty!", "timestamp": None, "message": message}
    headers = {"Content-Type": "application/json"}
    payload = {"text": message}
    
    start_time = time.time()
    ist = pytz.timezone('Asia/Kolkata')

    for attempt in range(max_retries):
        try:
            response = requests.post(webhook_url, headers=headers, json=payload, timeout=5)
            timestamp = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S %p")

            if response.status_code == 200:
                execution_time = time.time() - start_time
                return {"success": True, "timestamp": timestamp, "message": message, "execution_time": execution_time}
            
            elif response.status_code == 400:
                return {"success": False, "error": "Bad Request - Check your payload format!", "timestamp": timestamp, "message": message}
            
            elif response.status_code == 403:
                return {"success": False, "error": "Forbidden - Ensure webhook URL is correct and has permissions.", "timestamp": timestamp, "message": message}
            
            elif response.status_code == 404:
                return {"success": False, "error": "Webhook URL Not Found - Double-check your Google Chat webhook URL.", "timestamp": timestamp, "message": message}
            
            elif response.status_code == 429:
                time.sleep(5)  
                continue  
            
            else:
                return {"success": False, "error": f"Unexpected Error: {response.status_code}, Response: {response.text}", "timestamp": timestamp, "message": message}

        except requests.exceptions.Timeout:
            time.sleep(2)  
        
        except requests.exceptions.ConnectionError:
            time.sleep(2)  
        
        except json.JSONDecodeError:
            return {"success": False, "error": "Invalid JSON response from server.", "timestamp": timestamp, "message": message}
        
        except Exception as e:
            return {"success": False, "error": str(e), "timestamp": timestamp, "message": message}

    return {"success": False, "error": "Failed to send notification after multiple attempts.", "timestamp": datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S %p"), "message": message}



if __name__ == "__main__":
    send_group_msg_google_chat_space(message="Test message from Python script")