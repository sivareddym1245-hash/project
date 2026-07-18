# Dual Agent Workspace

This workspace contains a lightweight Python application with:

- A FastAPI backend exposing trip-planning and coding-assistant endpoints
- SQLite persistence for saved trip plans and coding history
- A Streamlit frontend with two modules: trip planning and coding assistant

## Files

- [main.py](main.py) — FastAPI backend routes and AI prompt handling
- [database.py](database.py) — SQLite initialization and persistence helpers
- [app.py](app.py) — Streamlit UI for the two modules
- [requirements.txt](requirements.txt) — Python package dependencies
- [.env.example](.env.example) — sample environment variable file

## Run locally

1. Install dependencies:
   ```bash
   C:/Python313/python.exe -m pip install -r requirements.txt
   ```
2. Start the backend:
   ```bash
   C:/Python313/python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
   ```
3. Start the frontend in a second terminal:
   ```bash
   C:/Python313/python.exe -m streamlit run app.py --server.headless true --server.address 127.0.0.1 --server.port 8501
   ```

## Notes

- Set OPENAI_API_KEY in your environment or .env to enable live AI responses.
- If no key is present, the app will return a fallback message while still saving history locally.
