import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Lade Google Credentials aus Streamlit Secrets
try:
    creds_dict = dict(st.secrets["GOOGLE_CREDENTIALS"])  # Stelle sicher, dass es ein Dictionary ist
    
    # Private Key richtig formatieren
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

    # Authentifiziere mit Google Sheets API
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict)
    client = gspread.authorize(creds)

    # Test: Liste verfügbare Google Sheets auf
    spreadsheet_list = client.openall()
    st.success("✅ Verbindung erfolgreich!")
    st.write("📄 Verfügbare Tabellen:", [sheet.title for sheet in spreadsheet_list])

except Exception as e:
    st.error(f"❌ Fehler bei der Authentifizierung: {e}")
