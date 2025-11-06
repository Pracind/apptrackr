# AppTrackr

Python-powered job application tracker  
Track, manage, and visualize your job search with ease.

## 🚀 Features
- **Add, view, edit, and delete job applications**
- **Organize** applications by company, role, city, country, status, follow-up, and notes
- **Dashboard**: View all your applications and filter by status
- **Charts & Metrics**: Real-time charts and statistics of your progress
- **Timeline Viewer**: See every status change, follow-up, and event for each application
- **Automatic notifications**: Get reminders for pending follow-ups and status changes
- **CSV export**: Download your complete application data anytime
- **Modern, responsive interface** built with Streamlit
- **Authentication**: Secure JWT login & signup with validation
- **Profile Settings**: Edit your name, email, and password (with validation)
- **Account Deletion**: Permanently delete your account and all associated data
- **Logout**: Instantly log out from your session

## 🌐 Live Demo
Try AppTrackr online: [http://apptrackr.ddns.net/](http://apptrackr.ddns.net/)  
Accessible and free — no setup required!

## 🛠️ Tech Stack
- **Backend**: FastAPI & SQLModel (typed ORM, SQLite DB)
- **Frontend**: Streamlit (Python UI toolkit)
- **Authentication**: Secure JWT-based login/signup

## 📦 Installation

1. **Clone the repo:**
    ```
    git clone https://github.com/yourname/apptrackr.git
    cd apptrackr
    ```

2. **Install dependencies:**
    ```
    pip install -r requirements.txt
    ```

3. **Run the backend:**
    ```
    uvicorn backend.main:app --reload
    ```

4. **Start the frontend:**
    ```
    streamlit run frontend/streamlit_app.py
    ```

    Open [http://localhost:8501](http://localhost:8501/) in your browser.

## 🎬 Usage
- Sign up or log in
- Add your first job application
- Track statuses, update follow-ups, add notes
- View statistics in the Metrics tab
- Export your data to CSV anytime
- Edit account details and delete your account if needed

## 📄 License
MIT license — free for personal or commercial use.

## 💡 Credits
Built & maintained by Dev Phadke (Pracind).  
Powered by FastAPI, SQLModel, and Streamlit.
