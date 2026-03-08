"""
RMP Quiz AgentCore agent.

Two flows:
1. get_question: Uses Eka MCP (search_protocols, search_pharmacology, get_protocol_publishers)
   to fetch content, then produces one quiz question + reference answer for gamified RMP learning.
2. score_answer: Given question, reference answer, and user answer, returns points (0-10) + feedback.
"""

import json
import logging

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool

from gateway_client import (
    _is_gateway_configured,
    get_protocol_publishers_via_gateway,
    search_pharmacology_via_gateway,
    search_protocols_via_gateway,
)

logger = logging.getLogger(__name__)

GET_QUESTION_SYSTEM = """You are a medical quiz assistant for Rural Medical Practitioners (RMPs) in India.
Your task: use the Eka tools to look up protocol or pharmacology content for the given topic, then produce exactly ONE short quiz question and its reference answer.
- Call get_protocol_publishers first if you need valid publisher names, then search_protocols with a query about the topic, OR use search_pharmacology with a drug/topic query.
- After you have content, output ONLY a single JSON object with keys: question, reference_answer, topic. No markdown, no code block, no other text.
- question: clear short question (one or two sentences) that an RMP could answer from the content.
- reference_answer: the correct or ideal answer in 1-3 sentences.
- topic: the topic string you used (e.g. fever protocol, paracetamol dosing)."""

SCORE_ANSWER_SYSTEM = """You are a fair scorer for RMP quiz answers. Given a question, the reference answer, and the user's answer, score from 0 to 10 and give one line of feedback.
- 10: Correct and complete. 7-9: Mostly correct or partially complete. 4-6: Some relevance but incomplete or partly wrong. 1-3: Mostly wrong. 0: No meaningful answer.
- Output ONLY a single JSON object with keys: points (integer 0-10), feedback (string, one line). No markdown, no code block, no other text."""

app = BedrockAgentCoreApp()


@tool
def get_protocol_publishers_tool() -> str:
    """Get list of protocol publishers (e.g. ICMR, RSSDI). Call before search_protocols to get valid publisher names."""
    if not _is_gateway_configured():
        return json.dumps({"publishers": ["ICMR", "RSSDI"], "message": "Gateway not configured"})
    out = get_protocol_publishers_via_gateway()
    return json.dumps(out.get("publishers", out), indent=2)


@tool
def search_protocols_tool(queries: str) -> str:
    """Search Indian treatment protocols. Pass a JSON string: array of objects with query (string), optional tag, optional publisher."""
    if not _is_gateway_configured():
        return json.dumps({"protocols": [], "message": "Gateway not configured"})
    try:
        q = json.loads(queries) if isinstance(queries, str) else queries
    except json.JSONDecodeError:
        q = []
    out = search_protocols_via_gateway(queries=q)
    return json.dumps(out.get("protocols", out), indent=2)


@tool
def search_pharmacology_tool(query: str, limit: int = 5) -> str:
    """Search pharmacology: dose, indications, contraindications. Use for drug-related quiz questions."""
    if not _is_gateway_configured():
        return json.dumps({"results": [], "message": "Gateway not configured"})
    out = search_pharmacology_via_gateway(query=query, limit=limit)
    return json.dumps(out.get("results", out), indent=2)


def _extract_json_from_content(content: str) -> dict | None:
    """Parse JSON from agent response (plain JSON or inside markdown code block)."""
    content = (content or "").strip()
    if not content:
        return None
    if content.startswith("```"):
        lines = content.split("\n")
        start = next(
            (i for i, ln in enumerate(lines) if "```json" in ln or ln.strip() == "```"),
            0,
        )
        end = next(
            (i for i in range(start + 1, len(lines)) if lines[i].strip() == "```"),
            len(lines),
        )
        content = "\n".join(lines[start + 1 : end])
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None


def _run_agent(agent: Agent, prompt: str) -> str:
    """Run agent and return text content from message."""
    result = agent(prompt)
    msg = result.message if hasattr(result, "message") else result
    content = ""
    if isinstance(msg, dict):
        content = msg.get("content", "")
    elif hasattr(msg, "content"):
        content = msg.content or ""
    else:
        content = str(msg)
    if isinstance(content, list):
        content = "".join(
            c.get("text", "") if isinstance(c, dict) else str(getattr(c, "text", c))
            for c in content
        )
    return (content or "").strip()


@app.entrypoint
def rmp_quiz(payload: dict) -> dict:
    """
    Entrypoint: get_question (topic -> question + reference_answer) or score_answer (question, reference, user_answer -> points + feedback).
    Payload:
      - action: "get_question" | "score_answer"
      - get_question: topic (string)
      - score_answer: question, reference_answer, user_answer (strings)
    """
    action = (payload.get("action") or "get_question").strip().lower()

    if action == "score_answer":
        question = payload.get("question") or ""
        reference = payload.get("reference_answer") or payload.get("reference") or ""
        user_answer = payload.get("user_answer") or ""
        if not question or not reference or not user_answer:
            return {"points": 0, "feedback": "Missing question, reference_answer, or user_answer."}
        prompt = f"{SCORE_ANSWER_SYSTEM}\n\nQuestion: {question}\nReference answer: {reference}\nUser answer: {user_answer}"
        agent = Agent(tools=[])  # No tools for scoring
        content = _run_agent(agent, prompt)
        data = _extract_json_from_content(content)
        if data and "points" in data:
            points = data.get("points", 0)
            if not isinstance(points, (int, float)):
                try:
                    points = int(float(points))
                except (TypeError, ValueError):
                    points = 0
            points = max(0, min(10, int(points)))
            return {
                "points": points,
                "feedback": data.get("feedback", "Scored."),
            }
        return {"points": 0, "feedback": "Could not parse score. Please try again."}

    # get_question
    topic = (payload.get("topic") or "fever protocol").strip()
    prompt = f"{GET_QUESTION_SYSTEM}\n\nTopic for the quiz question: {topic}"
    tools = [get_protocol_publishers_tool, search_protocols_tool, search_pharmacology_tool]
    agent = Agent(tools=tools)
    content = _run_agent(agent, prompt)
    data = _extract_json_from_content(content)
    if data and data.get("question") and data.get("reference_answer"):
        return {
            "question": data["question"],
            "reference_answer": data["reference_answer"],
            "topic": data.get("topic", topic),
        }
    # Fallback: return a simple question if agent didn't return valid JSON
    return {
        "question": f"What is the first step you would take for a patient presenting with {topic}?",
        "reference_answer": "Assess ABC (Airway, Breathing, Circulation) and vital signs; then follow the relevant protocol.",
        "topic": topic,
    }


if __name__ == "__main__":
    app.run()
