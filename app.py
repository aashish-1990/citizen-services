# main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import time

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class ChatRequest(BaseModel):
    message: str

# Intent memory (in-memory session simulation)
session = {
    "intent": None,
    "step": 0,
    "context": {}
}

@app.get("/", response_class=HTMLResponse)
def serve_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
def chat(request: ChatRequest):
    user_input = request.message.lower().strip()
    response = ""

    if session["step"] == 0:
        if "bill" in user_input:
            session["intent"] = "pay_bill"
            session["step"] = 1
            response = "Sure, please share your address."
        elif "permit" in user_input:
            session["intent"] = "apply_permit"
            session["step"] = 1
            response = "What type of permit are you applying for?"
        elif "ticket" in user_input:
            session["intent"] = "pay_ticket"
            session["step"] = 1
            response = "Please share your ticket number."
        elif "report" in user_input:
            session["intent"] = "report_issue"
            session["step"] = 1
            response = "What issue would you like to report?"
        else:
            response = "I didn’t catch that. You can say things like 'I want to pay my bill'."

    elif session["step"] == 1:
        if session["intent"] == "pay_bill":
            session["context"]["address"] = user_input
            if any(x in user_input for x in ["123", "main", "olive", "pine"]):
                session["step"] = 2
                response = f"Found a bill for $82.35 at {user_input}. Is this correct? (yes/no)"
            else:
                response = f"No bill found for {user_input}. Try again."
        elif session["intent"] == "apply_permit":
            session["context"]["permit_type"] = user_input
            session["step"] = 2
            response = "Please enter the address for the permit."
        elif session["intent"] == "pay_ticket":
            session["context"]["ticket"] = user_input
            session["step"] = 2
            response = f"Ticket {user_input} found with fine $45.00. Do you want to pay it? (yes/no)"
        elif session["intent"] == "report_issue":
            session["context"]["issue"] = user_input
            session["step"] = 2
            response = "Please provide the location of this issue."

    elif session["step"] == 2:
        if session["intent"] == "pay_bill":
            if "yes" in user_input:
                time.sleep(1)
                session["step"] = 3
                response = "✅ Payment confirmed! Would you like to download the receipt or pay another bill?"
            else:
                session["step"] = 1
                response = "Okay, please enter your address again."
        elif session["intent"] == "apply_permit":
            session["context"]["address"] = user_input
            session["step"] = 0
            response = f"✅ Permit application for {session['context']['permit_type']} at {user_input} submitted."
        elif session["intent"] == "pay_ticket":
            if "yes" in user_input:
                time.sleep(1)
                session["step"] = 0
                response = "✅ Ticket paid successfully. Anything else I can help with?"
            else:
                session["step"] = 0
                response = "Okay, ticket payment cancelled."
        elif session["intent"] == "report_issue":
            session["context"]["location"] = user_input
            session["step"] = 0
            response = f"🛠 Issue at {user_input} reported. Our team will look into it."

    return JSONResponse(content={"reply": response})
