import os
import re

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from hindsight_client import Hindsight


# =====================================================
# LOAD ENVIRONMENT
# =====================================================

load_dotenv(override=True)


# =====================================================
# FASTAPI APP
# =====================================================

app = FastAPI(title="RecallMeet")


# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# HINDSIGHT CLIENT
# =====================================================

client = Hindsight(
    base_url=os.getenv("HINDSIGHT_BASE_URL"),
    api_key=os.getenv("HINDSIGHT_API_KEY")
)

BANK_ID = os.getenv("HINDSIGHT_BANK_ID")


# =====================================================
# DATA MODELS
# =====================================================

class Meeting(BaseModel):
    client_name: str
    notes: str


class RecallRequest(BaseModel):
    query: str


class PrepareRequest(BaseModel):
    client_name: str


# =====================================================
# MEMORY HELPERS
# =====================================================

def get_memory_text(result):

    text = getattr(result, "text", "")

    if not text:
        return ""

    return text.strip()


def clean_memory_for_comparison(text):

    if not text:
        return ""

    clean_text = re.split(
        r"\s*\|\s*(?:When|Involving)\s*:",
        text,
        flags=re.IGNORECASE
    )[0]

    clean_text = re.sub(
        r"\s+",
        " ",
        clean_text
    ).strip()

    clean_text = clean_text.rstrip(
        " .,!?:;"
    )

    return clean_text.lower()


def get_unique_memories(results):

    memories = []
    seen = set()

    for result in results:

        text = get_memory_text(result)

        if not text:
            continue

        key = clean_memory_for_comparison(text)

        if not key:
            continue

        if key in seen:
            continue

        seen.add(key)
        memories.append(text)

    return memories
# =====================================================
# CLIENT HELPERS
# =====================================================

def filter_client_memories(memories, client_name):

    client_lower = client_name.lower().strip()

    return [
        memory
        for memory in memories
        if client_lower in memory.lower()
    ]


def detect_client_from_query(query):

    known_clients = [
        "TechNova Ltd",
        "Acme Corp"
    ]

    query_lower = query.lower()

    for client_name in known_clients:

        if client_name.lower() in query_lower:
            return client_name

    return None


# =====================================================
# EXTRACTION HELPERS
# =====================================================

def extract_money(text):

    matches = re.findall(
        r"₹\s?\d+(?:\.\d+)?\s?"
        r"(?:lakh|lakhs|crore|crores)",
        text,
        re.IGNORECASE
    )

    unique = []

    for value in matches:

        value = value.strip()

        if value.lower() not in [
            x.lower() for x in unique
        ]:
            unique.append(value)

    return unique


def extract_months(text):

    matches = re.findall(
        r"\b\d+\s+months?\b",
        text,
        re.IGNORECASE
    )

    unique = []

    for value in matches:

        value = value.lower().strip()

        if value not in unique:
            unique.append(value)

    return unique


def extract_timeline_changes(memories):

    changes = []

    for memory in memories:

        match = re.search(
            r"from\s+(\d+)\s+months?"
            r"\s+to\s+(\d+)\s+months?",
            memory,
            re.IGNORECASE
        )

        if match:

            changes.append(
                (
                    f"{match.group(1)} months",
                    f"{match.group(2)} months",
                    memory
                )
            )

    return changes


# =====================================================
# MEMORY SELECTION
# =====================================================

def select_relevant_memories(memories):

    selected = []

    categories = {
        "budget": None,
        "timeline": None,
        "security": None,
        "integration": None,
        "concern": None,
        "timeline_change": None
    }

    for memory in memories:

        text = memory.lower()

        if (
            categories["budget"] is None
            and "budget" in text
        ):
            categories["budget"] = memory

        if (
            categories["timeline"] is None
            and "month" in text
        ):
            categories["timeline"] = memory

        if (
            categories["security"] is None
            and (
                "security" in text
                or "encryption" in text
                or "two-factor" in text
                or "2fa" in text
                or "authentication" in text
            )
        ):
            categories["security"] = memory

        if (
            categories["integration"] is None
            and (
                "integration" in text
                or "existing system" in text
            )
        ):
            categories["integration"] = memory

        if (
            categories["concern"] is None
            and (
                "concern" in text
                or "risk" in text
                or "issue" in text
            )
        ):
            categories["concern"] = memory

        if (
            categories["timeline_change"] is None
            and (
                "from" in text
                and "to" in text
                and "month" in text
            )
        ):
            categories["timeline_change"] = memory

    for category in [
        "budget",
        "timeline",
        "security",
        "integration",
        "concern",
        "timeline_change"
    ]:

        memory = categories[category]

        if memory and memory not in selected:
            selected.append(memory)

    return selected[:6]


