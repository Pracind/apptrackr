import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta, datetime
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import altair as alt


st_autorefresh(interval=30000)

initial_keys = {
    "nav": "Dashboard",
    "notif_dropdown_open": False,
    "editing_id": None,
    "editing_tab_status": None,
    "confirm_delete": False,
    "token": None,
    "email": None,
    "name": None,
    # add more as needed, e.g. "demo_mode": False, "draft_company": ""
}
for k, v in initial_keys.items():
    if k not in st.session_state:
        st.session_state[k] = v


API_URL = "http://127.0.0.1:8000"  #"http://127.0.0.1:8000" , "https://apptrackr.onrender.com"
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
            user_data = resp.json()
            st.session_state.token = user_data["token"]
            print("DEBUG TOKEN:", user_data["token"])
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
            st.success("Signup successful!")
        else:
            st.error("Signup failed. Try again.")

def fetch_apps(token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{API_URL}/apps", headers=headers)
    if resp.status_code == 200:
        return resp.json()
    else:
        st.error("Failed to fetch applications.")
        return []

def fetch_metrics(token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{API_URL}/metrics", headers=headers)
    if resp.status_code == 200:
        return resp.json()
    else:
        st.error("Failed to fetch metrics.")
        return {"applications_total": 0, "applications_by_status": {}}
    
def fetch_app_timeline(app_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{API_URL}/apps/{app_id}/timeline", headers=headers)
    if resp.status_code == 200:
        return resp.json()
    else:
        st.error("Failed to fetch timeline.")
        return []
    
def add_app(data, token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{API_URL}/apps", json=data, headers=headers)
    return resp

def edit_app(app_id, data, token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.put(f"{API_URL}/apps/{app_id}", json=data, headers=headers)
    return resp

def make_edit_button(row_id):
    return f'<form action="" method="post"><button name="edit_clicked" value="{row_id}" style="background:#3075d1;color:white;border:none;padding:3px 12px;border-radius:6px;">Edit</button></form>'

def delete_app(app_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.delete(f"{API_URL}/apps/{app_id}", headers=headers)
    return resp


def get_notifications():
    token = st.session_state.get("token")
    if not token:
        return []
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/notifications", headers=headers)
    if response.ok:
        return response.json()
    return []

def mark_notifications_as_read():
    token = st.session_state.get("token")
    if not token:
        return
    headers = {"Authorization": f"Bearer {token}"}
    requests.post(f"{API_URL}/notifications/mark-read", headers=headers)

def run_automation_now():
    token = st.session_state.get("token")
    if not token:
        st.warning("You must be logged in.")
        return
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{API_URL}/automation/run-now", headers=headers)
    if resp.ok:
        res = resp.json()
        st.success(f"Automation ran: processed {res.get('processed', '?')} applications")
    else:
        st.error("Failed to run automation!")



    
edit_clicked = st.query_params.get("edit_clicked", None)
if edit_clicked:
    st.session_state["editing_id"] = int(edit_clicked)
    st.query_params.pop("edit_clicked")  # Remove the query param after reading it
    st.rerun()

# --- Authentication gating ---
if "token" not in st.session_state:
    auth_mode = st.sidebar.radio("Account", ["Login", "Signup"])
    if auth_mode == "Login":
        show_login()
        
    else:
        show_signup()
    st.stop()

# --- Authenticated user interface ---
st.sidebar.success(f"Welcome, {(st.session_state.get('name') or 'User').title()}")

notifications = get_notifications()

notif_count = len(notifications)
bell_icon = "🔔"
badge = f" {notif_count}" if notif_count > 0 else ""


if st.button(f"{bell_icon}{badge}", key="notif_bell"):
    st.session_state["notif_dropdown_open"] = not st.session_state["notif_dropdown_open"]
    st.rerun()

if st.session_state["notif_dropdown_open"]:
    print("Notifications panel open, count:", notif_count)
    if notif_count == 0:
        st.info("No new notifications.")
    else:
        for notif in notifications:
            st.markdown(f"- {notif['message']}")
        # Mark all as read button
        if st.button("Mark all as read", key="mark_all_read"):
            print("Clearing notifs")
            mark_notifications_as_read()
            print("Notifs cleared")
            st.session_state["notif_dropdown_open"] = False
            st.rerun()



# Navigation sidebar
st.sidebar.header("Navigation")

nav = st.session_state.get("nav", "Dashboard")


if st.session_state.get(FORCE_NAV_KEY):
    st.session_state["nav"] = "Dashboard"
    del st.session_state[FORCE_NAV_KEY]
    st.rerun()

option = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Add Application", "Metrics", "Settings"],
    index=["Dashboard", "Add Application", "Metrics", "Settings"].index(st.session_state["nav"]),
    key="nav"
)


# App Header
st.title("AppTrackr Job Applications")
st.write("Track and manage your job applications with ease.")

if option == "Dashboard":
    st.header("Your Applications")
    
    col_header, col_refresh = st.columns([8,1])
    with col_header:
        st.info("List and filter your job applications here.")
    with col_refresh:
        if st.button("🔄", help="Run Automation Now"):
            run_automation_now()
            st.rerun()

    apps = fetch_apps(st.session_state.token)
    if apps:
        df = pd.DataFrame(apps)

        today = date.today()

        # Format applied_date and followup_date to show only date part
        df['applied_date'] = pd.to_datetime(df['applied_date']).dt.date.astype(str)
        df['followup_date'] = pd.to_datetime(df['followup_date']).dt.date.astype(str)

        # Status chip formatter
        def chip(s):
            color = {
                "active": "#4CAF50",
                "pending": "#FFE066",
                "followed-up": "#B8F2E6",
                "not-responded": "#FFB4A2",
                "rejected": "#E63946",
                "accepted": "#02FFFB"
            }.get(s, "#d3d3d3")
            return f'<span style="background-color:{color};color:#222;padding:2px 8px;border-radius:8px;">{s.title()}</span>'

        # Apply chips just for display, not for actual editing values
        chip_df = df.copy()
        chip_df["status_chip"] = chip_df["status"].apply(chip)

        statuses = ["All", "active", "pending", "followed-up", "not-responded", "rejected", "accepted"]
        tabs = st.tabs(statuses)
        for idx, status in enumerate(statuses):
            with tabs[idx]:
                if status == "All":
                    filtered_df = df
                    filtered_chip_df = chip_df
                else:
                    filtered_df = df[df["status"] == status]
                    filtered_chip_df = chip_df[chip_df["status"] == status]

                st.write(f"Showing {len(filtered_df)} applications with status: {status if status != 'All' else 'any'}")

                display_cols = [
                    "company_name", "role_title", "salary", "city", "country",
                    "applied_date", "followup_date", "status_chip", "followup_method", "notes"
                ]

                # Render table using st.columns for native buttons
                header_cols = st.columns(len(display_cols) + 1)
                for i, col in enumerate(display_cols):
                    header_cols[i].markdown(f"**{col.replace('_chip','').replace('_',' ').title()}**")
                header_cols[-1].markdown("**Edit**")

                for i, row in filtered_chip_df.iterrows():
                    row_cols = st.columns(len(display_cols) + 1)
                    for j, col in enumerate(display_cols):
                        row_cols[j].write(row[col], unsafe_allow_html=True)
                    # True Streamlit button, not HTML
                    if row_cols[-1].button("Edit", key=f"editbtn_{row['id']}_{idx}"):
                        st.session_state['editing_id'] = row['id']
                        st.session_state['editing_tab_status'] = status
                        st.rerun()

        # --- EDIT FORM --
        if 'editing_id' in st.session_state:
            editing_id = st.session_state['editing_id']
            editing_row = df[df['id'] == editing_id].iloc[0]
            st.markdown("---")
            st.subheader(f"Edit Application: {editing_row['company_name']} - {editing_row['role_title']}")
            with st.form("edit_application_form"):
                edit_company = st.text_input("Company Name", value=editing_row['company_name'])
                edit_role = st.text_input("Role Title", value=editing_row['role_title'])
                edit_salary = st.text_input("Salary", value=editing_row['salary'])
                edit_city = st.text_input("City", value=editing_row['city'])
                edit_country = st.text_input("Country", value=editing_row['country'])
                edit_applied = st.text_input("Applied Date", value=editing_row['applied_date'])
                edit_followup = st.text_input("Followup Date", value=editing_row['followup_date'])
                edit_status = st.selectbox(
                    "Status", 
                    ["active", "pending", "followed-up", "not-responded", "rejected", "accepted"],
                    index=["active" ,"pending", "followed-up", "not-responded", "rejected", "accepted"].index(editing_row['status']),
                )
                edit_method = st.text_input("Followup Method", value=editing_row['followup_method'])
                edit_notes = st.text_area("Notes", value=editing_row['notes'])

                submitted = st.form_submit_button("Save Changes")
                cancel = st.form_submit_button("Cancel Edit")
                delete = st.form_submit_button("Delete")

                if submitted:
                    data = {
                        "company_name": edit_company,
                        "role_title": edit_role,
                        "salary": edit_salary,
                        "city": edit_city,
                        "country": edit_country,
                        "applied_date": edit_applied,
                        "followup_date": edit_followup,
                        "status": edit_status,
                        "followup_method": edit_method,
                        "notes": edit_notes
                    }

                    if edit_status == "followed-up":
                        data["followed_up_at"] = datetime.now().isoformat()
    
                    resp = edit_app(editing_id, data, st.session_state.token)
                    if resp.status_code == 200:
                        st.success("Application updated! Refresh to see changes.")
                        del st.session_state['editing_id']
                        del st.session_state['editing_tab_status']
                        st.session_state[FORCE_NAV_KEY] = True
                        st.rerun()
                    else:
                        st.error(f"Edit failed: {resp.text}")
                elif cancel:
                    del st.session_state['editing_id']
                    del st.session_state['editing_tab_status']
                    st.rerun()
                elif delete:
                    st.session_state['confirm_delete'] = True
                    st.rerun()
        
        # --- DELETE CONFIRMATION (outside form) ---
        if 'confirm_delete' not in st.session_state:
            st.session_state['confirm_delete'] = False

        # Only show confirmation if editing_id exists AND delete was clicked
        if st.session_state.get('confirm_delete', False) and 'editing_id' in st.session_state:
            st.warning("Are you sure you want to delete this application? This action cannot be undone.")
            col1, col2 = st.columns([1, 1])
            with col1:
                confirm = st.button("Yes, Delete", key="yes_delete")
            with col2:
                cancel_confirm = st.button("Cancel", key="cancel_delete_confirm")

            if confirm:
                resp = delete_app(st.session_state['editing_id'], st.session_state.token)
                if resp.status_code == 200:
                    st.success("Application deleted!")
                    st.session_state['confirm_delete'] = False
                    del st.session_state['editing_id']
                    del st.session_state['editing_tab_status']
                    st.session_state[FORCE_NAV_KEY] = True
                    st.rerun()
                else:
                    st.error(f"Delete failed: {resp.text}")
                    st.session_state['confirm_delete'] = False
            elif cancel_confirm:
                st.session_state['confirm_delete'] = False
                st.rerun()

        else:
            # Always reset it if not currently editing
            st.session_state['confirm_delete'] = False


    else:
        st.write("No applications found.")

elif option == "Add Application":
    with st.form("add_app_form"):
        company_name = st.text_input("Company", max_chars=100)
        role_title = st.text_input("Role Title", max_chars=100)
        salary = st.text_input("Salary")
        city = st.text_input("City", max_chars=50)
        country = st.text_input("Country", max_chars=50)
        applied_date = st.date_input("Applied Date")
        followup_date = st.date_input("Follow-up Date", value=None)
        status = st.selectbox("Status", ["active", "pending", "followed-up", "not-responded", "rejected", "accepted"])
        followup_method = st.selectbox("Follow-up Method", ["email", "phone", "portal", "other"])
        notes = st.text_area("Notes", max_chars=300)

        submitted = st.form_submit_button("Add Application")

        if submitted:
            # Simple required field validation (all except notes)
            missing_fields = []
            if not company_name:
                missing_fields.append("Company")
            if not role_title:
                missing_fields.append("Role Title")
            if not city:
                missing_fields.append("City")
            if not country:
                missing_fields.append("Country")
            if not applied_date:
                missing_fields.append("Applied Date")
            if not followup_date:
                missing_fields.append("Follow-up Date")
            if not status:
                missing_fields.append("Status")

            if missing_fields:
                st.warning(f"Please fill in all required fields: {', '.join(missing_fields)}")
                
            else:
                data = {
                    "company_name": company_name,
                    "role_title": role_title,
                    "salary": salary,
                    "city": city,
                    "country": country,
                    "applied_date": str(applied_date),
                    "followup_date": str(followup_date) if followup_date else None,
                    "status": status,
                    "followup_method": followup_method,
                    "notes": notes
                }
                resp = add_app(data, st.session_state.token)
                if resp.status_code == 200:
                    st.success("Application added! Go to Dashboard to see it.")
                    st.session_state[FORCE_NAV_KEY] = True
                    st.rerun()
                else:
                    st.error(f"Application add failed: {resp.text}")

elif option == "Metrics":
    st.header("📊 Application Metrics & Charts")

    metrics = fetch_metrics(st.session_state.token)
    status_counts = metrics["applications_by_status"]

    status_order = ["Total Applications", "pending", "active", "followed-up", "not-responded", "rejected", "accepted"]
    metrics_dict = {"Total Applications": metrics["applications_total"]}
    metrics_dict.update({k.title(): status_counts.get(k, 0) for k in status_order[1:]})

    cols = st.columns(len(metrics_dict))
    for col, (label, val) in zip(cols, metrics_dict.items()):
        col.metric(label, val)

    st.markdown("---")

    status_counts = metrics["applications_by_status"]
    df_chart = pd.DataFrame({
        "Status": list(status_counts.keys()),
        "Count": list(status_counts.values())
    })
    df_chart["Count"] = df_chart["Count"].astype(int)

    st.subheader("Applications by Status")
    chart = alt.Chart(df_chart).mark_bar().encode(
        x=alt.X('Status', sort=None),
        y='Count',
        color='Status'
    )
    st.altair_chart(chart, use_container_width=True)

    st.markdown("---")
    st.header("📜 Application Timeline Viewer")

    apps = fetch_apps(st.session_state.token)  # Reuse your fetch_apps to get all user's applications
    if apps:
        # Nice selector labels -- company + role, fallback to ID if missing name
        app_options = [
            {"id": app["id"], "label": f"{app['company_name']} – {app['role_title']}"}
            for app in apps
        ]
        app_labels = [a["label"] for a in app_options]
        app_ids = [a["id"] for a in app_options]

        selected_idx = st.selectbox("Select an application to view timeline", range(len(app_labels)), format_func=lambda i: app_labels[i], key="metrics_timeline_app")

        selected_app_id = app_ids[selected_idx]
        app_info = next((a for a in apps if a["id"] == selected_app_id), None)


        timeline = fetch_app_timeline(selected_app_id, st.session_state.token)
        st.subheader(f"Timeline for {app_labels[selected_idx]}")

        # Always show creation date first!
        if app_info and "applied_date" in app_info:
            applied_str = pd.to_datetime(app_info["applied_date"]).strftime("%Y-%m-%d %H:%M UTC")
            st.markdown(f"- 📄 **Application created on:** {applied_str}")

        if not timeline or len(timeline) == 0:
            st.caption("No timeline events yet.")
        else:
            for event in timeline:
                time_str = pd.to_datetime(event["event_time"]).strftime("%Y-%m-%d %H:%M UTC") 

                old_status = event.get("old_status", "").replace("-", " ").title()
                new_status = event.get("new_status", "").replace("-", " ").title() 
                status_change = f"{old_status} → {new_status}" if old_status and new_status else ""

                notes = event.get("notes", "")

                if notes and "automation" in notes.lower():
                    status_change += f" by automation"

                main_msg = status_change if status_change else notes
                
                st.markdown(
                    f"- {main_msg}  \n"
                    f"  <small style='color:gray;'>{time_str}</small>",
                    unsafe_allow_html=True,
                )



        st.markdown("---")
        df = pd.DataFrame(apps)

        # --- EXPORT TO CSV BUTTON ---
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export All Applications to CSV",
            data=csv,
            file_name="applications.csv",
            mime='text/csv'
        )
    else:
        st.info("You don’t have any applications yet.")

elif option == "Settings":
    st.header("Settings")
    st.info("Configure your preferences.")
    # TODO: Add settings management
    




# Footer
st.markdown("---")
st.caption("Built with Streamlit • AppTrackr © 2025")
