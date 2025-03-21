import streamlit as st
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Lade Google Credentials aus Streamlit Secrets
try:
    credentials_json = st.secrets["GOOGLE_CREDENTIALS"]
    creds_dict = json.loads(json.dumps(credentials_json))  # Sicherstellen, dass es ein JSON-Objekt ist

    # Fix: Ersetze doppelte Escape-Sequenzen für den Private Key
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

    # Debugging: Zeige den Private Key teilweise an (später entfernen!)
    st.write("🔑 Private Key Preview:", creds_dict["private_key"][:50])

    # Authentifiziere mit Google Sheets API
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict)
    client = gspread.authorize(creds)

    # Test: Liste verfügbare Google Sheets auf
    spreadsheet_list = client.openall()
    st.success("✅ Verbindung erfolgreich!")
    st.write("📄 Verfügbare Tabellen:", [sheet.title for sheet in spreadsheet_list])

except Exception as e:
    st.error(f"❌ Fehler bei der Authentifizierung: {e}")
