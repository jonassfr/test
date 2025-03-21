import streamlit as st
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Lade Google Credentials aus Streamlit Secrets
credentials_json = st.secrets["GOOGLE_CREDENTIALS"]





# Authentifiziere mit Google Sheets API
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict)
client = gspread.authorize(creds)

# Test: Liste verfügbare Google Sheets auf
try:
    spreadsheet_list = client.openall()
    st.success("✅ Verbindung erfolgreich!")
    st.write("📄 Verfügbare Tabellen:", [sheet.title for sheet in spreadsheet_list])
except Exception as e:
    st.error(f"❌ Fehler: {e}")
