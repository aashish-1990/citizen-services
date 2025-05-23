# main.py - LIA Conversational AI Agent for Gov2Biz
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import time
import uuid
import logging
from typing import Dict, Optional, List
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LIA - Gov2Biz Conversational AI",
    description="AI Assistant for City Services",
    version="1.0.0"
)

# CORS middleware for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception:
    # Static directory might not exist in demo
    pass

templates = Jinja2Templates(directory="templates")

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "demo-key")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    session_id: str
    intent: Optional[str] = None
    needs_escalation: bool = False
    options: Optional[List[str]] = None
    auto_continue_delay: Optional[int] = None  # Milliseconds to wait before auto-continuing

# User sessions storage (use Redis/database in production)
user_sessions: Dict[str, Dict] = {}

# Mock data for demonstration - In production, replace with real database calls
MOCK_BILLS = {
    "123 main st": {
        "amount": 82.35, 
        "type": "water", 
        "due_date": "2025-06-15",
        "account": "WAT-001234"
    },
    "456 olive ave": {
        "amount": 156.20, 
        "type": "electricity", 
        "due_date": "2025-06-10",
        "account": "ELE-005678"
    },
    "789 pine rd": {
        "amount": 45.80, 
        "type": "gas", 
        "due_date": "2025-06-20",
        "account": "GAS-009876"
    },
    "101 oak street": {
        "amount": 234.50, 
        "type": "water", 
        "due_date": "2025-06-18",
        "account": "WAT-001122"
    }
}

MOCK_TICKETS = {
    "TK001": {"amount": 45.00, "type": "parking", "location": "Main St", "date": "2025-05-15"},
    "TK002": {"amount": 125.00, "type": "speeding", "location": "Highway 101", "date": "2025-05-20"},
    "PK2025001": {"amount": 35.00, "type": "parking meter", "location": "Downtown", "date": "2025-05-22"}
}

# Mock data for demonstration - In production, replace with real database calls
MOCK_BILLS = {
    "123 main st": {
        "amount": 82.35, 
        "type": "water", 
        "due_date": "2025-06-15",
        "account": "WAT-001234"
    },
    "456 olive ave": {
        "amount": 156.20, 
        "type": "electricity", 
        "due_date": "2025-06-10",
        "account": "ELE-005678"
    },
    "789 pine rd": {
        "amount": 45.80, 
        "type": "gas", 
        "due_date": "2025-06-20",
        "account": "GAS-009876"
    },
    "101 oak street": {
        "amount": 234.50, 
        "type": "water", 
        "due_date": "2025-06-18",
        "account": "WAT-001122"
    }
}

MOCK_TICKETS = {
    "TK001": {"amount": 45.00, "type": "parking", "location": "Main St", "date": "2025-05-15"},
    "TK002": {"amount": 125.00, "type": "speeding", "location": "Highway 101", "date": "2025-05-20"},
    "PK2025001": {"amount": 35.00, "type": "parking meter", "location": "Downtown", "date": "2025-05-22"}
}

# Enhanced garage sales permit tracking system
GARAGE_SALE_PERMITS = {
    # Track permits by address and year for annual limit enforcement
    "123 pine street": [
        {"permit_id": "GSP-2025-045", "date": "2025-04-15", "duration": 1, "status": "approved", "year": 2025},
    ],
    "456 oak avenue": [
        {"permit_id": "GSP-2025-023", "date": "2025-03-10", "duration": 2, "status": "approved", "year": 2025},
        {"permit_id": "GSP-2025-031", "date": "2025-04-20", "duration": 1, "status": "approved", "year": 2025},
    ]
}

MOCK_APPLICATIONS = {
    "APP001": {"type": "construction permit", "status": "pending review", "address": "123 Main St", "submitted": "2025-05-10"},
    "APP002": {"type": "business license", "status": "under review", "address": "456 Oak Ave", "submitted": "2025-05-18"},
    "GSP-2025-045": {"type": "garage sale permit", "status": "approved", "address": "123 Pine Street", "submitted": "2025-04-10", "date": "2025-04-15", "duration": "1 day"},
    "GSP-2025-023": {"type": "garage sale permit", "status": "approved", "address": "456 Oak Avenue", "submitted": "2025-03-05", "date": "2025-03-10", "duration": "2 days"},
}

