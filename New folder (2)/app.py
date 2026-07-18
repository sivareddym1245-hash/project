import requests
import streamlit as st

st.set_page_config(page_title="Persistent Agent Hub", layout="wide")
BACKEND_URL = "http://127.0.0.1:8000"

workspace = st.sidebar.selectbox("Choose Module", ["🌍 AI Trip Planner", "💻 Coding Assistant"])


def call_backend(method: str, path: str, payload=None):
    try:
        if method == "GET":
            return requests.get(f"{BACKEND_URL}{path}", timeout=30)
        return requests.post(f"{BACKEND_URL}{path}", json=payload, timeout=60)
    except requests.exceptions.RequestException as exc:
        st.error(f"Unable to reach backend at {BACKEND_URL}: {exc}")
        st.stop()


if workspace == "🌍 AI Trip Planner":
    st.title("🌍 AI Trip Planner with History")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Plan a New Journey")
        destination = st.text_input("Destination", "Tokyo, Japan")
        days = st.number_input("Days", min_value=1, max_value=14, value=5)

        if st.button("Build Itinerary"):
            with st.spinner("Generating itinerary..."):
                res = call_backend("POST", "/api/trip/generate", {"destination": destination, "days": int(days)})
                if res.status_code == 200:
                    st.success("Plan generated and saved!")
                    st.write(res.json()["itinerary"])
                else:
                    st.error("Failed to generate plan from the backend.")

    with col2:
        st.subheader("📚 Saved Trip History")
        history_res = call_backend("GET", "/api/trip/history")
        if history_res.status_code == 200:
            past_trips = history_res.json()
            if not past_trips:
                st.info("No saved trip plans yet.")
            for trip in past_trips:
                with st.expander(f"{trip['destination']} ({trip['days']} Days)"):
                    st.caption(f"Planned on: {trip['date'][:10]}")
                    st.text(trip["itinerary"])
        else:
            st.error("Unable to load trip history.")

elif workspace == "💻 Coding Assistant":
    st.title("💻 Coding Assistant & History Logger")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Code Utility Node")
        task = st.selectbox("Task Profile", ["Explain", "Debug", "Convert", "Unit Test", "Optimize"])
        code = st.text_area("Input Code Snippet", height=180)
        context = st.text_input("Extra Specifications")

        if st.button("Process Code"):
            with st.spinner("Processing code task..."):
                res = call_backend("POST", "/api/code/execute", {"task": task, "code": code, "context": context})
                if res.status_code == 200:
                    st.success("Task completed successfully!")
                    st.markdown(res.json()["result"])
                else:
                    st.error("Error communicating with the AI engine.")

    with col2:
        st.subheader("⏳ Session History Log")
        history_res = call_backend("GET", "/api/code/history")
        if history_res.status_code == 200:
            past_tasks = history_res.json()
            if not past_tasks:
                st.info("No coding sessions recorded yet.")
            for task_item in past_tasks:
                with st.expander(f"Task: {task_item['task']} ({task_item['date'][:10]})"):
                    st.code(task_item["code"][:150] + "...", language="python")
                    st.markdown("**AI Response Preview:**")
                    st.write(task_item["result"][:300] + "...")
        else:
            st.error("Unable to load coding history.")
