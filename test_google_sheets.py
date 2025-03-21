import json
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# Lade Google Credentials aus Streamlit Secrets
credentials_json = st.secrets["GOOGLE_CREDENTIALS"]

try:
    # JSON-String in ein Dictionary umwandeln
    creds_dict = json.loads(credentials_json)

    # Sicherstellen, dass die private_key das richtige Format hat
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

    # Debug: Zeige die ersten 100 Zeichen des private_key, um Formatfehler zu finden
    st.write("Private Key Preview:", creds_dict["private_key"][:100])

    # Authentifiziere mit Google Sheets API
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict)
    client = gspread.authorize(creds)

    st.success("✅ Google Sheets API connected successfully!")

except json.JSONDecodeError as e:
    st.error(f"❌ JSON Decoding Error: {e}")
    st.stop()
except Exception as e:
    st.error(f"❌ Unexpected Error: {e}")
    st.stop()
