import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz
import sys
import time
from concurrent.futures import ThreadPoolExecutor

# Define IST timezone
IST = pytz.timezone('Asia/Kolkata')

# API URLs
LOGIN_URL = "https://fwprepaid.myfastway.in/api/index.php/v1/user/login?vr=web1.1"
SUSPEND_URL = "https://fwprepaid.myfastway.in/api/index.php/v1/account/{accNo}/suspend"
RESUME_URL = "https://fwprepaid.myfastway.in/api/index.php/v1/account/{accNo}/resume"

# User credentials (you can load from env or secure config too)
USERNAME = "IN-0000016345"
PASSWORD = "AshishDudeja@123"

# Request bodies
SUSPEND_BODY = {"remark": "Non Paid", "refund_type": 2}
RESUME_BODY = {"remark": "Payment Done"}

# Function to login and fetch access token
def get_access_token(username, password):
    payload = {
        "LoginForm": {
            "username": username,
            "password": password
        }
    }
    try:
        response = requests.post(LOGIN_URL, json=payload, headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        response_data = response.json()

        if response.status_code == 200 and response_data.get("status") == 200:
            token = response_data["data"]["access_token"]
            print("Login successful. Access token acquired.")
            return token
        else:
            print("Login failed:", response_data.get("message", "Unknown error"))
            sys.exit(1)
    except Exception as e:
        print(f"Login error: {e}")
        sys.exit(1)

# Fetch token and set dynamic headers
access_token = get_access_token(USERNAME, PASSWORD)
HEADERS = {
    "Authorization": f"Bearer {access_token}"
}
print("Authorization:", HEADERS["Authorization"])

# Load the Excel file
df = pd.read_excel('.github/workflows/test.xlsx')

# Get current time in IST
current_time = datetime.now(IST)

# Define the time window for deactivation (11:58 PM to 12:00 AM)
start_deactivation_time = current_time.replace(hour=23, minute=57, second=0, microsecond=0)
end_deactivation_time = current_time.replace(hour=23, minute=59, second=59, microsecond=999999)

# Wait until 11:58 PM if needed
if current_time < start_deactivation_time:
    remaining_time = (start_deactivation_time - current_time).total_seconds()
    print(f"Waiting {int(remaining_time // 60)} min and {int(remaining_time % 60)} sec until 11:58 PM.")
    time.sleep(remaining_time)

if datetime.now(IST) > end_deactivation_time:
    print("It's past 12:00 AM, stopping execution.")
    sys.exit(0)
else:
    print("Proceeding with deactivation...")

# Function to suspend an account
def suspend_account(acc_no):
    url = SUSPEND_URL.format(accNo=acc_no)
    try:
        response = requests.post(url, json=SUSPEND_BODY, headers=HEADERS)
        if response.status_code == 201:
            print(f"Suspended account {acc_no}")
            return acc_no
        else:
            print(f"Failed to suspend {acc_no}: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error suspending {acc_no}: {e}")
    return None

# Suspend accounts concurrently
suspended_accounts = []
with ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(suspend_account, df['accNo'])
    suspended_accounts = [acc for acc in results if acc is not None]

# Wait for 2 minutes
print("Waiting for 2 minutes before resuming accounts...")
time.sleep(120)

# Resume function
def resume_account(acc_no):
    url = RESUME_URL.format(accNo=acc_no)
    try:
        response = requests.post(url, json=RESUME_BODY, headers=HEADERS)
        if response.status_code == 201:
            print(f"Resumed account {acc_no}")
        else:
            print(f"Failed to resume {acc_no}: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error resuming {acc_no}: {e}")

# Resume accounts concurrently
with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(resume_account, suspended_accounts)
