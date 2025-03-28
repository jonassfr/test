import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

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

# ✅ UI Start
st.title("🚗 Vehicle Management")

st.header("➕ Add New Entry")
is_recurring = st.checkbox("🔁 Is this a recurring service? If yes check the box!")
user = st.selectbox("Who is submitting?", ["Bea", "Nik", "Bob", "Bri", "Dad"])

with st.form("new_entry_form"):
    date = st.date_input("Date")
    
    
    # Automatically assign car model based on user
    car_mapping = {
        "Bea": "Honda CRV",
        "Nik": "Honda Accord",
        "Bob": "Mitsubishi",
        "Bri": "Jeep",
        "Dad": "Kia"
    }
    car_options = list(car_mapping.values())
    default_index = car_options.index(car_mapping[user])
    car_model = st.selectbox("Car Model", car_options, index=default_index)
    
    service_center = st.text_input("Service Center")
    service_type = st.selectbox("Service Type", ["Inspection", "Oil Change", "Tires", "Brakes", "Checkup", "Battery", "Alignment", "Other"])
    cost = st.number_input("Cost ($)", min_value=0.0, step=10.0)
    status = st.selectbox("Status", ["active", "paused", "finished"])
    notes = st.text_input("Notes")
    
    next_service = ""
    mileage_last = ""
    mileage_interval = ""

    if is_recurring:
        next_service = st.date_input("Next Service Date")
        mileage_last = st.number_input("Mileage at last service (mi)", min_value=0)
        mileage_interval = st.number_input("Mileage interval until next service (mi)", min_value=0)

    submitted = st.form_submit_button("✅ Save Entry")
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
            next_service.strftime("%m/%d/%Y") if is_recurring else "",
            mileage_last,
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
st.subheader("🗑️ Manage Entries")

# +1 because Google Sheets is 1-indexed and has header row
for i, row in df.iterrows():
    with st.expander(f"📝 Entry {i+2}: {row['Car Model']} | {row['Date'].strftime('%m/%d/%Y')}"):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.write(f"Service: **{row['Service Type']}** at **{row['Service Center']}**")
            st.write(f"Submitted by: **{row['User']}**")
            st.write(f"Cost: **${row['Cost ($)']}**")
            st.write(f"Status: **{row['Status']}**")
        with col2:
            confirm = st.checkbox("Yes, I’m sure I want to delete this entry.", key=f"confirm_{i}")
            if confirm:
                if st.button("🗑️ Delete", key=f"delete_{i}"):
                    sheet = get_sheet()
                    sheet.delete_rows(i + 2)
                    st.success("✅ Entry deleted.")
                    st.rerun()

