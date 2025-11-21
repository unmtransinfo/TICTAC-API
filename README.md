# TICTAC API
FastAPI backend for the TICTAC analytics platform.  
Currently in the initial development phase.

---

## Initial Setup (Development Environment)

### **1. Install Python 3.12**
Make sure your system has Python 3.12 installed

## 2. Create Virtual Environment
Inside the project directory:
`python3.12 -m venv .venv`
`source .venv/bin/activate`

## 3. Install Dependencies
`pip install --upgrade pip`
`pip install -r requirements.txt`

## 4. Run the API
`uvicorn app.main:app --reload`

API will run at:

http://127.0.0.1:8000


Interactive Docs (Swagger):

http://127.0.0.1:8000/docs