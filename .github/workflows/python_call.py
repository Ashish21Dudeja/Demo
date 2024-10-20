import pandas as pd
import requests

from datetime import datetime
import pytz
import sys
import requests
import pandas as pd

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

# Define the base URL and the headers
base_url = "https://fwprepaid.myfastway.in/api/index.php/v1/account/{accNo}/suspend"
headers = {
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3MjMwMTMwMTksImlzcyI6Imh0dHBzOlwvXC9md3ByZXBhaWQubXlmYXN0d2F5LmluIiwiYXVkIjoiaHR0cHM6XC9cL2Z3cHJlcGFpZC5teWZhc3R3YXkuaW4iLCJuYmYiOjE3MjMwMTMwMTksImV4cCI6MTczMzM4MTAxOSwiZXh0cmFfZGF0YSI6W10sInJlc3RyaWN0X2lwIjpbXSwiaXNfYWdncmVtZW50X3ZvaWQiOjAsImFsbG93ZWRfYXBpcyI6bnVsbCwiZGF0YSI6eyJ1c2VybmFtZSI6ImluLTAwMDAwMTYzNDUiLCJyb2xlTGFiZWwiOiJBZG1pbmlzdHJhdG9yIiwibGFzdExvZ2luQXQiOiIyMDI0LTA4LTA3IDEyOjEzOjM5Iiwic2Vzc2lvbl9pZCI6IjExMDYwIiwiYXV0aF9rZXkiOiJqN2M0ZWVRRHhCLW1jeWtpZmg5ZzI0eHNrZUZRclREYyJ9LCJqdGkiOjgyMDR9.wR_NqaES32YRvrWZDKDc_P3b3OmeBnnz6m8ZhIU9ae8"
}

# Body of the request
body = {
    "remark": "Non Paid",
    "refund_type": 2
}

# Iterate over each account number in the Excel file and make the API request
for index, row in df.iterrows():
    acc_no = row['accNo']  # Replace 'accNo' with the actual column name in the Excel file
    url = base_url.format(accNo=acc_no)

    # Make the API request
    response = requests.post(url, json=body, headers=headers)

    # Handle the response
    if response.status_code == 201:
        print(f"Successfully suspended account {acc_no}: {response.status_code}, {response.text}")
        # print(f"Successfully suspended account {acc_no}")
    else:
        print(f"Failed to suspend account {acc_no}: {response.status_code}, {response.text}")
