import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ✅ Google Verbindung herstellen
creds_dict = dict(st.secrets["GOOGLE_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict)
client = gspread.authorize(creds)

# ✅ Tabelle laden
SHEET_NAME = "FuhrparkDaten"
def get_sheet():
    return client.open(SHEET_NAME).sheet1

def get_data():
    sheet = get_sheet()
    data = sheet.get_all_records()
    return pd.DataFrame(data) if data else pd.DataFrame(columns=[
        "Date", "User", "Car Model", "Service Center", "Service Type", "Cost ($)", 
        "Status", "Notes", "Is Recurring", "Next Service Date"
    ])

def insert_data(row):
    sheet = get_sheet()
    sheet.append_row(row)

# ✅ UI Start
st.title("🚗 Fuhrparkverwaltung")

st.header("➕ Neuen Eintrag hinzufügen")
with st.form("new_entry_form"):
    date = st.date_input("Datum")
    user = st.selectbox("Wer trägt ein?", ["Bea", "Nik", "Bob", "Bri", "Dad"])
    
    # Automatisch Modell zuordnen
    car_mapping = {
        "Bea": "Honda CRV",
        "Nik": "Honda Accord",
        "Bob": "Mitsubishi",
        "Bri": "Jeep",
        "Dad": "Kia"
    }
    car_model = f"{user} {car_mapping[user]}"
    
    service_center = st.text_input("Werkstatt")
    service_type = st.selectbox("Art des Services", ["TÜV", "Ölwechsel", "Reifen", "Bremsen", "Inspektion", "Sonstiges"])
    cost = st.number_input("Kosten ($)", min_value=0.0, step=10.0)
    status = st.selectbox("Status", ["active", "paused", "finished"])
    notes = st.text_input("Notizen")
    
    is_recurring = st.checkbox("🔁 Wiederkehrender Service?")
    next_service = st.date_input("Nächstes Servicedatum", disabled=not is_recurring)

    submitted = st.form_submit_button("✅ Eintrag speichern")
    if submitted:
        row = [
            date.strftime("%m/%d/%Y"),
            user,
            car_model,
            service_center,
            service_type,
            cost,
            status,
            notes,
            "yes" if is_recurring else "no",
            next_service.strftime("%m/%d/%Y") if is_recurring else ""
        ]
        insert_data(row)
        st.success("✅ Eintrag erfolgreich gespeichert!")
        st.rerun()

# ✅ Daten anzeigen
st.header("📋 Übersicht aller Einträge")
df = get_data()

# Stelle sicher, dass Cost ($) numerisch ist
df["Cost ($)"] = pd.to_numeric(df["Cost ($)"], errors="coerce")

# 🔍 Filter nach Auto
car_filter = st.selectbox("🚘 Filter nach Auto", ["Alle"] + df["Car Model"].unique().tolist())
if car_filter != "Alle":
    df = df[df["Car Model"] == car_filter]

# 📆 Sortierung nach Datum (optional)
df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y")
df = df.sort_values(by="Date", ascending=False)

# 💸 Gesamtkosten anzeigen
st.markdown(f"**💰 Gesamtkosten:** ${df['Cost ($)'].sum():,.2f}")

# 🔔 Reminderanzeige für fällige Services
today = datetime.today()
reminders = df[
    (df["Is Recurring"] == "yes") &
    (df["Next Service Date"] != "") &
    (pd.to_datetime(df["Next Service Date"], format="%m/%d/%Y") <= today)
]

if not reminders.empty:
    st.warning("🔔 Fällige Services:")
    for _, row in reminders.iterrows():
        st.write(f"- {row['Car Model']} (fällig am {row['Next Service Date']})")

# 📊 Tabelle anzeigen
st.dataframe(df, use_container_width=True)