# City of Kermit boundaries (mock data for address validation)
CITY_BOUNDARIES = [
    "main st", "main street", "pine st", "pine street", "oak ave", "oak avenue", 
    "elm street", "elm st", "maple avenue", "maple ave", "cedar lane", "cedar ln", 
    "birch road", "birch rd", "willow drive", "willow dr", "commerce st", "commerce street",
    "downtown", "city center", "first street", "first st", "second street", "second st",
    "third street", "third st", "fourth street", "fourth st", "fifth street", "fifth st"
]

PERMIT_TYPES = [
    "Garage sale permit",
    "Construction permit", 
    "Business license",
    "Event permit",
    "Signage permit",
    "Other"
]

ISSUE_TYPES = [
    "Pothole",
    "Streetlight not working",
    "Traffic signal issue",
    "Water leak",
    "Noise complaint",
    "Other"
]

# Garage Sales Permit Helper Functions
def validate_garage_sale_date(date_str: str) -> Dict:
    """Validate garage sale date according to City of Kermit rules"""
    try:
        from datetime import datetime, timedelta
        import re
        
        # Parse various date formats
        date_str = date_str.lower().strip()
        current_date = datetime.now()
        
        # Handle common date formats
        if re.match(r'^(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}', date_str):
            # "June 8", "June 8th"
            date_str = re.sub(r'(st|nd|rd|th)', '', date_str)
            try:
                parsed_date = datetime.strptime(f"{date_str} {current_date.year}", "%B %d %Y")
            except:
                parsed_date = datetime.strptime(f"{date_str} {current_date.year}", "%b %d %Y")
        elif re.match(r'\d{1,2}/\d{1,2}', date_str):
            # "6/8" or "06/08"
            try:
                parsed_date = datetime.strptime(f"{date_str}/{current_date.year}", "%m/%d/%Y")
            except:
                return {"valid": False, "error": "Invalid date format. Try 'June 8' or '6/8'"}
        elif re.match(r'\d{4}-\d{2}-\d{2}', date_str):
            # "2025-06-08"
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
        else:
            # Try to parse other formats
            try:
                parsed_date = datetime.strptime(date_str, "%B %d")
                parsed_date = parsed_date.replace(year=current_date.year)
            except:
                return {"valid": False, "error": "I didn't understand that date format. Please try 'June 8' or '6/8'"}
        
        # Check if date is in the past
        if parsed_date.date() < current_date.date():
            return {"valid": False, "error": "Sorry, you can't schedule a garage sale for a past date. Please choose a future date."}
        
        # Check if date is more than 30 days in advance
        if parsed_date.date() > (current_date + timedelta(days=30)).date():
            return {"valid": False, "error": "You can only apply for garage sale permits up to 30 days in advance. Please choose a date within the next 30 days."}
        
        return {
            "valid": True, 
            "parsed_date": parsed_date,
            "formatted_date": parsed_date.strftime("%B %d, %Y")
        }
        
    except Exception as e:
        return {"valid": False, "error": "I had trouble understanding that date. Please try a format like 'June 8' or '6/8'"}

def check_annual_permit_limit(address: str) -> Dict:
    """Check if address has exceeded 2 garage sale permits per year limit"""
    address_clean = address.lower().strip()
    current_year = datetime.now().year
    
    permits_this_year = 0
    existing_permits = []
    
    for addr, permits in GARAGE_SALE_PERMITS.items():
        if addr in address_clean or address_clean in addr:
            year_permits = [p for p in permits if p.get("year", 2025) == current_year and p.get("status") == "approved"]
            permits_this_year += len(year_permits)
            existing_permits.extend(year_permits)
    
    return {
        "within_limit": permits_this_year < 2,
        "current_count": permits_this_year,
        "existing_permits": existing_permits,
        "remaining": max(0, 2 - permits_this_year)
    }

def validate_city_address(address: str) -> Dict:
    """Check if address is within City of Kermit boundaries"""
    address_clean = address.lower().strip()
    
    # Check against known city streets
    is_valid = any(boundary in address_clean for boundary in CITY_BOUNDARIES)
    
    return {
        "valid": is_valid,
        "message": "Address verified within City of Kermit limits" if is_valid else "This address appears to be outside City of Kermit boundaries. Please verify the address or contact us at (555) 123-CITY for assistance."
    }

