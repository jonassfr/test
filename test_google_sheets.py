import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

def admin_login():
    st.sidebar.title("🔒 Admin Login")
    password = st.sidebar.text_input("Enter Password", type="password")
    if password == "B3ll@621":  # Du kannst das später über st.secrets absichern
        return True
    elif password:
        st.sidebar.error("Wrong Password")
        return False
    else:
        return False
        
# ✅ Connect to Google Sheets
creds_dict = dict(st.secrets["GOOGLE_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict)
client = gspread.authorize(creds)

# ✅ Load Sheet
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

def get_modelle():
    try:
        modell_sheet = client.open(SHEET_NAME).worksheet("Modelle")
        return [row[0] for row in modell_sheet.get_all_values() if row]
    except Exception as e:
        st.error(f"Error Loading Modells: {e}")
        return []
        
def get_service_typen():
    try:
        service_sheet = client.open(SHEET_NAME).worksheet("ServiceTypen")
        return [row[0] for row in service_sheet.get_all_values() if row]
    except Exception as e:
        st.error(f"Error Loading Service Types: {e}")
        return []

# ✅ UI Start
st.title("🚗 Vehicle Management")
seite = st.sidebar.selectbox("Menu", ["📋 Dashboard", "🛠️ Admin-Section"])

if seite == "📋 Dashboard":
    st.header("➕ Add New Entry")
    is_recurring = st.checkbox("🔁 Recurring Service?")
    user = st.selectbox("Who is submitting?", ["Bea", "Nik", "Bob", "Bri", "Dad"])
    
    with st.form("new_entry_form"):
        date = st.date_input("Date")
        
        
        car_options = get_modelle()

        # Standardmodell abhängig vom User (Fallback, falls kein Mapping passt)
        default_model = {
            "Bea": "Honda CRV",
            "Nik": "Honda Accord",
            "Bob": "Mitsubishi",
            "Bri": "Jeep",
            "Dad": "Kia"
        }.get(user, car_options[0] if car_options else "")
        
        default_index = car_options.index(default_model) if default_model in car_options else 0
        
        car_model = st.selectbox("Car Model", car_options, index=default_index)
        
        service_center = st.text_input("Service Center")
        
        service_type_options = get_service_typen()
        if not service_type_options:
            service_type_options = ["- no Service Type -"]
        service_type = st.selectbox("Service Type", service_type_options)
        
        mileage_last = st.number_input("Mileage at last service (mi)", min_value=0)
        cost = st.number_input("Cost ($)", min_value=0.0, step=10.0)
        status = st.selectbox("Status", ["active", "paused", "finished"])
        notes = st.text_input("Notes")
        
        next_service = ""
        mileage_interval = ""
    
        if is_recurring:
            next_service = st.date_input("Next Service Date")
            mileage_interval = st.number_input("Mileage interval until next service (mi)", min_value=0)
    
        submitted = st.form_submit_button("✅ Save Entry")
        if submitted:
            row = [
                date.strftime("%m/%d/%Y"),
                user,
                car_model,
                service_center,
                service_type,
                mileage_last,
                cost,
                status,
                notes,
                "yes" if is_recurring else "no",
                next_service.strftime("%m/%d/%Y") if is_recurring else "",
                mileage_interval
            ]
            insert_data(row)
            st.success("✅ Entry successfully saved!")
            st.rerun()
    
    # ✅ Display Data
    st.header("📋 All Entries")
    df = get_data()
    
    # Make sure Cost ($) is numeric
    df["Cost ($)"] = pd.to_numeric(df["Cost ($)"], errors="coerce")
    
    # 🔍 Filter by Car
    car_filter = st.selectbox("🚘 Filter by Car", ["All"] + df["Car Model"].unique().tolist())
    if car_filter != "All":
        df = df[df["Car Model"] == car_filter]
    
    # 📆 Sort by date
    df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y")
    df = df.sort_values(by="Date", ascending=False)
    
    # 💸 Total cost display
    st.markdown(f"**💰 Total Cost:** ${df['Cost ($)'].sum():,.2f}")
    
    # 🔔 Reminder for due services
    today = datetime.today()
    reminders = df[
        (df["Is Recurring"] == "yes") &
        (df["Next Service Date"] != "") &
        (pd.to_datetime(df["Next Service Date"], format="%m/%d/%Y") <= today)
    ]
    
    if not reminders.empty:
        st.warning("🔔 Upcoming Services Due:")
        for _, row in reminders.iterrows():
            mileage_info = f"{int(row['Mileage (Last)'])} mi / every {int(row['Mileage Interval'])} mi" \
                if row["Mileage (Last)"] and row["Mileage Interval"] else "Mileage info missing"
            st.write(
                f"- {row['Car Model']} (due on {row['Next Service Date']} | {mileage_info})"
            )
    
    
    # 📊 Show table
    st.dataframe(df, use_container_width=True)
    st.markdown("---")
    st.subheader("🗑️ Delete an Entry")
    
    # String-Datum + Label bauen
    df_display = df.copy()
    df_display["Date_str"] = df_display["Date"].dt.strftime("%m/%d/%Y")
    df_display["Label"] = df_display.apply(
        lambda row: f"{row['Date_str']} | {row['Car Model']} | {row['Service Type']} | {row['Service Center']}", axis=1
    )
    
    entry_to_delete = st.selectbox("Select an entry to delete", df_display["Label"].tolist())
    
    confirm = st.checkbox("Yes, I want to delete this entry.")
    
    if confirm and st.button("🗑️ Delete selected entry"):
        match = df_display[df_display["Label"] == entry_to_delete]
    
        if not match.empty:
            row_index = int(match.index[0])  # 👈 Hier ist der entscheidende Fix
            sheet = get_sheet()
            sheet.delete_rows(row_index + 2)
            st.success("✅ Entry deleted.")
            st.rerun()
        else:
            st.error("⚠️ Could not find the entry in the table.")

elif seite == "🛠️ Admin-Section":
    if admin_login():
        st.success("Access granted. Welcome to the admin area!")

        st.header("🚗 Add new Car Model")
        neues_modell = st.text_input("Name of new Model")
        if st.button("Add Model") and neues_modell:
            try:
                modell_sheet = client.open(SHEET_NAME).worksheet("Modelle")
                vorhandene_modelle = [x[0] for x in modell_sheet.get_all_values()]
                if neues_modell in vorhandene_modelle:
                    st.warning("Modell already exists.")
                else:
                    modell_sheet.append_row([neues_modell])
                    st.success(f"✅ Model '{neues_modell}' added successfully.")
            except Exception as e:
                st.error(f"Fehler: {e}")
        # 🔽 NEU: Modelle anzeigen und löschen
        st.markdown("---")
        st.subheader("📄 Current Model List")

        try:
            modell_sheet = client.open(SHEET_NAME).worksheet("Modelle")
            modelle_df = pd.DataFrame(modell_sheet.get_all_values(), columns=["Modell"])
            st.dataframe(modelle_df)

            # Auswahl für Löschung
            st.subheader("🗑️ Delete Car Model")
            modell_zum_loeschen = st.selectbox("Pick Model to delete", modelle_df["Modell"].tolist())

            if st.button("Delete Model"):
                zeilen = modell_sheet.get_all_values()
                for i, row in enumerate(zeilen):
                    if row and row[0] == modell_zum_loeschen:
                        modell_sheet.delete_rows(i + 1)  # +1 wegen 1-basiertem Index
                        st.success(f"✅ Model '{modell_zum_loeschen}' deleted successfully.")
                        st.rerun()
                        break
        except Exception as e:
            st.error(f"Error for loading or deleting Model: {e}")

        st.markdown("---")
        st.header("🔧 Manage Service Types")

        # Service-Typ hinzufügen
        neuer_service = st.text_input("Name of new Service Type")
        if st.button("Add Service Type") and neuer_service:
            try:
                service_sheet = client.open(SHEET_NAME).worksheet("ServiceTypen")
                vorhandene_services = [x[0] for x in service_sheet.get_all_values()]
                if neuer_service in vorhandene_services:
                    st.warning("Service Type already exists.")
                else:
                    service_sheet.append_row([neuer_service])
                    st.success(f"✅ Service Type '{neuer_service}' added successfully.")
            except Exception as e:
                st.error(f"Error for adding: {e}")

        # Aktuelle Liste anzeigen und löschen
        try:
            service_sheet = client.open(SHEET_NAME).worksheet("ServiceTypen")
            services_df = pd.DataFrame(service_sheet.get_all_values(), columns=["Service"])
            st.subheader("📄 Current Service Types")
            st.dataframe(services_df)

            st.subheader("🗑️ Delete Service Type")
            service_zum_loeschen = st.selectbox("Pick Service Type to delete", services_df["Service"].tolist())

            if st.button("Delete Service Type"):
                zeilen = service_sheet.get_all_values()
                for i, row in enumerate(zeilen):
                    if row and row[0] == service_zum_loeschen:
                        service_sheet.delete_rows(i + 1)
                        st.success(f"✅ Service Type '{service_zum_loeschen}' deleted successfully.")
                        st.rerun()
                        break
        except Exception as e:
            st.error(f"Error for printing or deleting: {e}")
        
            
    else:
        st.warning("Please enter the password to gain access.")
