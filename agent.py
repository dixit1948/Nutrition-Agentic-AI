"""
agent.py
──────────────────────────────────────────────────────────────────────────────
Nutrition Agentic AI Engine

Implements the full agentic loop:
  1. PERCEIVE  – Receive and validate user input / profile
  2. REASON    – Select the appropriate tool / action
  3. ACT       – Call IBM Granite LLM with structured prompts
  4. REFLECT   – Apply guardrails and safety checks to output
  5. RESPOND   – Return safe, helpful, formatted response

Tools available to the agent:
  • generate_nutrition_plan  – Full personalized meal plan
  • answer_nutrition_query   – General Q&A about nutrition / health
  • get_local_food_tips      – Regional / cultural food recommendations
  • calculate_bmi            – BMI calculation and classification
"""

import os
from typing import Any

from granite_client import generate_text
from guardrails import (
    screen_input,
    screen_output,
    apply_ham_tone,
    add_disclaimer,
    validate_user_profile,
    is_nutrition_related,
)

# ── Agent memory (in-process session store) ───────────────────────────────────
# Key: session_id (str), Value: list of {"role": ..., "content": ...}
_session_memory: dict[str, list[dict]] = {}

MAX_HISTORY = 10  # Maximum conversation turns to keep in memory


# ─────────────────────────────────────────────────────────────────────────────
# Tool Implementations
# ─────────────────────────────────────────────────────────────────────────────

def tool_generate_nutrition_plan(profile: dict) -> str:
    """
    Tool: Generate a personalized nutrition plan using IBM Granite.
    """
    name    = profile.get("name", "User")
    age     = profile.get("age", "N/A")
    diet    = profile.get("diet", "vegetarian")
    medical = profile.get("medical_history", "none")
    city    = profile.get("city", "")
    country = profile.get("country", "")
    goals   = profile.get("goals", "maintain a healthy lifestyle")
    weight  = profile.get("weight", "")
    height  = profile.get("height", "")

    location_str = f"{city}, {country}" if city and country else (country or city or "unspecified location")

    weight_info = f"\n- Weight: {weight} kg" if weight else ""
    height_info = f"\n- Height: {height} cm" if height else ""

    prompt = f"""[INST] You are NutriAI, an expert clinical nutritionist and dietitian powered by IBM Granite. Your role is to provide safe, evidence-based, personalized nutrition guidance.

Create a comprehensive, detailed, and practical 7-day-style personalized nutrition plan for the following individual:

**User Profile:**
- Name: {name}
- Age: {age} years
- Diet Preference: {diet}
- Medical History / Conditions: {medical}
- Location: {location_str}{weight_info}{height_info}
- Health Goals: {goals}

**Instructions:**
1. Design a realistic, culturally appropriate meal plan (consider local foods from {location_str}).
2. Include breakfast, mid-morning snack, lunch, afternoon snack, dinner, and post-dinner options.
3. Specify macro and micronutrient targets (calories, protein, carbs, fats, fiber, water).
4. Address the medical conditions ({medical}) with specific dietary modifications and foods to include/avoid.
5. Include hydration schedule and lifestyle recommendations.
6. Format the plan with clear markdown headers, bullet points, and a food summary table.
7. Be culturally sensitive — suggest foods commonly available in {location_str}.
8. Use a warm, encouraging, and respectful tone throughout.
9. Do NOT claim to replace medical advice — focus on evidence-based nutritional guidance.

Generate the complete personalized nutrition plan now: [/INST]"""

    raw_response = generate_text(prompt, max_new_tokens=1500, temperature=0.65)
    safe_response = screen_output(raw_response)
    ham_response  = apply_ham_tone(safe_response)
    final         = add_disclaimer(ham_response)
    return final