def generate_garage_sale_permit_id() -> str:
    """Generate unique garage sale permit ID in GSP-YYYY-XXX format"""
    current_year = datetime.now().year
    
    # Count existing permits for this year to get next number
    existing_count = 0
    for permits in GARAGE_SALE_PERMITS.values():
        existing_count += len([p for p in permits if p.get("year", 2025) == current_year])
    
    # Also count from MOCK_APPLICATIONS
    for app_id, app in MOCK_APPLICATIONS.items():
        if app_id.startswith("GSP-") and app.get("type") == "garage sale permit":
            existing_count += 1
    
    next_number = existing_count + 1
    return f"GSP-{current_year}-{next_number:03d}"

def validate_permit_duration(duration_str: str) -> Dict:
    """Validate garage sale duration"""
    try:
        duration_clean = duration_str.lower().strip()
        
        # Extract number from various formats
        import re
        numbers = re.findall(r'\d+', duration_clean)
        
        if not numbers:
            return {"valid": False, "error": "Please specify the number of days (e.g., '1 day', '2', or 'two days')"}
        
        duration = int(numbers[0])
        
        if duration < 1:
            return {"valid": False, "error": "Garage sale must be at least 1 day long."}
        elif duration > 3:
            return {"valid": False, "error": "Garage sales are limited to maximum 3 consecutive days. For longer events, you may need a special event permit."}
        
        day_word = "day" if duration == 1 else "days"
        return {
            "valid": True,
            "duration": duration,
            "formatted": f"{duration} {day_word}"
        }
        
    except:
        return {"valid": False, "error": "Please specify the number of days as a number (e.g., '1', '2', or 'two')"}

def calculate_garage_sale_fee(duration: int) -> float:
    """Calculate garage sale permit fee based on duration"""
    base_fee = 15.00  # Base fee for 1 day
    additional_day_fee = 5.00  # Additional fee per extra day
    
    if duration <= 1:
        return base_fee
    else:
        return base_fee + ((duration - 1) * additional_day_fee)

def get_session(session_id: str) -> Dict:
    """Get or create user session"""
    if session_id not in user_sessions:
        user_sessions[session_id] = {
            "intent": None,
            "step": 0,
            "context": {},
            "conversation_history": [],
            "failed_attempts": 0,
            "created_at": datetime.now()
        }
    return user_sessions[session_id]

def log_interaction(session_id: str, user_message: str, bot_response: str, intent: str = None):
    """Log user interactions for analytics"""
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "user_message": user_message,
        "bot_response": bot_response[:100] + "..." if len(bot_response) > 100 else bot_response,
        "intent": intent
    }
    logger.info(f"Interaction: {json.dumps(log_data)}")

def detect_intent_with_llm(message: str, conversation_history: List = None) -> Dict:
    """Detect intent using LLM (fallback to keyword matching for demo)"""
    message_lower = message.lower().strip()
    
    # Special cases - handle specific button clicks first
    if message_lower in ["check other services", "other services", "main menu", "back to menu"]:
        return {"intent": "greeting", "confidence": 0.9, "entities": {}, "needs_clarification": False}
    
    if message_lower in ["download receipt", "get receipt"]:
        return {"intent": "download_receipt", "confidence": 0.9, "entities": {}, "needs_clarification": False}
    
    if message_lower in ["pay another bill", "another bill"]:
        return {"intent": "pay_bill", "confidence": 0.9, "entities": {}, "needs_clarification": False}
    
    if message_lower in ["i'm all set", "all set", "done", "finished", "no thanks"]:
        return {"intent": "farewell", "confidence": 0.9, "entities": {}, "needs_clarification": False}
    
    # Garage sale permit specific detection
    if any(phrase in message_lower for phrase in ["garage sale permit", "garage sale", "yard sale permit", "yard sale"]):
        return {"intent": "apply_permit", "confidence": 0.95, "entities": {"permit_type": "garage_sale"}, "needs_clarification": False}
    
    # Permit status checking with garage sale specificity
    if any(phrase in message_lower for phrase in ["check permit gsp", "permit gsp", "garage sale status", "check my garage sale"]):
        return {"intent": "check_status", "confidence": 0.95, "entities": {"permit_type": "garage_sale"}, "needs_clarification": False}
    
    # Greeting detection
    if any(word in message_lower for word in ["hello", "hi", "hey", "help", "start"]):
        return {"intent": "greeting", "confidence": 0.9, "entities": {}, "needs_clarification": False}
    
    # Bill payment detection
    if any(word in message_lower for word in ["bill", "pay", "water", "electricity", "gas", "electric", "utility"]):
        return {"intent": "pay_bill", "confidence": 0.9, "entities": {}, "needs_clarification": False}
    
    # General permit application detection
    if any(word in message_lower for word in ["permit", "license", "apply", "application", "construction"]):
        return {"intent": "apply_permit", "confidence": 0.8, "entities": {}, "needs_clarification": False}
    
    # Ticket/fine payment detection
    if any(word in message_lower for word in ["ticket", "fine", "violation", "parking", "speeding"]):
        return {"intent": "pay_ticket", "confidence": 0.9, "entities": {}, "needs_clarification": False}
    
    # Issue reporting detection
    if any(word in message_lower for word in ["report", "issue", "problem", "pothole", "streetlight", "traffic", "noise"]):
        return {"intent": "report_issue", "confidence": 0.9, "entities": {}, "needs_clarification": False}
    
    # Status check detection (only for specific status-related phrases, not general "check")
    if any(phrase in message_lower for phrase in ["application status", "check status", "track application", "status of", "my application", "permit status"]):
        return {"intent": "check_status", "confidence": 0.9, "entities": {}, "needs_clarification": False}
    
    # Escalation keywords
    if any(word in message_lower for word in ["human", "agent", "person", "representative", "help me", "confused"]):
        return {"intent": "escalate", "confidence": 0.9, "entities": {}, "needs_clarification": False}
    
    return {"intent": "other", "confidence": 0.3, "entities": {}, "needs_clarification": True}

