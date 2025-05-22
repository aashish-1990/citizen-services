# LIA – Agentic AI Architecture (CrewAI-style) with FastAPI + Session Memory

from typing import Dict, Optional, List
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# === Session Memory ===
session_memory: Dict[str, List[str]] = {}

# === FastAPI App ===
app = FastAPI()

# Enable CORS for frontend integration (React/Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Data Models ===
class ChatRequest(BaseModel):
    user_input: str
    context: Optional[Dict] = {}
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    memory: List[str]

# === Agent Definitions ===
class BaseAgent:
    def __init__(self, name: str):
        self.name = name

    def handle(self, input_text: str, context: dict) -> str:
        raise NotImplementedError

class IntentAgent(BaseAgent):
    def __init__(self):
        super().__init__("Intent Agent")

    def handle(self, input_text: str, context: dict) -> str:
        text = input_text.lower()
        if "bill" in text and ("pay" in text or "check" in text):
            return "pay_bill"
        elif "ticket" in text:
            return "pay_ticket"
        elif "permit" in text:
            return "apply_permit"
        elif "report" in text:
            return "report_issue"
        else:
            return "unknown"

class BillAgent(BaseAgent):
    def __init__(self):
        super().__init__("Bill Agent")

    def handle(self, input_text: str, context: dict) -> str:
        address = context.get("address")
        if not address:
            return "Please provide your address to look up the bill."
        if "olive" in address.lower():
            return f"Bill for {address}: $82.35. Would you like to proceed with payment?"
        return f"No bill found for {address}."

class TicketAgent(BaseAgent):
    def __init__(self):
        super().__init__("Ticket Agent")

    def handle(self, input_text: str, context: dict) -> str:
        ticket_id = context.get("ticket_id")
        if not ticket_id:
            return "Please provide your ticket number."
        if ticket_id == "123":
            return "Ticket 123 found. Fine: $45.00. Would you like to pay now?"
        return "Ticket not found."

class PermitAgent(BaseAgent):
    def __init__(self):
        super().__init__("Permit Agent")

    def handle(self, input_text: str, context: dict) -> str:
        permit_type = context.get("permit_type")
        location = context.get("location")
        if not permit_type or not location:
            return "Please provide both permit type and location."
        return f"Your {permit_type} permit application for {location} has been submitted."

# === Orchestrator Agent ===
class LIAOrchestrator:
    def __init__(self):
        self.intent_agent = IntentAgent()
        self.agents = {
            "pay_bill": BillAgent(),
            "pay_ticket": TicketAgent(),
            "apply_permit": PermitAgent()
        }

    def run(self, user_input: str, context: dict = {}) -> str:
        intent = self.intent_agent.handle(user_input, context)
        agent = self.agents.get(intent)
        if agent:
            return agent.handle(user_input, context)
        return "I'm not sure how to help with that. Please try again."

lia_core = LIAOrchestrator()

# === FastAPI Route ===
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    session_id = request.session_id or "default"
    response = lia_core.run(request.user_input, request.context or {})

    # Update session memory
    if session_id not in session_memory:
        session_memory[session_id] = []
    session_memory[session_id].append(f"User: {request.user_input}")
    session_memory[session_id].append(f"LIA: {response}")

    return ChatResponse(response=response, memory=session_memory[session_id])

# === Run the server (for local dev) ===
# if __name__ == "__main__":
#     uvicorn.run("lia_agent_architecture:app", host="0.0.0.0", port=8000, reload=True)
