import csv
import os
from datetime import date

import streamlit as st

FILE = "applications.csv"
FIELDS = ["company", "role", "status", "date"]
STATUSES = ["Applied", "Interview", "Rejected", "Offer"]
FOLLOW_UP_DAYS = 7


def load_applications():
    if not os.path.exists(FILE):
        return []
    with open(FILE, newline="") as f:
        return list(csv.DictReader(f))


def save_applications(applications):
    with open(FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(applications)


def clean_status(text):
    return text.strip().capitalize()


st.title("Job Tracker")
applications = load_applications()

# --- Add a new application ---
with st.form("add_form", clear_on_submit=True):
    st.subheader("Add application")
    company = st.text_input("Company")
    role = st.text_input("Role")
    status = st.selectbox("Status", STATUSES)
    applied_on = st.date_input("Date applied", value=date.today())
    submitted = st.form_submit_button("Save")

if submitted:
    if company == "":
        st.error("Please enter a company name.")
    else:
        app = {"company": company, "role": role, "status": status,
               "date": applied_on.isoformat()}
        applications.append(app)
        save_applications(applications)
        st.success("Saved " + company)

# --- Update a status ---
if len(applications) > 0:
    st.subheader("Update status")
    labels = [app["company"] + " - " + app["role"] for app in applications]
    picked = st.selectbox("Application", labels)
    new_status = st.selectbox("New status", STATUSES, key="new_status")
    if st.button("Update"):
        index = labels.index(picked)
        applications[index]["status"] = new_status
        save_applications(applications)
        st.success("Updated " + picked + " to " + new_status)

# --- Stats ---
st.subheader("Stats")
counts = {}
for app in applications:
    status = clean_status(app["status"])
    counts[status] = counts.get(status, 0) + 1
columns = st.columns(len(STATUSES))
for i, status in enumerate(STATUSES):
    columns[i].metric(status, counts.get(status, 0))

# --- Follow-ups ---
st.subheader("Follow-ups due")
today = date.today()
found = False
for app in applications:
    if clean_status(app["status"]) != "Applied" or not app.get("date"):
        continue
    days = (today - date.fromisoformat(app["date"])).days
    if days >= FOLLOW_UP_DAYS:
        st.warning(app["company"] + " - applied " + str(days) + " days ago")
        found = True
if not found:
    st.write("No follow-ups due.")

# --- All applications ---
st.subheader("All applications")
st.dataframe(applications)