def search_by_address(address: str, search_type: str) -> Dict:
    """Search for bills/applications by address with fuzzy matching"""
    address_clean = address.lower().strip()
    
    # Remove common words and normalize
    address_clean = address_clean.replace("street", "st").replace("avenue", "ave").replace("road", "rd")
    
    if search_type == "bills":
        for addr, bill in MOCK_BILLS.items():
            addr_normalized = addr.replace("street", "st").replace("avenue", "ave").replace("road", "rd")
            if any(part in addr_normalized for part in address_clean.split()) or any(part in address_clean for part in addr_normalized.split()):
                return {"found": True, "data": bill, "address": addr}
    
    elif search_type == "applications":
        for app_id, app in MOCK_APPLICATIONS.items():
            app_addr = app["address"].lower()
            if any(part in app_addr for part in address_clean.split()) or any(part in address_clean for part in app_addr.split()):
                return {"found": True, "data": app, "app_id": app_id}
    
    return {"found": False}

def handle_greeting() -> str:
    """Handle greeting intent with friendly response"""
    return """Hello! 👋 I'm LIA, your **City of Kermit** AI assistant. I'm here to help make your interaction with city services as smooth as possible.

I can help you with:
• 💳 **Pay bills** (water, electricity, gas)
• 🎫 **Pay tickets or fines** (parking, traffic violations)
• 🛠️ **Report issues** (potholes, streetlights, etc.)
• 📊 **Check application status**
• 🎪 **Apply for garage sale permits** *(with smart validation & City of Kermit rules)*

**✨ New Enhanced Features:**
• 🏠 **Address validation** within city limits
• 📅 **Date verification** (no past dates, 30-day advance limit)
• 📋 **Annual permit tracking** (2 garage sales per address/year)
• 💰 **Automatic fee calculation** based on duration
• 🆔 **Real permit IDs** (GSP-2025-XXX format)

Just tell me what you'd like to do in your own words! For example:
• *"I want to pay my water bill"*
• *"I need a garage sale permit for June 8th"*
• *"Check my permit GSP-2025-045"*
• *"There's a pothole on Pine Street"*

How can I help you today?"""

