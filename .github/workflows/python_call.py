import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz
import sys
import time

# Define IST timezone
IST = pytz.timezone('Asia/Kolkata')

# Get current time in IST
current_time = datetime.now(IST)

# Define the time window for deactivation (11:57 PM to 12:00 AM)
start_deactivation_time = current_time.replace(hour=23, minute=57, second=0, microsecond=0)
end_deactivation_time = current_time.replace(hour=23, minute=59, second=59, microsecond=999999)

# If current time is before 11:56 PM, wait until 11:57 PM
if current_time < start_deactivation_time:
    # Calculate the remaining time in seconds until 11:57 PM
    remaining_time = (start_deactivation_time - current_time).total_seconds()
    print(f"Current time is {current_time.strftime('%H:%M %p IST')}. Waiting {int(remaining_time // 60)} minutes and {int(remaining_time % 60)} seconds until 11:56 PM.")
    
    # Sleep for the remaining time
    time.sleep(remaining_time)

    # Update current time after waiting
    current_time = datetime.now(IST)

# Check if the current time is now within the allowed time window for deactivation
if current_time > end_deactivation_time:
    print(f"Current time is {current_time.strftime('%H:%M %p IST')}. It's past 12:00 AM, stopping execution.")
    sys.exit(0)  # Stop the script
else:
    print(f"Current time is {current_time.strftime('%H:%M %p IST')}. Proceeding with deactivation.")
    
# Load the Excel file
df = pd.read_excel('.github/workflows/test.xlsx')

# Define the base URLs and the headers
suspend_url = "https://fwprepaid.myfastway.in/api/index.php/v1/account/{accNo}/suspend"
resume_url = "https://fwprepaid.myfastway.in/api/index.php/v1/account/{accNo}/resume"
headers = {
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NDEyODU5MjcsImlzcyI6Imh0dHBzOlwvXC9md3ByZXBhaWQubXlmYXN0d2F5LmluIiwiYXVkIjoiaHR0cHM6XC9cL2Z3cHJlcGFpZC5teWZhc3R3YXkuaW4iLCJuYmYiOjE3NDEyODU5MjcsImV4cCI6MTc1MTY1MzkyNywiZXh0cmFfZGF0YSI6W10sInJlc3RyaWN0X2lwIjpbXSwiaXNfYWdncmVtZW50X3ZvaWQiOjAsImFsbG93ZWRfYXBpcyI6bnVsbCwiZGF0YSI6eyJ1c2VybmFtZSI6ImluLTAwMDAwMTYzNDUiLCJyb2xlTGFiZWwiOiJBZG1pbmlzdHJhdG9yIiwibGFzdExvZ2luQXQiOiIyMDI1LTAzLTA3IDAwOjAyOjA3Iiwic2Vzc2lvbl9pZCI6IjExMDYwIiwiYXV0aF9rZXkiOiJRMklEVzZNQk1WU2ZrMjFGZ09aa3lSODJ1VjByaG85eiJ9LCJqdGkiOjgyMDR9.wmRKRuq-ZR3ZwEVztW7yw4iMotbz4T5RRPW9OsgTuhI"
}

# Body of the suspend request
suspend_body = {
    "remark": "Non Paid",
    "refund_type": 2
}

# Body of the resume request
resume_body = {
    "remark": "Payment Done"
}

# Step 1: Deactivate accounts between 11:56 PM and 12:00 AM
suspended_accounts = []
for index, row in df.iterrows():
    acc_no = row['accNo']  # Replace 'accNo' with the actual column name in the Excel file

    # Suspend the account
    suspend_url_formatted = suspend_url.format(accNo=acc_no)
    response_suspend = requests.post(suspend_url_formatted, json=suspend_body, headers=headers)

    # Handle the suspend response
    if response_suspend.status_code == 201:
        print(f"Successfully suspended account {acc_no}: {response_suspend.status_code}, {response_suspend.text}")
        suspended_accounts.append(acc_no)  # Add to list of suspended accounts
    else:
        print(f"Failed to suspend account {acc_no}: {response_suspend.status_code}, {response_suspend.text}")

# Step 2: Wait for 5 minutes after deactivation
print("Waiting for 5 minutes before checking if the date has changed...")
time.sleep(100)  # 5 minutes delay (300 seconds)

# Step 3: Check if the date has changed to the next day before resuming accounts
# print("Checking if the date has changed to the next day...")
# while True:
#     # Get the current date
#     # current_date = datetime.now(IST).date()
#     # Calculate the next day
#     next_day = current_time  + timedelta(days=1)

#     # Wait for 1 minute and check if the date has changed
#     if datetime.now(IST).date() >= next_day:
#         print(f"Date has changed to {datetime.now(IST).date()}. Proceeding with account resumption.")
#         break
#     else:
#         print(f"Current date is still {current_date}. Waiting for 1 minute before checking again...")
#         time.sleep(60)  # Wait for 1 minute before checking again

# Step 4: Resume the suspended accounts after the date changes
for acc_no in suspended_accounts:
    resume_url_formatted = resume_url.format(accNo=acc_no)
    response_resume = requests.post(resume_url_formatted, json=resume_body, headers=headers)

    # Handle the resume response
    if response_resume.status_code == 201:
        print(f"Successfully resumed account {acc_no}: {response_resume.status_code}, {response_resume.text}")
    else:
        print(f"Failed to resume account {acc_no}: {response_resume.status_code}, {response_resume.text}")