def select_recall_memories(memories):

    selected = []

    security_memory = None
    budget_memory = None
    timeline_memory = None
    timeline_change_memory = None
    integration_memory = None
    concern_memory = None

    for memory in memories:

        text = memory.lower()

        if (
            security_memory is None
            and (
                "security" in text
                or "encryption" in text
                or "two-factor" in text
                or "2fa" in text
                or "authentication" in text
            )
        ):
            security_memory = memory

        if (
            budget_memory is None
            and "budget" in text
        ):
            budget_memory = memory

        if (
            timeline_memory is None
            and "month" in text
        ):
            timeline_memory = memory

        if (
            timeline_change_memory is None
            and (
                "from" in text
                and "to" in text
                and "month" in text
            )
        ):
            timeline_change_memory = memory

        if (
            integration_memory is None
            and (
                "integration" in text
                or "existing system" in text
            )
        ):
            integration_memory = memory

        if (
            concern_memory is None
            and (
                "concern" in text
                or "risk" in text
                or "issue" in text
            )
        ):
            concern_memory = memory

    if security_memory:
        selected.append(security_memory)

    if budget_memory:
        selected.append(budget_memory)

    if timeline_memory:
        selected.append(timeline_memory)

    if timeline_change_memory:
        selected.append(timeline_change_memory)

    if integration_memory:
        selected.append(integration_memory)

    if (
        concern_memory
        and concern_memory != security_memory
        and concern_memory != integration_memory
    ):
        selected.append(concern_memory)

    final = []
    seen = set()

    for memory in selected:

        key = clean_memory_for_comparison(memory)

        if key not in seen:

            seen.add(key)
            final.append(memory)

    return final[:5]
# =====================================================
# HOME
# =====================================================

@app.get("/")
def home():

    return {
        "message": "RecallMeet is running!"
    }


# =====================================================
# REMEMBER A MEETING
# =====================================================

@app.post("/remember")
def remember_meeting(meeting: Meeting):

    client.retain(
        bank_id=BANK_ID,
        content=meeting.notes,
        context=f"Meeting with {meeting.client_name}"
    )

    return {
        "message": "Meeting remembered successfully",
        "client": meeting.client_name
    }


# =====================================================
# RECALL PAST CONTEXT
# =====================================================

@app.post("/recall")
def recall_memory(request: RecallRequest):

    response = client.recall(
        bank_id=BANK_ID,
        query=request.query
    )

    memories = get_unique_memories(
        response.results
    )

    selected_client = detect_client_from_query(
        request.query
    )

    if selected_client:

        memories = filter_client_memories(
            memories,
            selected_client
        )

    memories = select_recall_memories(
        memories
    )

    return {
        "query": request.query,
        "client": selected_client,
        "memories": memories
    }


# =====================================================
# PREPARE MEETING
# =====================================================

