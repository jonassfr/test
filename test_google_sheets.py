import json
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# Load Google Credentials from Streamlit Secrets
credentials_json = st.secrets["GOOGLE_CREDENTIALS"]

# Debugging: Print the first few characters to verify it's correctly retrieved
st.write(f"First 50 characters of secret: {credentials_json[:50]}...")

try:
    creds_dict = json.loads(credentials_json)
except json.JSONDecodeError as e:
    st.error(f"Error decoding JSON: {e}")
    st.stop()

# Authenticate with Google Sheets API
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict)
client = gspread.authorize(creds)