def tool_answer_nutrition_query(query: str, profile: dict = None, history: list = None) -> str:
    """
    Tool: Answer a general nutrition or health-related query.
    """
    context = ""
    if profile:
        context = (
            f"The user is {profile.get('name', 'a user')}, "
            f"age {profile.get('age', 'unknown')}, "
            f"follows a {profile.get('diet', 'balanced')} diet, "
            f"and has the following medical history: {profile.get('medical_history', 'none')}. "
            f"They are located in {profile.get('city', '')}, {profile.get('country', '')}."
        )

    history_str = ""
    if history:
        recent = history[-4:]  # Last 4 turns
        history_str = "\n".join(
            f"{'User' if h['role'] == 'user' else 'NutriAI'}: {h['content']}"
            for h in recent
        )

    prompt = f"""[INST] You are NutriAI, a knowledgeable and empathetic nutrition assistant powered by IBM Granite. You provide evidence-based, safe, and helpful answers to nutrition and health questions.

{f'User Context: {context}' if context else ''}
{f'Recent Conversation:{chr(10)}{history_str}' if history_str else ''}

User Question: {query}

Answer the question helpfully, accurately, and in a friendly, respectful tone. Use bullet points and structure where appropriate. Keep your answer practical and actionable. If the question is outside nutrition/health scope, gently redirect to nutrition topics. [/INST]"""

    raw_response = generate_text(prompt, max_new_tokens=800, temperature=0.7)
    safe_response = screen_output(raw_response)
    ham_response  = apply_ham_tone(safe_response)
    return ham_response


def tool_get_local_food_tips(city: str, country: str, diet: str) -> str:
    """
    Tool: Provide local / regional food recommendations.
    """
    prompt = f"""[INST] You are NutriAI, an expert in global cuisines and nutrition. 

Provide practical, culturally appropriate, and nutritious food recommendations for someone living in {city}, {country} who follows a {diet} diet.

Include:
1. Top 5 locally available nutritious foods and their health benefits
2. Traditional dishes that are healthy and nutritious
3. Local superfoods or traditional remedies
4. Foods to avoid or limit for health reasons
5. Where to find healthy options (markets, stores)

Keep it practical, specific to {country}'s food culture, and evidence-based. [/INST]"""

    raw_response = generate_text(prompt, max_new_tokens=600, temperature=0.7)
    return screen_output(raw_response)