def handle_pay_bill_flow(session: Dict, user_input: str) -> Dict:
    """Handle bill payment conversation flow with realistic payment simulation"""
    if session["step"] == 1:
        session["step"] = 2
        return {
            "response": "I'd be happy to help you find and pay your bills! 💳\n\nTo locate your account, could you please share your address? You can say something like '123 Main Street' or just 'Main Street' - I'll do my best to find it.",
            "needs_escalation": False
        }
    
    elif session["step"] == 2:
        result = search_by_address(user_input, "bills")
        if result["found"]:
            bill = result["data"]
            session["context"]["bill"] = bill
            session["context"]["address"] = result["address"]
            session["step"] = 3
            return {
                "response": f"Perfect! I found your account for **{result['address']}**:\n\n💰 **{bill['type'].title()} Bill**: ${bill['amount']:.2f}\n📅 **Due Date**: {bill['due_date']}\n🏠 **Account**: {bill['account']}\n\nWould you like to proceed with the payment?",
                "needs_escalation": False,
                "options": ["Yes, pay now", "Show me other bills", "Not now"]
            }
        else:
            session["failed_attempts"] += 1
            if session["failed_attempts"] >= 2:
                return {
                    "response": "I'm having trouble locating your bill in our system. This might be because:\n• The address format is different\n• The account is under a different name\n• There might be a system issue\n\nLet me connect you with a customer service representative who can help you find your account and process your payment. They'll be able to access more detailed records.",
                    "needs_escalation": True
                }
            return {
                "response": f"I couldn't find any bills for '{user_input}'. Let me try to help:\n\n• Try a different format (e.g., '123 Main St' instead of '123 Main Street')\n• Double-check the address spelling\n• Make sure it's the address on your account\n\nCould you try entering your address again?",
                "needs_escalation": False
            }
    
    elif session["step"] == 3:
        user_lower = user_input.lower()
        if "yes" in user_lower or "pay" in user_lower:
            session["step"] = 4  # Move to payment processing step
            bill = session["context"]["bill"]
            return {
                "response": f"Awesome! I'm processing your ${bill['amount']:.2f} {bill['type']} bill payment.\n\n📱 **Please check your SMS and email** for the secure payment link. You'll receive it within a few moments.\n\n⏳ Processing payment...",
                "needs_escalation": False,
                "auto_continue_delay": 2000  # Auto-continue after 2 seconds
            }
        elif "other" in user_lower or "show" in user_lower:
            session["step"] = 2
            return {
                "response": "I'd be happy to show you other bills! Could you provide the address for the other account you'd like to check?",
                "needs_escalation": False
            }
        else:
            session["step"] = 0
            session["intent"] = None
            return {
                "response": "No problem at all! Your bill information is saved and you can come back to pay it anytime before the due date.\n\n⏰ **Reminder**: Your bill is due on " + session["context"]["bill"]["due_date"] + "\n\nIs there anything else I can help you with?",
                "needs_escalation": False
            }
    
    elif session["step"] == 4:
        # Payment confirmation step (auto-triggered after delay)
        session["step"] = 0
        session["intent"] = None
        bill = session["context"]["bill"]
        return {
            "response": f"✅ **Payment Successful!**\n\nYour ${bill['amount']:.2f} {bill['type']} bill has been paid successfully!\n\n🧾 **Receipt #**: PAY{datetime.now().strftime('%Y%m%d%H%M%S')}\n📧 **Confirmation email**: Sent to your registered email\n📱 **SMS confirmation**: Sent to your phone\n\nWhat would you like to do next?",
            "needs_escalation": False,
            "options": ["Download receipt", "Pay another bill", "Check other services", "I'm all set"]
        }

def handle_apply_permit_flow(session: Dict, user_input: str) -> Dict:
    """Handle permit application flow"""
    if session["step"] == 1:
        session["step"] = 2
        return {
            "response": "I'd be happy to help you apply for a permit! 📋\n\nWhat type of permit do you need? Here are the most common ones:",
            "needs_escalation": False,
            "options": PERMIT_TYPES
        }
    
    elif session["step"] == 2:
        session["context"]["permit_type"] = user_input
        session["step"] = 3
        return {
            "response": f"Great choice! For a **{user_input}**, I'll need the address where this permit will be used.\n\nCould you please provide the address?",
            "needs_escalation": False
        }
    
    elif session["step"] == 3:
        session["context"]["address"] = user_input
        session["step"] = 0
        session["intent"] = None
        app_id = f"APP{datetime.now().strftime('%Y%m%d%H%M')}"
        
        return {
            "response": f"✅ **Application Submitted Successfully!**\n\n📋 **Permit Type**: {session['context']['permit_type']}\n🏠 **Address**: {user_input}\n🆔 **Application ID**: {app_id}\n\n**Next Steps:**\n• You'll receive an email confirmation within 1 hour\n• Required documents list will be sent to you\n• Typical processing time: 5-7 business days\n• You can check status anytime with your application ID\n\n📞 Questions? Call (555) 123-CITY or reply here!\n\nAnything else I can help with?",
            "needs_escalation": False
        }

