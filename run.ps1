# Activate virtual environment
& .\.venv\Scripts\Activate.ps1

# Start backend (FastAPI) in background
Start-Process powershell -ArgumentList "uvicorn backend.main:app --reload"

# Wait to ensure backend is running
Start-Sleep -Seconds 2

# Start user portal (Streamlit) in new tab
Start-Process powershell -ArgumentList "cd frontend; streamlit run user_portal.py"

# Start admin panel (Streamlit) in new tab
Start-Process powershell -ArgumentList "cd frontend; streamlit run admin_panel.py"
