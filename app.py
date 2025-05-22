# LIA – Agentic AI Architecture (CrewAI-style) with FastAPI + Session Memory + Logs

from typing import Dict, Optional, List
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging

# === Logging Setup ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lia_agent")

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
        logger.info(f"[IntentAgent] Input: {input_text}")
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
        address = context.get("address", input_text)
        logger.info(f"[BillAgent] Address: {address}")
        if any(x in address.lower() for x in ["olive", "main", "pine", "123"]):
            return f"Bill for {address}: $82.35. ✅ Do you want to proceed with payment?"
        return f"❌ No bill found for {address}"

class TicketAgent(BaseAgent):
    def __init__(self):
        super().__init__("Ticket Agent")

    def handle(self, input_text: str, context: dict) -> str:
        ticket_id = context.get("ticket_id", input_text)
        logger.info(f"[TicketAgent] Ticket ID: {ticket_id}")
        if ticket_id == "123":
            return "Ticket 123 found. Fine: $45.00. Would you like to pay now?"
        return "❌ Ticket not found."

class PermitAgent(BaseAgent):
    def __init__(self):
        super().__init__("Permit Agent")

    def handle(self, input_text: str, context: dict) -> str:
        permit_type = context.get("permit_type")
        location = context.get("location")
        logger.info(f"[PermitAgent] Type: {permit_type}, Location: {location}")
        if not permit_type or not location:
            return "Please provide both permit type and location."
        return f"📝 Your {permit_type} permit for {location} has been submitted."

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
        logger.info(f"[LIAOrchestrator] Input: {user_input} | Context: {context}")
        intent = self.intent_agent.handle(user_input, context)
        logger.info(f"[LIAOrchestrator] Intent: {intent}")
        agent = self.agents.get(intent)
        if agent:
            return agent.handle(user_input, context)
        return (
            "I didn’t quite catch that. You can ask me to pay a bill, pay a ticket, "
            "apply for a permit, or report an issue."
        )

lia_core = LIAOrchestrator()

# === FastAPI Route ===
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    session_id = request.session_id or "default"
    logger.info(f"[API] Session ID: {session_id}")
    response = lia_core.run(request.user_input, request.context or {})

    # Update session memory
    if session_id not in session_memory:
        session_memory[session_id] = []
    session_memory[session_id].append(f"🟢 You: {request.user_input}")
    session_memory[session_id].append(f"🟣 LIA: {response}")

    logger.info(f"[API] Memory for {session_id}: {session_memory[session_id]}")
    return ChatResponse(response=response, memory=session_memory[session_id])
