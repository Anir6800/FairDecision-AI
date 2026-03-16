# FairDecision AI

Project stack: FastAPI backend, React frontend, MongoDB database, LM Studio as local AI engine.

## Setup

1. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

2. **Backend**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

3. **Database**:
   ```bash
   docker-compose up -d
   ```