def handle_pay_ticket_flow(session: Dict, user_input: str) -> Dict:
    """Handle ticket payment flow"""
    if session["step"] == 1:
        session["step"] = 2
        return {
            "response": "I can help you pay your ticket! 🎫\n\nHow would you like me to find your ticket?",
            "needs_escalation": False,
            "options": ["I have the ticket number", "Look up by address", "Look up by license plate"]
        }
    
    elif session["step"] == 2:
        if "ticket number" in user_input.lower():
            session["step"] = 3
            return {
                "response": "Perfect! Please enter your ticket number (it usually starts with letters like TK or PK followed by numbers):",
                "needs_escalation": False
            }
        else:
            # Simplified for demo - assume we found a ticket
            session["step"] = 4
            session["context"]["ticket"] = {"amount": 45.00, "type": "parking", "location": "Main St"}
            return {
                "response": "I found a ticket for you:\n\n🎫 **Parking Violation** - $45.00\n📍 **Location**: Main St\n📅 **Date**: May 15, 2025\n\nWould you like to pay this ticket now?",
                "needs_escalation": False,
                "options": ["Yes, pay now", "Not this ticket", "Dispute this ticket"]
            }
    
    elif session["step"] == 3:
        # Look up ticket by number
        ticket_num = user_input.upper().strip()
        if ticket_num in MOCK_TICKETS:
            ticket = MOCK_TICKETS[ticket_num]
            session["context"]["ticket"] = ticket
            session["step"] = 4
            return {
                "response": f"Found your ticket! 🎫\n\n**{ticket['type'].title()} Violation**\n💰 **Amount**: ${ticket['amount']:.2f}\n📍 **Location**: {ticket['location']}\n📅 **Date**: {ticket['date']}\n\nWould you like to pay this ticket now?",
                "needs_escalation": False,
                "options": ["Yes, pay now", "Dispute this ticket", "Not now"]
            }
        else:
            session["failed_attempts"] += 1
            if session["failed_attempts"] >= 2:
                return {
                    "response": "I'm having trouble finding that ticket number in our system. Let me connect you with someone who can help locate your ticket and assist with payment.",
                    "needs_escalation": True
                }
            return {
                "response": f"I couldn't find ticket number '{ticket_num}'. Could you double-check the number? It's usually printed at the top of your ticket.",
                "needs_escalation": False
            }
    
    elif session["step"] == 4:
        if "yes" in user_input.lower() and "pay" in user_input.lower():
            session["step"] = 0
            session["intent"] = None
            ticket = session["context"]["ticket"]
            return {
                "response": f"✅ **Ticket Paid Successfully!**\n\nYour ${ticket['amount']:.2f} ticket has been paid in full.\n\n📧 Confirmation email sent\n🧾 Receipt available in your account\n🚗 Drive safely!\n\nIs there anything else I can help you with?",
                "needs_escalation": False
            }
        elif "dispute" in user_input.lower():
            session["step"] = 0
            session["intent"] = None
            return {
                "response": "I understand you'd like to dispute this ticket. Here's what you need to know:\n\n📋 **To dispute**: Visit our online portal or visit City Hall\n📅 **Deadline**: You have 21 days from the ticket date\n📞 **Questions**: Call (555) 123-CITY\n\n⚖️ You can continue to drive while your dispute is being reviewed.\n\nAnything else I can help with?",
                "needs_escalation": False
            }
        else:
            session["step"] = 0
            session["intent"] = None
            return {
                "response": "No problem! Your ticket information is saved. Remember, you can pay anytime to avoid late fees.\n\nIs there anything else I can help you with?",
                "needs_escalation": False
            }

def handle_report_issue_flow(session: Dict, user_input: str) -> Dict:
    """Handle issue reporting flow"""
    if session["step"] == 1:
        session["step"] = 2
        return {
            "response": "Thank you for helping keep our city in great shape! 🛠️\n\nWhat type of issue would you like to report?",
            "needs_escalation": False,
            "options": ISSUE_TYPES
        }
    
    elif session["step"] == 2:
        session["context"]["issue_type"] = user_input
        session["step"] = 3
        return {
            "response": f"Thanks for reporting a **{user_input.lower()}**. To help our team respond quickly, could you provide the specific location?\n\nFor example: '123 Main Street' or 'Corner of Oak and Pine'",
            "needs_escalation": False
        }
    
    elif session["step"] == 3:
        session["context"]["location"] = user_input
        session["step"] = 0
        session["intent"] = None
        ticket_id = f"SR{datetime.now().strftime('%Y%m%d%H%M')}"
        
        return {
            "response": f"✅ **Issue Reported Successfully!**\n\n🎫 **Service Request**: #{ticket_id}\n🛠️ **Issue**: {session['context']['issue_type']}\n📍 **Location**: {user_input}\n\n**What happens next:**\n• Our maintenance team has been notified\n• Expected response time: 2-3 business days\n• You'll receive email updates on progress\n• Emergency issues are prioritized\n\n📞 For urgent safety issues, call (555) 911-CITY\n\nThank you for helping improve our community! Anything else I can do for you?",
            "needs_escalation": False
        }

