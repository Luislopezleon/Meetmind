"""
MeetMind Meeting Intelligence Agent.

LangGraph-based agent that processes meeting transcripts and extracts:
- Action items (tasks, assignees, deadlines)
- Decisions (choices made, impact, context)
- Risks (problems, concerns, blockers)
- Open questions (unanswered questions needing follow-up)
- Executive summary
"""

import json
from typing import List, Dict, Any, Optional
from loguru import logger

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END

from app.agents.state import AgentState
from app.agents.prompts import (
    SYSTEM_PROMPT,
    ACTION_ITEMS_PROMPT,
    DECISIONS_PROMPT,
    RISKS_PROMPT,
    QUESTIONS_PROMPT,
    SUMMARY_PROMPT,
)
from app.core.config import settings


# Initialize LLM
def get_llm(temperature: float = 0.1):
    """Get configured Gemini instance for JSON extraction."""
    return ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=temperature,
        google_api_key=settings.gemini_api_key,
    )


def get_llm_text(temperature: float = 0.3):
    """Get Gemini for text generation (summaries)."""
    return ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=temperature,
        google_api_key=settings.gemini_api_key,
    )


def format_transcript(transcript: List[dict]) -> str:
    """Format transcript segments into readable text."""
    lines = []
    for segment in transcript:
        speaker = segment.get("speaker", segment.get("speaker_name", "Unknown"))
        text = segment.get("text", "")
        if text.strip():
            lines.append(f"{speaker}: {text}")
    return "\n".join(lines)


def parse_json_response(content) -> dict:
    """Parse JSON from LLM response, handling various response formats."""
    # Handle list-type responses (Gemini returns [{type: text, text: ...}])
    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                text_parts.append(part["text"])
            elif isinstance(part, str):
                text_parts.append(part)
        text = " ".join(text_parts)
    else:
        text = str(content).strip()
    
    # Remove markdown code block if present
    if "```" in text:
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    
    text = text.strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object in the text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        return {}


# --- Agent Nodes ---

def extract_action_items(state: AgentState) -> dict:
    """Extract action items from the transcript."""
    transcript_text = format_transcript(state["transcript"])
    
    if not transcript_text.strip():
        return {"action_items": []}
    
    llm = get_llm()
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=ACTION_ITEMS_PROMPT.format(transcript=transcript_text)),
    ]
    
    try:
        response = llm.invoke(messages)
        result = parse_json_response(response.content)
        items = result.get("action_items", [])
        
        # Filter by confidence threshold
        filtered = [item for item in items if item.get("confidence", 0) >= 0.75]
        logger.info(f"Detected {len(filtered)} action items (from {len(items)} candidates)")
        
        return {"action_items": filtered}
    except Exception as e:
        logger.error(f"Error extracting action items: {e}")
        return {"action_items": []}


def extract_decisions(state: AgentState) -> dict:
    """Extract decisions from the transcript."""
    transcript_text = format_transcript(state["transcript"])
    
    if not transcript_text.strip():
        return {"decisions": []}
    
    llm = get_llm()
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=DECISIONS_PROMPT.format(transcript=transcript_text)),
    ]
    
    try:
        response = llm.invoke(messages)
        result = parse_json_response(response.content)
        items = result.get("decisions", [])
        
        filtered = [item for item in items if item.get("confidence", 0) >= 0.75]
        logger.info(f"Detected {len(filtered)} decisions (from {len(items)} candidates)")
        
        return {"decisions": filtered}
    except Exception as e:
        logger.error(f"Error extracting decisions: {e}")
        return {"decisions": []}


def extract_risks(state: AgentState) -> dict:
    """Extract risks and concerns from the transcript."""
    transcript_text = format_transcript(state["transcript"])
    
    if not transcript_text.strip():
        return {"risks": []}
    
    llm = get_llm()
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=RISKS_PROMPT.format(transcript=transcript_text)),
    ]
    
    try:
        response = llm.invoke(messages)
        result = parse_json_response(response.content)
        items = result.get("risks", [])
        
        filtered = [item for item in items if item.get("confidence", 0) >= 0.75]
        logger.info(f"Detected {len(filtered)} risks (from {len(items)} candidates)")
        
        return {"risks": filtered}
    except Exception as e:
        logger.error(f"Error extracting risks: {e}")
        return {"risks": []}


