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
    # Öffne das Google Sheet
    spreadsheet = client.open("MeineDaten")  # Name der Tabelle (Google Sheet)
    worksheet = spreadsheet.sheet1  # Wählt das erste Arbeitsblatt aus
    
    # Test: Lese alle Daten aus der Tabelle
    data = worksheet.get_all_records()  # Holt alle Zeilen als Dictionary
    
    st.write("📊 Tabelleninhalte:", data)
    if st.button("➕ Neue Zeile hinzufügen"):
    worksheet.append_row(["Jonas", "Schaefer", "Streamlit Test"])
    st.success("✅ Neue Zeile erfolgreich hinzugefügt!")

except Exception as e:
    st.error(f"❌ Fehler bei der Authentifizierung: {e}")
