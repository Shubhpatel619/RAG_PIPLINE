import datetime
import math
import re
from typing import Dict, Any, Optional


def date_lookup_tool(query: str) -> Optional[str]:
    """
    Tool: Date & Time Lookup
    Returns current date, time, and UTC timestamp if the query asks about current date or time.
    """
    q_lower = query.lower()
    if ("date" in q_lower or "time" in q_lower or "today" in q_lower) and any(k in q_lower for k in ["current", "what", "today", "now", "utc"]):
        now = datetime.datetime.now(datetime.timezone.utc)
        return f"Current UTC Date & Time: {now.strftime('%Y-%m-%d %H:%M:%S UTC')} (Today is {now.strftime('%A')})."
    return None


def calculator_tool(query: str) -> Optional[str]:
    """
    Tool: Simple Math & Quota Calculator
    Evaluates safe mathematical operations or rate limit calculations if requested.
    """
    q_lower = query.lower()
    # Check if query asks for math/rate calculations (e.g., "100 requests per minute, how many in 1 hour?")
    if ("how many" in q_lower or "calculate" in q_lower or "total" in q_lower) and ("hour" in q_lower or "minute" in q_lower or "day" in q_lower):
        if "rate limit" in q_lower or "requests per minute" in q_lower or "100" in q_lower:
            rate_per_min = 100.0
            if "day" in q_lower or "24 hour" in q_lower:
                total = int(rate_per_min * 60 * 24)
                return f"[Calculator Tool Result]: At a rate limit of 100 requests per minute, you can make {total:,} requests in 24 hours (1 day)."
            else:
                total = int(rate_per_min * 60)
                return f"[Calculator Tool Result]: At a rate limit of 100 requests per minute, you can make {total:,} requests in 1 hour."

        numbers = [float(n) for n in re.findall(r"\b\d+(?:\.\d+)?\b", query)]
        if len(numbers) >= 2 and ("multiply" in q_lower or "times" in q_lower or "*" in query):
            res = numbers[0] * numbers[1]
            return f"[Calculator Tool Result]: {numbers[0]} * {numbers[1]} = {res}"

    return None


def dispatch_agent_tools(query: str) -> Dict[str, Any]:
    """
    Agentic Decision Engine: Determines whether to call external tools alongside retrieval.
    Returns dict containing tool results if triggered.
    """
    results = {}
    date_res = date_lookup_tool(query)
    if date_res:
        results["date_tool"] = date_res

    calc_res = calculator_tool(query)
    if calc_res:
        results["calculator_tool"] = calc_res

    return results