def tool_calculate_bmi(weight_kg: float, height_cm: float) -> dict:
    """
    Tool: Calculate BMI and provide classification.
    Returns dict with bmi, category, and recommendation.
    """
    if height_cm <= 0 or weight_kg <= 0:
        return {"error": "Invalid weight or height values."}

    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m ** 2), 1)

    if bmi < 18.5:
        category = "Underweight"
        recommendation = "Focus on calorie-dense, nutrient-rich foods to reach a healthy weight."
    elif 18.5 <= bmi < 25.0:
        category = "Normal Weight"
        recommendation = "Maintain your current healthy weight with a balanced diet and regular activity."
    elif 25.0 <= bmi < 30.0:
        category = "Overweight"
        recommendation = "Adopt a moderate calorie-reduction strategy and increase physical activity."
    else:
        category = "Obese"
        recommendation = "Consult a healthcare provider for a supervised weight management program."

    return {
        "bmi": bmi,
        "category": category,
        "recommendation": recommendation,
        "healthy_range": "18.5 – 24.9",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Agent Router  –  Decides which tool to invoke
# ─────────────────────────────────────────────────────────────────────────────

def _route_to_tool(message: str, profile: dict) -> str:
    """
    Simple intent-based router: map user message to the right tool.
    """
    msg = message.lower()

    if any(kw in msg for kw in ["bmi", "body mass", "calculate my bmi"]):
        weight = profile.get("weight")
        height = profile.get("height")
        if weight and height:
            try:
                result = tool_calculate_bmi(float(weight), float(height))
                if "error" not in result:
                    return (
                        f"📊 **Your BMI Results**\n\n"
                        f"- **BMI Score:** {result['bmi']}\n"
                        f"- **Category:** {result['category']}\n"
                        f"- **Healthy Range:** {result['healthy_range']}\n"
                        f"- **Recommendation:** {result['recommendation']}"
                    )
            except (ValueError, TypeError):
                pass

    if any(kw in msg for kw in ["local food", "food in", "traditional food", "regional food", "cuisine"]):
        city    = profile.get("city", "your city")
        country = profile.get("country", "your country")
        diet    = profile.get("diet", "balanced")
        return tool_get_local_food_tips(city, country, diet)

    if any(kw in msg for kw in
           ["generate plan", "nutrition plan", "meal plan", "diet plan",
            "create plan", "my plan", "give me a plan"]):
        return tool_generate_nutrition_plan(profile)

    # Default: answer as a nutrition Q&A
    history = _session_memory.get(profile.get("session_id", ""), [])
    return tool_answer_nutrition_query(message, profile, history)


# ─────────────────────────────────────────────────────────────────────────────
# Public Agent Interface
# ─────────────────────────────────────────────────────────────────────────────

def run_agent(message: str, profile: dict, session_id: str) -> dict[str, Any]:
    """
    Main agentic loop entry point.

    Parameters
    ----------
    message    : User's natural-language input.
    profile    : Collected user profile dict.
    session_id : Unique session identifier for memory.

    Returns
    -------
    dict with keys: response (str), tool_used (str), safe (bool)
    """
    # ── PHASE 1: PERCEIVE — Input Validation ────────────────────────────────
    is_safe, error_msg = screen_input(message)
    if not is_safe:
        return {"response": error_msg, "tool_used": "guardrail_block", "safe": False}

    if not is_nutrition_related(message):
        return {
            "response": (
                "I'm NutriAI, your personal nutrition assistant! 🥗 "
                "I'm specialized in nutrition, diet planning, and health-related topics. "
                "Could you please ask me something related to food, nutrition, or your health goals? "
                "I'd love to help you with a personalized meal plan or answer your nutrition questions!"
            ),
            "tool_used": "off_topic_redirect",
            "safe": True,
        }

    # ── PHASE 2: REASON — Add context to profile ────────────────────────────
    profile["session_id"] = session_id

    # ── PHASE 3: ACT — Route to appropriate tool ────────────────────────────
    response = _route_to_tool(message, profile)

    # ── PHASE 4: REFLECT — Validate output ──────────────────────────────────
    if response.startswith("[ERROR]"):
        response = (
            "I encountered a technical issue connecting to the AI service. "
            "Please check your IBM credentials in the .env file, or the application "
            "will use its built-in knowledge base to assist you.\n\n"
            + tool_answer_nutrition_query(message, profile)
        )

    # ── PHASE 5: RESPOND — Update memory and return ─────────────────────────
    if session_id not in _session_memory:
        _session_memory[session_id] = []

    _session_memory[session_id].append({"role": "user", "content": message})
    _session_memory[session_id].append({"role": "assistant", "content": response[:500]})

    # Trim memory to MAX_HISTORY turns
    if len(_session_memory[session_id]) > MAX_HISTORY * 2:
        _session_memory[session_id] = _session_memory[session_id][-(MAX_HISTORY * 2):]

    tool_used = _detect_tool_used(message)
    return {"response": response, "tool_used": tool_used, "safe": True}


def generate_plan_for_profile(profile: dict) -> str:
    """Direct plan generation — called when user completes the profile form."""
    is_valid, err = validate_user_profile(profile)
    if not is_valid:
        return f"⚠️ Profile validation error: {err}"
    return tool_generate_nutrition_plan(profile)


def _detect_tool_used(message: str) -> str:
    msg = message.lower()
    if any(k in msg for k in ["bmi", "body mass"]):
        return "calculate_bmi"
    if any(k in msg for k in ["local food", "traditional food", "cuisine"]):
        return "get_local_food_tips"
    if any(k in msg for k in ["plan", "meal plan", "diet plan"]):
        return "generate_nutrition_plan"
    return "answer_nutrition_query"


def get_session_history(session_id: str) -> list:
    """Retrieve conversation history for a session."""
    return _session_memory.get(session_id, [])


def clear_session(session_id: str) -> None:
    """Clear memory for a given session."""
    if session_id in _session_memory:
        del _session_memory[session_id]
