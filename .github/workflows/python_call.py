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

# Define 11:59 PM in IST for today
end_of_day = current_time.replace(hour=23, minute=59, second=0, microsecond=0)

# Check if current time is before 11:59 PM
if current_time >= end_of_day:
    print("The time is past 11:59 PM IST. Stopping execution.")
    sys.exit(0)  # Stop the script
else:
    print(f"Current time is {current_time.strftime('%H:%M %p IST')}. Proceeding with execution.")
    
# Load the Excel file
df = pd.read_excel('.github/workflows/test.xlsx')

# Define the base URLs and the headers
suspend_url = "https://fwprepaid.myfastway.in/api/index.php/v1/account/{accNo}/suspend"
resume_url = "https://fwprepaid.myfastway.in/api/index.php/v1/account/{accNo}/resume"
headers = {
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3MjMwMTMwMTksImlzcyI6Imh0dHBzOlwvXC9md3ByZXBhaWQubXlmYXN0d2F5LmluIiwiYXVkIjoiaHR0cHM6XC9cL2Z3cHJlcGFpZC5teWZhc3R3YXkuaW4iLCJuYmYiOjE3MjMwMTMwMTksImV4cCI6MTczMzM4MTAxOSwiZXh0cmFfZGF0YSI6W10sInJlc3RyaWN0X2lwIjpbXSwiaXNfYWdncmVtZW50X3ZvaWQiOjAsImFsbG93ZWRfYXBpcyI6bnVsbCwiZGF0YSI6eyJ1c2VybmFtZSI6ImluLTAwMDAwMTYzNDUiLCJyb2xlTGFiZWwiOiJBZG1pbmlzdHJhdG9yIiwibGFzdExvZ2luQXQiOiIyMDI0LTA4LTA3IDEyOjEzOjM5Iiwic2Vzc2lvbl9pZCI6IjExMDYwIiwiYXV0aF9rZXkiOiJqN2M0ZWVRRHhCLW1jeWtpZmg5ZzI0eHNrZUZRclREYyJ9LCJqdGkiOjgyMDR9.wR_NqaES32YRvrWZDKDc_P3b3OmeBnnz6m8ZhIU9ae8"
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

# Step 1: Suspend all accounts
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

# Step 2: Wait until the date changes to the next day
print("Waiting for the date to change to the next day...")
while True:
    # Get the current date and compare it with the initial date
    current_time = datetime.now(IST)
    initial_date = current_time.date()

    # Calculate the next day
    next_day = initial_date + timedelta(days=1)

    # Wait for 1 minute and check if the date has changed
    if datetime.now(IST).date() >= next_day:
        print(f"Date has changed to {datetime.now(IST).date()}. Proceeding with account resumption.")
        break
    else:
        print(f"Current date is {initial_date}. Waiting for 1 minute...")
        time.sleep(60)  # Wait for 1 minute before checking again

# Step 3: Resume the suspended accounts
for acc_no in suspended_accounts:
    resume_url_formatted = resume_url.format(accNo=acc_no)
    response_resume = requests.post(resume_url_formatted, json=resume_body, headers=headers)

    # Handle the resume response
    if response_resume.status_code == 201:
        print(f"Successfully resumed account {acc_no}: {response_resume.status_code}, {response_resume.text}")
    else:
        print(f"Failed to resume account {acc_no}: {response_resume.status_code}, {response_resume.text}")
