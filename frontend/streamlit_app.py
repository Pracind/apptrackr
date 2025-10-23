import streamlit as st
import requests
import pandas as pd


API_URL = "http://127.0.0.1:8000"
FORCE_NAV_KEY = "force_dashboard"

st.set_page_config(page_title="AppTrackr", layout="wide")

def show_login():
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Log In"):
        resp = requests.post(f"{API_URL}/login", json={"email": email, "password": password})
        if resp.status_code == 200:
            st.success("Login successful!")
            # st.session_state.token = resp.json()["token"]
            # st.session_state.email = email
            user_data = resp.json()
            st.session_state.token = user_data["token"]
            st.session_state.email = user_data["user"]["email"]
            st.session_state.name = user_data["user"]["name"]

            st.session_state.nav = "Dashboard"  
            st.rerun()
        else:
            st.error("Invalid email or password")


def show_signup():
    st.subheader("Signup")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    name = st.text_input("Name")
    if st.button("Sign Up"):
        resp = requests.post(f"{API_URL}/signup", json={"email": email, "password": password, "name": name})
        if resp.status_code == 200:
            st.success("Signup successful! Please go to the Login tab.")
        else:
            st.error("Signup failed. Try a different email.")

def fetch_apps(token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{API_URL}/apps", headers=headers)
    if resp.status_code == 200:
        return resp.json()
    else:
        st.error("Failed to fetch applications.")
        return []

# --- Authentication gating ---
if "token" not in st.session_state:
    auth_mode = st.sidebar.radio("Account", ["Login", "Signup"])
    if auth_mode == "Login":
        show_login()
    else:
        show_signup()
    st.stop()

# --- Authenticated user interface ---
st.sidebar.success(f"Welcome, {st.session_state.get('name', 'user').title()}")

# Navigation sidebar
st.sidebar.header("Navigation")

if "nav" not in st.session_state:
    st.session_state["nav"] = "Dashboard"

if st.session_state.get(FORCE_NAV_KEY):
    st.session_state["nav"] = "Dashboard"
    del st.session_state[FORCE_NAV_KEY]

option = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Add Application", "Settings"],
    index=["Dashboard", "Add Application", "Settings"].index(st.session_state["nav"]),
    key="nav"
)

# App Header
st.title("AppTrackr Job Applications")
st.write("Track and manage your job applications with ease.")

if option == "Dashboard":
    st.header("Your Applications")
    st.info("List and filter your job applications here.")
    apps = fetch_apps(st.session_state.token)
    if apps:
        df = pd.DataFrame(apps)
        # cols = [
        #     "company_name", "role_title", "salary",          
        #     "city", "country", "applied_date",    
        #     "followup_date", "status", "followup_method", 
        #     "notes"           
        # ]

        # display_cols = [c for c in cols if c in df.columns]
        # st.dataframe(df[display_cols])

        statuses = ["All", "pending", "followed-up", "not-responded", "rejected", "accepted"]
        tabs = st.tabs(statuses)
        for idx, status in enumerate(statuses):
            with tabs[idx]:
                if status == "All":
                    filtered_df = df
                else:
                    filtered_df = df[df["status"] == status]

                st.write(f"Showing {len(filtered_df)} applications with status: {status if status != 'All' else 'any'}")

                # Status chip formatter
                def chip(s):
                    color = {
                        "pending": "#FFE066",
                        "followed-up": "#B8F2E6",
                        "not-responded": "#FFB4A2",
                        "rejected": "#E63946",
                        "accepted": "#4CAF50"
                    }.get(s, "#d3d3d3")
                    return f'<span style="background-color:{color};color:#222;padding:2px 8px;border-radius:8px;">{s.title()}</span>'

                # Apply chips
                chip_df = filtered_df.copy()
                chip_df["status"] = chip_df["status"].apply(chip)
                display_cols = [
                    "company_name", "role_title", "salary", "city", "country",
                    "applied_date", "followup_date", "status", "followup_method", "notes"
                ]
                chip_df = chip_df[[c for c in display_cols if c in chip_df.columns]]
                st.write(chip_df.to_html(escape=False), unsafe_allow_html=True)       
    else:
        st.write("No applications found.")

elif option == "Add Application":
    st.header("Add New Application")
    st.info("Fill in details to submit a new application.")
    # TODO: Add form for new application

elif option == "Settings":
    st.header("Settings")
    st.info("Configure your preferences.")
    # TODO: Add settings management

# Footer
st.markdown("---")
st.caption("Built with Streamlit • AppTrackr © 2025")
