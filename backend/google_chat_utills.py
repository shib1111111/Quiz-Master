# import requests
# import json
# import time
# from datetime import datetime
# import pytz 

# def send_group_msg_google_chat_space(webhook_url: str, message: str, max_retries: int = 3):
#     if not webhook_url or not message:
#         return {"success": False, "error": "Webhook URL and message cannot be empty!", "timestamp": None, "message": message}
    
#     headers = {"Content-Type": "application/json"}
#     payload = {"text": message}
    
#     start_time = time.time()
#     ist = pytz.timezone('Asia/Kolkata')

#     for attempt in range(max_retries):
#         try:
#             response = requests.post(webhook_url, headers=headers, json=payload, timeout=5)
#             timestamp = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S %p")

#             if response.status_code == 200:
#                 execution_time = time.time() - start_time
#                 return {"success": True, "timestamp": timestamp, "message": message, "execution_time": execution_time}
            
#             elif response.status_code == 400:
#                 return {"success": False, "error": "Bad Request - Check your payload format!", "timestamp": timestamp, "message": message}
            
#             elif response.status_code == 403:
#                 return {"success": False, "error": "Forbidden - Ensure webhook URL is correct and has permissions.", "timestamp": timestamp, "message": message}
            
#             elif response.status_code == 404:
#                 return {"success": False, "error": "Webhook URL Not Found - Double-check your Google Chat webhook URL.", "timestamp": timestamp, "message": message}
            
#             elif response.status_code == 429:
#                 time.sleep(5)  # Wait before retrying
#                 continue  # Retry
            
#             else:
#                 return {"success": False, "error": f"Unexpected Error: {response.status_code}, Response: {response.text}", "timestamp": timestamp, "message": message}

#         except requests.exceptions.Timeout:
#             time.sleep(2)  # Retry after a short delay
        
#         except requests.exceptions.ConnectionError:
#             time.sleep(2)  # Retry after a short delay
        
#         except json.JSONDecodeError:
#             return {"success": False, "error": "Invalid JSON response from server.", "timestamp": timestamp, "message": message}
        
#         except Exception as e:
#             return {"success": False, "error": str(e), "timestamp": timestamp, "message": message}

#     return {"success": False, "error": "Failed to send notification after multiple attempts.", "timestamp": datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S %p"), "message": message}

# # Example Usage
# webhook_url = "https://chat.googleapis.com/v1/spaces/dummy"
# message = "🚀 Notification: Task completed successfully!"
# send_group_msg_google_chat_space(webhook_url, message)

# import os
# import json
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError

# SCOPES = [
#     "https://www.googleapis.com/auth/chat.messages",
#     "https://www.googleapis.com/auth/chat.spaces",
#     "https://www.googleapis.com/auth/chat.spaces.readonly"
# ]

# def authenticate(credentials_file):
#     creds = None
#     token_path = "token.json"

#     if os.path.exists(token_path):
#         creds = Credentials.from_authorized_user_file(token_path, SCOPES)

#     if not creds or not creds.valid:
#         try:
#             if creds and creds.expired and creds.refresh_token:
#                 creds.refresh(Request())
#             else:
#                 flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
#                 creds = flow.run_local_server(port=0)

#             with open(token_path, "w") as token:
#                 token.write(creds.to_json())

#         except Exception as e:
#             print(f"Authentication failed: {e}")
#             return None

#     return creds

# def get_dm_space_id(service, user_email):
#     """Fetch the DM space ID for a specific user."""
#     try:
#         response = service.spaces().list().execute()
#         spaces = response.get("spaces", [])
        
#         for space in spaces:
#             # Check if this space is a direct message (DM) with the user
#             if space.get("type") == "DM" and user_email in space.get("name", ""):
#                 return space.get("name")  # This is the correct `space_id`
        
#         print(f"No DM space found for: {user_email}")
#         return None

#     except HttpError as e:
#         print(f"Error retrieving spaces: {e}")
#         return None

# def send_direct_message(credentials_file, user_email, message_text):
#     creds = authenticate(credentials_file)
#     if not creds:
#         print("Authentication failed. Check credentials.")
#         return None

#     try:
#         service = build("chat", "v1", credentials=creds)

#         # Retrieve DM space ID dynamically
#         dm_space_id = get_dm_space_id(service, user_email)
#         if not dm_space_id:
#             print("Failed to get DM space ID. Ensure you have an existing conversation with the user.")
#             return None

#         message = {"text": message_text}

#         try:
#             result = service.spaces().messages().create(parent=dm_space_id, body=message).execute()
#             print(f"Message sent successfully: {result}")
#             return result

#         except HttpError as e:
#             print(f"API Error: {e}")
#             return None

#     except Exception as e:
#         print(f"Unexpected error: {e}")
#         return None

# # -------------------- RUN SCRIPT --------------------

# credentials_file = "google_chat_api.json"
# user_email = "shibkumar1002@gmail.com"  # The recipient's email
# message_text = "Hello from Python!"

# send_direct_message(credentials_file, user_email, message_text)
