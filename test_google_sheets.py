import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Lade Credentials aus secrets
creds_dict = dict(st.secrets["GOOGLE_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict)
client = gspread.authorize(creds)

# Sheet öffnen
sheet = client.open("FuhrparkDaten").sheet1

# Testdaten abrufen
data = sheet.get_all_records()
df = pd.DataFrame(data)

st.write("✅ Verbindung erfolgreich!")
st.dataframe(df)
