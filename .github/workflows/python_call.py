import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz
import sys
import time
from concurrent.futures import ThreadPoolExecutor

# Define IST timezone
IST = pytz.timezone('Asia/Kolkata')

# Define the base URLs and headers
SUSPEND_URL = "https://fwprepaid.myfastway.in/api/index.php/v1/account/{accNo}/suspend"
RESUME_URL = "https://fwprepaid.myfastway.in/api/index.php/v1/account/{accNo}/resume"
HEADERS = {
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NDY5MDA2MjIsImlzcyI6Imh0dHA6XC9cL2Z3cHJlcGFpZC5teWZhc3R3YXkuaW4iLCJhdWQiOiJodHRwOlwvXC9md3ByZXBhaWQubXlmYXN0d2F5LmluIiwibmJmIjoxNzQ2OTAwNjIyLCJleHAiOjE3NTcyNjg2MjIsImxhc3RfbG9naW5fYXQiOiIyMDI1LTA1LTEwIDIzOjQwOjIyIiwiZXh0cmFfZGF0YSI6W10sInJlc3RyaWN0X2lwIjpbXSwiaXNfYWdncmVtZW50X3ZvaWQiOjAsImFsbG93ZWRfYXBpcyI6bnVsbCwiZGF0YSI6eyJ1c2VybmFtZSI6ImluLTAwMDAwMTYzNDUiLCJyb2xlTGFiZWwiOiJBZG1pbmlzdHJhdG9yIiwibGFzdExvZ2luQXQiOiIyMDI1LTA1LTEwIDIzOjQwOjIyIiwic2Vzc2lvbl9pZCI6IjExMDYwIiwiYXV0aF9rZXkiOiJRMklEVzZNQk1WU2ZrMjFGZ09aa3lSODJ1VjByaG85eiJ9LCJqdGkiOjgyMDR9.iH4ifhjbii2V-G8AznyC1VJ5YtxQ_H_Hgc6uoZ_3_CM"
}

# Request bodies
SUSPEND_BODY = {"remark": "Non Paid", "refund_type": 2}
RESUME_BODY = {"remark": "Payment Done"}

# Load the Excel file
df = pd.read_excel('.github/workflows/test.xlsx')

# Get current time in IST
current_time = datetime.now(IST)

# Define the time window for deactivation (11:58 PM to 12:00 AM)
start_deactivation_time = current_time.replace(hour=23, minute=58, second=0, microsecond=0)
end_deactivation_time = current_time.replace(hour=23, minute=59, second=59, microsecond=999999)

# If current time is before 11:58 PM, wait until 11:58 PM
if current_time < start_deactivation_time:
    remaining_time = (start_deactivation_time - current_time).total_seconds()
    print(f"Current time is {current_time.strftime('%H:%M %p IST')}. Waiting {int(remaining_time // 60)} minutes and {int(remaining_time % 60)} seconds until 11:57 PM.")
    time.sleep(remaining_time)

# Check if the current time is within the allowed deactivation window
if datetime.now(IST) > end_deactivation_time:
    print("It's past 12:00 AM, stopping execution.")
    sys.exit(0)
else:
    print("Proceeding with deactivation...")

# Function to suspend an account
def suspend_account(acc_no):
    url = SUSPEND_URL.format(accNo=acc_no)
    response = requests.post(url, json=SUSPEND_BODY, headers=HEADERS)
    if response.status_code == 201:
        print(f"Successfully suspended account {acc_no}")
        return acc_no  # Store suspended account
    else:
        print(f"Failed to suspend account {acc_no}: {response.status_code}, {response.text}")
        return None

# Step 1: Suspend accounts using multithreading
suspended_accounts = []
with ThreadPoolExecutor(max_workers=10) as executor:  # Adjust worker count as needed
    results = executor.map(suspend_account, df['accNo'])
    suspended_accounts = [acc for acc in results if acc is not None]

# Step 2: Wait for 2 minutes
print("Waiting for 2 minutes before checking date change...")
time.sleep(120)

# Step 3: Check if the date has changed
# print("Checking if the date has changed to the next day...")
# while True:
#     current_date = datetime.now(IST).date()
#     if current_date > start_deactivation_time.date():  # Ensures the date has changed
#         print(f"Date has changed to {current_date}. Proceeding with account resumption.")
#         break
#     else:
#         print(f"Current date is still {current_date}. Waiting for 1 minute before checking again...")
#         time.sleep(60)

# Function to resume an account
def resume_account(acc_no):
    url = RESUME_URL.format(accNo=acc_no)
    response = requests.post(url, json=RESUME_BODY, headers=HEADERS)
    if response.status_code == 201:
        print(f"Successfully resumed account {acc_no}")
    else:
        print(f"Failed to resume account {acc_no}: {response.status_code}, {response.text}")

# Step 4: Resume accounts using multithreading
with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(resume_account, suspended_accounts)
