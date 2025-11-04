# AppTrackr

Python-powered job application tracker  
Track, manage, and visualize your job search with ease.

## 🚀 Features
- Add, view, edit, and delete job applications
- Organize by company, role, city, country, status, follow-up, and notes
- Dashboard: All your applications, filter by status
- Charts & Metrics: Real-time charts of your progress
- Timeline: See every status change, follow-up, and event for each application
- Automatic notifications: Get reminders for follow-ups
- CSV export: Download your application data anytime
- Modern, responsive interface with Streamlit

## 🛠️ Tech Stack
- Backend: FastAPI & SQLModel (typed ORM, SQLite DB)
- Frontend: Streamlit (Python UI toolkit)
- Authentication: Secure JWT-based login/signup

## 📦 Installation

1. Clone the repo:
git clone https://github.com/yourname/apptrackr.git
cd apptrackr


2. Install dependencies:
pip install -r requirements.txt


3. Run the backend:
uvicorn backend.main:app --reload


4. Start the frontend:
streamlit run frontend/streamlit_app.py


Open [http://localhost:8501](http://localhost:8501/) in your browser.

## 🎬 Usage
- Sign up or log in
- Add your first job application
- Track status, update follow-ups, add notes
- See stats in the Metrics tab
- Export your data to CSV anytime

## 📄 License
MIT license — free for personal or commercial use.

## 💡 Credits
Built & maintained by Dev Phadke (Pracind).  
Powered by FastAPI, SQLModel, and Streamlit.