def extract_questions(state: AgentState) -> dict:
    """Extract open/unanswered questions from the transcript."""
    transcript_text = format_transcript(state["transcript"])
    
    if not transcript_text.strip():
        return {"questions": []}
    
    llm = get_llm()
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=QUESTIONS_PROMPT.format(transcript=transcript_text)),
    ]
    
    try:
        response = llm.invoke(messages)
        result = parse_json_response(response.content)
        items = result.get("questions", [])
        
        filtered = [item for item in items if item.get("confidence", 0) >= 0.75]
        logger.info(f"Detected {len(filtered)} open questions (from {len(items)} candidates)")
        
        return {"questions": filtered}
    except Exception as e:
        logger.error(f"Error extracting questions: {e}")
        return {"questions": []}


def generate_summary(state: AgentState) -> dict:
    """Generate executive summary of the meeting."""
    transcript_text = format_transcript(state["transcript"])
    
    if not transcript_text.strip():
        return {"summary": None}
    
    # Use GPT-4o for higher quality summaries
    llm = get_llm_text()
    
    # Format detected insights for context
    action_items_text = json.dumps(state.get("action_items", []), ensure_ascii=False, indent=2)
    decisions_text = json.dumps(state.get("decisions", []), ensure_ascii=False, indent=2)
    participants = ", ".join(state.get("participants", []))
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=SUMMARY_PROMPT.format(
            transcript=transcript_text,
            participants=participants or "No identificados",
            action_items=action_items_text,
            decisions=decisions_text,
        )),
    ]
    
    try:
        response = llm.invoke(messages)
        summary = response.content
        # Handle list-type response from Gemini
        if isinstance(summary, list):
            parts = []
            for part in summary:
                if isinstance(part, dict) and "text" in part:
                    parts.append(part["text"])
                elif isinstance(part, str):
                    parts.append(part)
            summary = "\n".join(parts)
        logger.info(f"Generated summary ({len(summary)} chars)")
        
        return {"summary": summary}
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return {"summary": None}


# --- Build the Graph ---

def build_meeting_agent() -> StateGraph:
    """
    Build the LangGraph agent for meeting intelligence.
    
    Graph structure:
    
        START
          |
          ├── extract_action_items
          ├── extract_decisions
          ├── extract_risks
          └── extract_questions
          |
          v
        generate_summary
          |
          v
         END
    
    The first 4 nodes run in parallel (fan-out), then converge
    into the summary generator which has access to all detected insights.
    """
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("extract_action_items", extract_action_items)
    workflow.add_node("extract_decisions", extract_decisions)
    workflow.add_node("extract_risks", extract_risks)
    workflow.add_node("extract_questions", extract_questions)
    workflow.add_node("generate_summary", generate_summary)
    
    # Define edges: all extractors run from start
    workflow.set_entry_point("extract_action_items")
    
    workflow.add_edge("extract_action_items", "extract_decisions")
    workflow.add_edge("extract_decisions", "extract_risks")
    workflow.add_edge("extract_risks", "extract_questions")
    workflow.add_edge("extract_questions", "generate_summary")
    workflow.add_edge("generate_summary", END)
    
    return workflow.compile()


# Global agent instance
meeting_agent = build_meeting_agent()


async def analyze_meeting(
    meeting_id: int,
    transcript: List[dict],
    participants: List[str] = None,
    generate_summary_flag: bool = True,
) -> Dict[str, Any]:
    """
    Run the meeting intelligence agent on a transcript.
    
    Args:
        meeting_id: ID of the meeting
        transcript: List of transcript segments [{text, speaker, ...}]
        participants: List of participant names
        generate_summary_flag: Whether to generate summary (set False for incremental)
    
    Returns:
        Dict with action_items, decisions, risks, questions, summary
    """
    if not transcript:
        return {
            "action_items": [],
            "decisions": [],
            "risks": [],
            "questions": [],
            "summary": None,
        }
    
    initial_state: AgentState = {
        "meeting_id": meeting_id,
        "transcript": transcript,
        "action_items": [],
        "decisions": [],
        "risks": [],
        "questions": [],
        "summary": None,
        "language": "auto",
        "participants": participants or [],
    }
    
    logger.info(f"Running meeting agent for meeting {meeting_id} ({len(transcript)} segments)")
    
    # Run the graph
    result = await meeting_agent.ainvoke(initial_state)
    
    logger.info(
        f"Agent completed for meeting {meeting_id}: "
        f"{len(result['action_items'])} actions, "
        f"{len(result['decisions'])} decisions, "
        f"{len(result['risks'])} risks, "
        f"{len(result['questions'])} questions"
    )
    
    return {
        "action_items": result["action_items"],
        "decisions": result["decisions"],
        "risks": result["risks"],
        "questions": result["questions"],
        "summary": result["summary"],
    }
