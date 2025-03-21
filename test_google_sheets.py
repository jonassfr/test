import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Lade Google Credentials aus Streamlit Secrets
try:
    creds_json = st.secrets["GOOGLE_CREDENTIALS"]
    creds_dict = dict(st.secrets["GOOGLE_CREDENTIALS"])  # Stelle sicher, dass es ein Dictionary ist
    st.write("🔍 Private Key Vorschau:", creds_json["private_key"][:50] + "...")
   

    # Authentifiziere mit Google Sheets API
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict)
    client = gspread.authorize(creds)

    # Test: Liste verfügbare Google Sheets auf
    spreadsheet_list = client.openall()
    st.success("✅ Verbindung erfolgreich!")
    

except Exception as e:
    st.error(f"❌ Fehler bei der Authentifizierung: {e}")
