import json
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# Load Google Credentials from Streamlit Secrets
credentials_json = st.secrets["GOOGLE_CREDENTIALS"]

try:
    # Convert JSON string to dictionary
    creds_dict = json.loads(credentials_json)

    # Ensure private_key has proper newlines
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

    # Authenticate with Google Sheets API
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict)
    client = gspread.authorize(creds)

    st.success("✅ Google Sheets API connected successfully!")

except json.JSONDecodeError as e:
    st.error(f"JSON Decoding Error: {e}")
    st.stop()
except Exception as e:
    st.error(f"Unexpected Error: {e}")
    st.stop()
