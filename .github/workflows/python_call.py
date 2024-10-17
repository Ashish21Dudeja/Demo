import pandas as pd
import requests

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
