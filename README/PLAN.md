# Project Milestones – apptrackr

## Day 0: Prep  
- [.] Create project folder structure  
- [.] Add .gitignore to root  
- [.] Add LICENSE (MIT) to root  
- [.] Add README.md with summary and tech stack  
- [.] Add backend/requirements.txt and frontend/requirements.txt  
- [.] Add README/PLAN.md with milestones  

## Days 1–2: Data Models & Database  
**Day 1**  
- [.] Implement User and Application models in backend/models.py  
- [.] Set up backend/db.py for DB engine and table creation  
- [.] Create database initialization function (create_db)  

**Day 2**  
- [.] Write script to initialize SQLite database  
- [.] Create seed/demo data generator  
- [.] Write unit tests for model creation (pytest)  

## Days 3–5: Auth & API (FastAPI)  
**Day 3**  
- [.] Implement POST /signup with password hashing  
- [.] Implement POST /login returning JWT token  

**Day 4**  
- [.] Add token dependency to get current user  
- [.] Implement GET /apps (filter by user) and POST /apps (create)  

**Day 5**  
- [.] Implement PUT /apps/{id} and DELETE /apps/{id}  
- [.] Write unit tests for API endpoints  

## Days 6–8: Frontend Core (Streamlit)  
**Day 6**  
- [.] Scaffold Streamlit app (frontend/streamlit_app.py)  
- [.] Implement login/signup UI with backend integration  

**Day 7**  
- [.] Build Applications List view (fetch GET /apps, show table)  
- [.] Add filter tabs and status chips  

**Day 8**  
- [.] Implement Add Application form, Edit modal, Delete action  
- [.] Ensure instant UI refresh after CRUD actions  

## Days 9–11: Automation & Notifications  
**Day 9**  
- [.] Implement follow-up logic function (check_followups) in backend  
- [.] Add POST /cron/check-followups endpoint  

**Day 10**  
- [ ] Integrate APScheduler for periodic automation  
- [ ] Add logging and last_run timestamp tracking  

**Day 11**  
- [ ] Frontend: add dashboard notification banner/bell  
- [ ] Implement button to manually run automation  
- [ ] Write automation unit tests (simulate date/status transitions)  

## Days 12–13: Analytics & Export  
**Day 12**  
- [ ] Implement backend GET /metrics endpoint  
- [ ] Add tags field and filtering to Application model  
- [ ] Add timeline/status change tracking for apps  

**Day 13**  
- [ ] Frontend: show metrics dashboard and charts  
- [ ] Detail view: show application timeline  
- [ ] Implement export to CSV  
- [ ] Write unit tests for metrics and exporting  

## Days 14–15: Demo, Docs, Deployment  
**Day 14**  
- [ ] Implement public demo mode (demo dataset, read-only)  
- [ ] Validate session persistence with Streamlit  

**Day 15**  
- [ ] Update README.md with install and run instructions  
- [ ] Add screenshots, features, CV section  
- [ ] Deploy backend (Render/Railway) and frontend (Streamlit Cloud)  
- [ ] Smoke test live demo and fix deployment issues  



Setup github action workflow day 9 
