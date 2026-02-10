import os
import streamlit as st

# Path where Streamlit Cloud allows writing files
CREDS_PATH = "/tmp/gcp_creds.json"

# Write credentials JSON to a real file (only once)
if not os.path.exists(CREDS_PATH):
    with open(CREDS_PATH, "w") as f:
        f.write(st.secrets["GOOGLE_SHEETS_CREDENTIALS_JSON"])

# Export env var so your existing code picks it up
os.environ["GOOGLE_SHEETS_CREDENTIALS_PATH"] = CREDS_PATH

# Optional: expose other secrets as env vars (if your code uses os.getenv)
for key in [
    "GEMINI_API_KEY",
    "OPENAI_API_KEY",
    "GOOGLE_SHEETS_PILOT_ROSTER_ID",
    "GOOGLE_SHEETS_DRONE_FLEET_ID",
    "GOOGLE_SHEETS_MISSIONS_ID",
]:
    if key in st.secrets:
        os.environ[key] = st.secrets[key]

# Run your original app (UNCHANGED)
import main
