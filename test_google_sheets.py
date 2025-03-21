import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# Lade Google Credentials aus Streamlit Secrets
credentials_json = st.secrets["GOOGLE_CREDENTIALS"]
creds_dict = json.loads(credentials_json)

# Authentifiziere mit Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Verbindung testen
st.title("🔍 Google Sheets Test")
try:
    sheet = client.open("MeineDaten").sheet1  # Name des Google Sheets
    data = sheet.get_all_records()  # Alle Daten abrufen
    st.success("✅ Verbindung erfolgreich! Hier sind die Daten aus Google Sheets:")
    st.write(pd.DataFrame(data))  # Daten als Tabelle anzeigen
except Exception as e:
    st.error(f"❌ Fehler beim Zugriff auf Google Sheets: {e}")