def handle_check_status_flow(session: Dict, user_input: str) -> Dict:
    """Handle application status checking"""
    if session["step"] == 1:
        session["step"] = 2
        return {
            "response": "I can help you check your application status! 📊\n\nDo you have your application ID, or would you like me to look it up by address?",
            "needs_escalation": False,
            "options": ["I have the application ID", "Look up by address"]
        }
    
    elif session["step"] == 2:
        if "application id" in user_input.lower():
            session["step"] = 3
            return {
                "response": "Great! Please enter your application ID (it usually starts with APP followed by numbers):",
                "needs_escalation": False
            }
        else:
            session["step"] = 4
            return {
                "response": "I'll look up your applications by address. What's the address associated with your application?",
                "needs_escalation": False
            }
    
    elif session["step"] == 3:
        # Look up by application ID
        app_id = user_input.upper().strip()
        if app_id in MOCK_APPLICATIONS:
            app = MOCK_APPLICATIONS[app_id]
            session["step"] = 0
            session["intent"] = None
            return {
                "response": f"📋 **Application Status Found**\n\n🆔 **ID**: {app_id}\n📝 **Type**: {app['type'].title()}\n🏠 **Address**: {app['address']}\n📊 **Status**: {app['status'].title()}\n📅 **Submitted**: {app['submitted']}\n\n**Status Details**: Your application is currently {app['status']}. You should receive an update within 2-3 business days.\n\nNeed help with anything else?",
                "needs_escalation": False
            }
        else:
            return {
                "response": f"I couldn't find application ID '{app_id}'. Could you double-check the ID? It should be in your confirmation email.",
                "needs_escalation": False
            }
    
    elif session["step"] == 4:
        # Look up by address
        result = search_by_address(user_input, "applications")
        session["step"] = 0
        session["intent"] = None
        
        if result["found"]:
            app = result["data"]
            return {
                "response": f"📋 **Application Found**\n\n📝 **Type**: {app['type'].title()}\n🏠 **Address**: {app['address']}\n📊 **Status**: {app['status'].title()}\n📅 **Submitted**: {app['submitted']}\n\n**Status Details**: Your application is {app['status']}.\n\nAnything else I can help with?",
                "needs_escalation": False
            }
        else:
            return {
                "response": f"I couldn't find any applications for '{user_input}'. The application might be under a different address or name. Would you like me to connect you with someone who can help locate it?",
                "needs_escalation": False,
                "options": ["Yes, connect me", "Let me try a different address"]
            }

