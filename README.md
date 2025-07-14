# ✨ Smartflow

**Smartflow** is a modern, natural-language-driven workflow engine for airline ticketing and travel management. It lets users and admins control complex booking workflows using plain English commands, powered by advanced AI and a modular backend.

---

## 🚀 What is Smartflow?

Smartflow allows both travelers and administrators to interact with a flight booking system using natural language. Admins can change business rules (like discounts, required steps, or tool substitutions) just by typing instructions in English. Travelers can book, reschedule, or manage tickets through a user-friendly portal.

---

## 🛠️ Modern Tools & Technologies

- **FastAPI**: High-performance Python web framework for the backend API.
- **Cohere LLM**: State-of-the-art language model for understanding and structuring user/admin commands.
- **Streamlit**: Modern, interactive web UI for both the user portal and admin panel.
- **Pydantic**: Data validation and settings management using Python type hints.
- **Uvicorn**: Lightning-fast ASGI server for running FastAPI.
- **HTTPX**: Async HTTP client for robust backend communication.
- **Python 3.10+**: Modern Python features and type safety.
- **LangChain-style architecture**: Modular, composable workflow steps inspired by the LangChain ecosystem.

---

## 🧩 How Does It Work?

1. **Natural Language Input**: Users or admins type commands in plain English.
2. **AI Understanding**: Cohere LLM interprets the command and converts it into structured JSON (intents, rules, actions).
3. **Dynamic Workflow Engine**: The backend executes the workflow, applying business rules (like skipping steps, forcing actions, or applying discounts).
4. **Modular APIs**: Each workflow step (book ticket, payment, email, etc.) is a separate API module, making the system easy to extend.
5. **Live Admin Control**: Admins can update business rules instantly—no code changes required.

---

## 🖥️ Project Structure

```
Smartflow/
  backend/
    apis/         # Modular API endpoints (booking, payment, etc.)
    services/     # LLM integration, workflow manager
    utils/        # Business rules, models, DB mock
    main.py       # FastAPI app entrypoint
  frontend/
    user_portal.py   # Streamlit app for travelers
    admin_panel.py   # Streamlit app for admins
  business_rules.json # Stores current business rules
  requirements.txt    # Python dependencies
  run.ps1             # Script to launch everything on Windows
```

---

## 👩‍💻 Getting Started

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd Smartflow
python -m venv .venv
# Activate your virtual environment, then:
pip install -r requirements.txt
```

### 2. Set Up Cohere API Key

Get a free API key from [Cohere](https://cohere.com/).  
Set it as an environment variable:

**On Windows (PowerShell):**
```powershell
$env:CO_API_KEY="your_cohere_api_key_here"
```

**On Mac/Linux:**
```bash
export CO_API_KEY=your_cohere_api_key_here
```

### 3. Run Everything

**On Windows:**
```powershell
./run.ps1
```

**Manually:**
- Start backend:  
  `cd backend && uvicorn main:app --reload`
- Start user portal:  
  `cd frontend && streamlit run user_portal.py`
- Start admin panel:  
  `cd frontend && streamlit run admin_panel.py`

---

## 🏷️ Features

- **Book, search, and manage flights** with a simple UI.
- **Admin panel** for live business rule updates (skip steps, force actions, apply discounts, etc.).
- **Dynamic workflow execution**—no code changes needed for new rules.
- **LLM-powered intent extraction** for robust natural language understanding.
- **Extensible API design**—add new tools or steps easily.

---

## 🤖 Example Admin Commands

- “Skip the payment step for all bookings.”
- “Apply a 20% discount until the end of the month.”
- “Always send a confirmation email.”
- “Remove all current rules and disable discounts.”

---

## 📦 Requirements

- Python 3.10.11+
- See `requirements.txt` for all dependencies.

---

## ❤️ Contributing

Pull requests and suggestions are welcome!  
Feel free to open issues for bugs or feature requests.

---