@app.post("/prepare")
def prepare_meeting(request: PrepareRequest):

    client_name = request.client_name.strip()

    query = f"""
    Prepare me for my next meeting with
    {client_name}.

    Only return information about
    {client_name}.

    Do not return information about
    other clients.

    Focus on budget, timeline,
    security requirements,
    integration requirements,
    concerns, commitments,
    unresolved issues and risks.
    """

    response = client.recall(
        bank_id=BANK_ID,
        query=query
    )

    memories = get_unique_memories(
        response.results
    )

    client_memories = filter_client_memories(
        memories,
        client_name
    )

    if not client_memories:
        client_memories = memories

    all_text = " ".join(client_memories)
    lower_text = all_text.lower()

    # =================================================
    # BUDGET
    # =================================================

    money_values = extract_money(all_text)

    if money_values:
        budget = money_values[0]
    else:
        budget = "Not found"

    # =================================================
    # TIMELINE
    # =================================================

    timeline_changes = extract_timeline_changes(
        client_memories
    )

    previous_timeline = "Not found"
    current_timeline = "Not found"

    if timeline_changes:

        old_value, new_value, _ = timeline_changes[-1]

        previous_timeline = old_value
        current_timeline = new_value

    else:

        month_values = extract_months(all_text)

        if len(month_values) >= 2:

            previous_timeline = month_values[0]
            current_timeline = month_values[-1]

        elif len(month_values) == 1:

            current_timeline = month_values[0]

    # =================================================
    # DETECT ISSUES
    # =================================================

    security_issue = (
        "security" in lower_text
        or "encryption" in lower_text
        or "two-factor" in lower_text
        or "2fa" in lower_text
        or "authentication" in lower_text
    )

    integration_issue = (
        "integration" in lower_text
        or "existing system" in lower_text
    )

    timeline_changed = len(timeline_changes) > 0

    # =================================================
    # KEY CHANGE
    # =================================================

    if security_issue and timeline_changed:

        key_change = (
            f"Security requirements changed "
            f"the delivery plan from "
            f"{previous_timeline} to "
            f"{current_timeline}."
        )

    elif integration_issue and timeline_changed:

        key_change = (
            f"Integration requirements changed "
            f"the delivery plan from "
            f"{previous_timeline} to "
            f"{current_timeline}."
        )

    elif timeline_changed:

        key_change = (
            f"The delivery timeline changed "
            f"from {previous_timeline} "
            f"to {current_timeline}."
        )

    elif security_issue:

        key_change = (
            "Security requirements became an "
            "important discussion point."
        )

    elif integration_issue:

        key_change = (
            "Integration requirements became an "
            "important discussion point."
        )

    else:

        key_change = (
            "Previous interactions contain "
            "important requirements to review."
        )
        # =================================================
    # RELATIONSHIP CONTEXT
    # =================================================

    if security_issue:

        relationship_context = (
            f"{client_name} previously discussed "
            "security requirements and related concerns."
        )

    elif integration_issue:

        relationship_context = (
            f"{client_name} previously discussed "
            "integration requirements and related concerns."
        )

    else:

        relationship_context = (
            f"RecallMeet found relevant previous "
            f"interactions with {client_name}."
        )

    # =================================================
    # COMMITMENT FOCUS
    # =================================================

    commitment_focus = (
        "Review previous commitments and deadlines."
    )

    # =================================================
    # NEXT MEETING FOCUS
    # =================================================

    next_meeting_focus = [
        "Review previous commitments",
        "Confirm current requirements"
    ]

    if security_issue:

        next_meeting_focus.append(
            "Review security requirements "
            "and remaining risks"
        )

    if integration_issue:

        next_meeting_focus.append(
            "Review integration requirements "
            "and remaining risks"
        )

    next_meeting_focus.extend([
        "Discuss unresolved concerns",
        "Confirm the latest delivery timeline",
        "Check whether the agreed budget "
        "still meets requirements"
    ])

    # =================================================
    # MEMORY EVIDENCE
    # =================================================

    clean_evidence = select_relevant_memories(
        client_memories
    )

    # =================================================
    # FINAL RESPONSE
    # =================================================

    return {
        "client": client_name,
        "budget": budget,
        "previous_timeline": previous_timeline,
        "current_timeline": current_timeline,
        "key_change": key_change,
        "relationship_context": relationship_context,
        "commitment_focus": commitment_focus,
        "next_meeting_focus": next_meeting_focus,
        "memory_evidence": clean_evidence
    }


# =====================================================
# MEETING HISTORY
# =====================================================

@app.post("/history")
def meeting_history(request: PrepareRequest):

    client_name = request.client_name.strip()

    query = f"""
    Show me the important history of
    my interactions with {client_name}.

    Only return memories involving
    {client_name}.

    Do not return information about
    other clients.

    Include previous discussions,
    commitments, concerns, deadlines,
    budget, unresolved issues and
    changes over time.
    """

    response = client.recall(
        bank_id=BANK_ID,
        query=query
    )

    memories = get_unique_memories(
        response.results
    )

    client_memories = filter_client_memories(
        memories,
        client_name
    )

    if not client_memories:
        client_memories = memories

    clean_history = select_relevant_memories(
        client_memories
    )

    return {
        "client": client_name,
        "history": clean_history
    }