@app.get("/", response_class=HTMLResponse)
def serve_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())
        session = get_session(session_id)
        
        user_input = request.message.strip()
        
        # Handle auto-continue messages (don't add to conversation history)
        is_auto_continue = user_input == "continue_payment"
        
        # Add to conversation history (except auto-continue messages)
        if not is_auto_continue:
            session["conversation_history"].append({
                "user": user_input, 
                "timestamp": datetime.now().isoformat()
            })
        
        response_data = {"needs_escalation": False, "options": None}
        
        # Handle conversation flow
        if session["step"] == 0 and not is_auto_continue:
            # Detect intent for new conversation (but not for auto-continue)
            intent_result = detect_intent_with_llm(user_input, session["conversation_history"])
            intent = intent_result["intent"]
            
            if intent == "greeting":
                response_text = handle_greeting()
            elif intent == "pay_bill":
                session["intent"] = "pay_bill"
                session["step"] = 1
                result = handle_pay_bill_flow(session, user_input)
                response_text = result["response"]
                response_data.update(result)
            elif intent == "apply_permit":
                session["intent"] = "apply_permit"
                
                # Check if it's specifically a garage sale permit request
                entities = intent_result.get("entities", {})
                is_garage_sale = entities.get("permit_type") == "garage_sale" or any(phrase in user_input.lower() for phrase in ["garage sale permit", "garage sale"])
                
                if is_garage_sale:
                    # For garage sale permits, set context and jump to address collection
                    session["context"]["permit_type"] = "garage sale permit"
                    session["step"] = 3
                    # Call handle_apply_permit_flow with a dummy input to trigger address request
                    result = handle_apply_permit_flow(session, "")
                else:
                    session["step"] = 1
                    result = handle_apply_permit_flow(session, user_input)
                    
                response_text = result["response"]
                response_data.update(result)
            elif intent == "pay_ticket":
                session["intent"] = "pay_ticket"
                session["step"] = 1
                result = handle_pay_ticket_flow(session, user_input)
                response_text = result["response"]
                response_data.update(result)
            elif intent == "report_issue":
                session["intent"] = "report_issue"
                session["step"] = 1
                result = handle_report_issue_flow(session, user_input)
                response_text = result["response"]
                response_data.update(result)
            elif intent == "check_status":
                session["intent"] = "check_status"
                session["step"] = 1
                result = handle_check_status_flow(session, user_input)
                response_text = result["response"]
                response_data.update(result)
            elif intent == "escalate":
                response_text = "Of course! Let me connect you with a human representative who can provide personalized assistance. Please hold on for just a moment."
                response_data["needs_escalation"] = True
            elif intent == "download_receipt":
                response_text = "🧾 **Receipt Download**\n\nYour receipt has been generated and will be downloaded shortly. You can also find all your payment receipts in your account history.\n\nIs there anything else I can help you with today?"
            elif intent == "farewell":
                response_text = "Perfect! Thank you for using our city services. Have a wonderful day! 😊\n\nRemember, I'm here 24/7 whenever you need help with city services. Just come back and start a new conversation anytime!"
            else:
                response_text = """I'm here to help with city services! I can assist you with:

• 💳 **"I want to pay my bill"**
• 📋 **"I need a permit"** 
• 🎫 **"I want to pay a ticket"**
• 🛠️ **"I want to report an issue"**
• 📊 **"Check my application status"**

Just tell me what you'd like to do, and I'll guide you through it step by step!"""
        
        else:
            # Continue existing conversation flow (including auto-continue)
            if session["intent"] == "pay_bill":
                result = handle_pay_bill_flow(session, user_input)
                response_text = result["response"]
                response_data.update(result)
            elif session["intent"] == "apply_permit":
                result = handle_apply_permit_flow(session, user_input)
                response_text = result["response"]
                response_data.update(result)
            elif session["intent"] == "pay_ticket":
                result = handle_pay_ticket_flow(session, user_input)
                response_text = result["response"]
                response_data.update(result)
            elif session["intent"] == "report_issue":
                result = handle_report_issue_flow(session, user_input)
                response_text = result["response"]
                response_data.update(result)
            elif session["intent"] == "check_status":
                result = handle_check_status_flow(session, user_input)
                response_text = result["response"]
                response_data.update(result)
        
        # Log interaction (skip auto-continue messages)
        if not is_auto_continue:
            log_interaction(session_id, user_input, response_text, session.get("intent"))
        
        # Add bot response to history
        session["conversation_history"].append({
            "bot": response_text[:200] + "..." if len(response_text) > 200 else response_text,
            "timestamp": datetime.now().isoformat()
        })
        
        return ChatResponse(
            reply=response_text,
            session_id=session_id,
            intent=session.get("intent"),
            needs_escalation=response_data["needs_escalation"],
            options=response_data.get("options"),
            auto_continue_delay=response_data.get("auto_continue_delay")
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return ChatResponse(
            reply="I'm experiencing some technical difficulties right now. Let me connect you with a human representative who can help you immediately.",
            session_id=session_id or str(uuid.uuid4()),
            needs_escalation=True,
            auto_continue_delay=None
        )

@app.get("/analytics/summary")
def get_analytics_summary():
    """Analytics endpoint for monitoring"""
    try:
        total_sessions = len(user_sessions)
        active_sessions = sum(1 for s in user_sessions.values() 
                            if (datetime.now() - s["created_at"]).seconds < 3600)
        total_interactions = sum(len(s["conversation_history"]) for s in user_sessions.values())
        
        # Intent distribution
        intents = {}
        for session in user_sessions.values():
            intent = session.get("intent", "unknown")
            intents[intent] = intents.get(intent, 0) + 1
        
        return {
            "status": "healthy",
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "total_interactions": total_interactions,
            "intent_distribution": intents,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        return {"status": "error", "message": str(e)}

# For local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
