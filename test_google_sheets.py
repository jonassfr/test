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

    # Öffne Google Sheet
    spreadsheet = client.open("MeineDaten")  # Name des Google Sheets
    worksheet = spreadsheet.sheet1  # Erstes Arbeitsblatt auswählen

    st.success("✅ Verbindung erfolgreich!")

    # 📊 **Tabelleninhalt anzeigen**
    data = worksheet.get_all_records()  # Lese alle Daten
    st.write("📋 **Aktuelle Tabelleninhalte:**", data)

    # ➕ **Daten hinzufügen**
    st.subheader("➕ Neue Zeile hinzufügen")

    # Eingabefelder für die neue Zeile
    col1, col2, col3 = st.columns(3)
    with col1:
        vorname = st.text_input("Vorname")
    with col2:
        nachname = st.text_input("Nachname")
    with col3:
        alter = st.number_input("Alter", min_value=0, max_value=120, step=1)

    # Wenn Button gedrückt wird → Neue Zeile einfügen
    if st.button("💾 Speichern"):
        neue_zeile = [vorname, nachname, alter]  # Werte für neue Zeile
        worksheet.append_row(neue_zeile)  # In Google Sheets schreiben
        st.success("✅ Neue Zeile erfolgreich hinzugefügt!")
        st.experimental_rerun()  # Seite neuladen, um die aktualisierte Tabelle zu sehen

except Exception as e:
    st.error(f"❌ Fehler bei der Authentifizierung: {e}")
