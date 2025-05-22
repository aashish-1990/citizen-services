from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List, Optional
from fastapi.middleware.cors import CORSMiddleware
import logging
import time

app = FastAPI()

# === CORS for frontend integration ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Logging Setup ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lia")

# === Memory per session ===
memory: Dict[str, List[str]] = {}
session_state: Dict[str, Dict] = {}

# === Request/Response Models ===
class ChatRequest(BaseModel):
    user_input: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    memory: List[str]

# === Intent Detection ===
def detect_intent(text: str) -> str:
    text = text.lower()
    if "bill" in text and "pay" in text:
        return "pay_bill"
    elif "ticket" in text:
        return "pay_ticket"
    elif "permit" in text:
        return "apply_permit"
    elif "report" in text or "leak" in text:
        return "report_issue"
    elif text in ["yes", "no"]:
        return "confirm"
    else:
        return "unknown"

# === Chat Engine ===
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    session_id = req.session_id
    user_input = req.user_input.strip()
    logger.info(f"[{session_id}] User: {user_input}")

    if session_id not in memory:
        memory[session_id] = []
        session_state[session_id] = {
            "step": 0,
            "intent": None,
            "context": {}
        }

    mem = memory[session_id]
    state = session_state[session_id]
    step = state["step"]
    intent = state["intent"]
    ctx = state["context"]

    mem.append(f"🟢 You: {user_input}")

    # Step 0 - Detect Intent
    if step == 0:
        intent = detect_intent(user_input)
        state["intent"] = intent

        if intent == "pay_bill":
            response = "Sure! Please share your address."
            state["step"] = 1

        elif intent == "pay_ticket":
            response = "Please provide your ticket number."
            state["step"] = 1

        elif intent == "apply_permit":
            response = "What type of permit would you like to apply for?"
            state["step"] = 1

        elif intent == "report_issue":
            response = "What issue would you like to report?"
            state["step"] = 1

        else:
            response = "I didn’t catch that. You can say 'I want to pay my bill' or 'report a water leak'."

    # Step 1 - Collect Input
    elif step == 1:
        if intent == "pay_bill":
            ctx["address"] = user_input
            response = f"Found a bill for $82.35 at {user_input}. Is this correct?"
            state["step"] = 2

        elif intent == "pay_ticket":
            ctx["ticket_id"] = user_input
            response = f"Ticket {user_input} has a fine of $45. Proceed with payment? (yes/no)"
            state["step"] = 2

        elif intent == "apply_permit":
            ctx["permit_type"] = user_input
            response = "What is the address for this permit?"
            state["step"] = 2

        elif intent == "report_issue":
            ctx["issue"] = user_input
            response = "Please share the location of the issue."
            state["step"] = 2

    # Step 2 - Confirm
    elif step == 2:
        if intent == "pay_bill":
            if user_input.lower() == "yes":
                response = "Please check your SMS/email for the payment link..."
                time.sleep(1)
                response += "\n✅ Your payment has been received. Would you like to download the receipt or do something else?"
                state["step"] = 3
            else:
                response = "Okay, what is your address again?"
                state["step"] = 1

        elif intent == "pay_ticket":
            if user_input.lower() == "yes":
                response = "Payment link sent. ✅ Ticket paid. Do you want to pay another ticket?"
                state["step"] = 3
            else:
                response = "Okay. Ticket not paid."
                state["step"] = 0

        elif intent == "apply_permit":
            ctx["address"] = user_input
            response = f"Your {ctx['permit_type']} permit request for {ctx['address']} has been submitted. ✅"
            state["step"] = 3

        elif intent == "report_issue":
            ctx["location"] = user_input
            response = f"Issue reported at {ctx['location']} – our team will investigate. ✅"
            state["step"] = 3

    # Step 3 - Wrap Up
    elif step == 3:
        if "yes" in user_input.lower():
            response = "Awesome! What would you like to do next?"
            state["step"] = 0
        else:
            response = "Thank you for using LIA. Goodbye!"
            state["step"] = 0

    else:
        response = "Something went wrong. Let’s restart. How can I help you today?"
        state["step"] = 0

    mem.append(f"🟣 LIA: {response}")
    return ChatResponse(response=response, memory=mem)
