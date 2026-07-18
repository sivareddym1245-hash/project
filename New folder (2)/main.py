import os

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

import database as db

load_dotenv()

app = FastAPI(title="Dual Agent Backend API")
db.init_db()


class TripRequest(BaseModel):
    destination: str
    days: int


class CodeRequest(BaseModel):
    task: str
    code: str
    context: str = ""


def get_llm():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.2,
            api_key=api_key,
        )
    except Exception:
        return None


llm = get_llm()


def build_fallback_trip_itinerary(destination: str, days: int) -> str:
    destination_name = destination.strip() or "your destination"
    label = "day" if days == 1 else "days"
    lines = [
        f"Fallback itinerary for {destination_name} ({days} {label}):",
        "",
    ]
    for day in range(1, days + 1):
        lines.append(f"Day {day}:")
        lines.append("- Morning: Start with a central landmark or local market visit.")
        lines.append("- Afternoon: Add a culture-focused stop or scenic walk.")
        lines.append("- Evening: Enjoy a relaxed dinner and a neighborhood stroll.")
        lines.append("")
    lines.append("Estimated daily budget: $90-$150 per person, excluding flights.")
    return "\n".join(lines)


def build_fallback_code_response(task: str, code: str, context: str) -> str:
    preview = code.strip().splitlines()[0] if code.strip() else "your code snippet"
    return (
        f"Fallback response for task '{task}'.\n\n"
        f"Preview: {preview}\n\n"
        "Suggested next steps:\n"
        "- Review the snippet structure and identify the main function or class.\n"
        "- Check imports, indentation, and obvious syntax issues first.\n"
        "- Add comments or docstrings if the intent is not clear."
        f"\nContext: {context or 'No additional context provided.'}"
    )


def build_prompt_response(prompt: str) -> str:
    if llm is None:
        return (
            "OpenAI API key is not configured. Set OPENAI_API_KEY in your environment to use the AI engine. "
            "The app will still save your requests locally in SQLite."
        )

    try:
        response = llm.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)
    except Exception as exc:
        return f"LLM request failed: {exc}"


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/api/trip/generate")
async def generate_trip(req: TripRequest) -> dict:
    prompt = (
        f"Create a detailed {req.days}-day travel itinerary for {req.destination} with morning, afternoon, and "
        f"evening activities, daily budget estimates, and 3 local food suggestions."
    )
    itinerary_text = build_prompt_response(prompt)
    if itinerary_text.startswith("OpenAI API key is not configured") or itinerary_text.startswith("LLM request failed"):
        itinerary_text = build_fallback_trip_itinerary(req.destination, req.days)
    db.save_trip(req.destination, req.days, itinerary_text)
    return {"itinerary": itinerary_text}


@app.get("/api/trip/history")
async def get_trip_history() -> list[dict]:
    trips = db.get_all_trips()
    return [
        {"destination": item[0], "days": item[1], "itinerary": item[2], "date": item[3]}
        for item in trips
    ]


@app.post("/api/code/execute")
async def execute_code_task(req: CodeRequest) -> dict:
    prompt = (
        f"Act as an expert software engineer. Execute task '{req.task}' on this code snippet.\n\n"
        f"Code:\n{req.code}\n\nContext: {req.context}"
    )
    ai_text = build_prompt_response(prompt)
    if ai_text.startswith("OpenAI API key is not configured") or ai_text.startswith("LLM request failed"):
        ai_text = build_fallback_code_response(req.task, req.code, req.context)
    db.save_coding_task(req.task, req.code, ai_text)
    return {"result": ai_text}


@app.get("/api/code/history")
async def get_code_history() -> list[dict]:
    history = db.get_coding_history()
    return [
        {"task": item[0], "code": item[1], "result": item[2], "date": item[3]}
        for item in history
    ]
