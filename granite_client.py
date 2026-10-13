"""
granite_client.py
──────────────────────────────────────────────────────────────────────────────
IBM Granite LLM client wrapper using IBM watsonx.ai REST API.
Handles authentication, token management, and text generation.
"""

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# ── Configuration ─────────────────────────────────────────────────────────────
IBM_API_KEY      = os.getenv("IBM_API_KEY", "")
IBM_PROJECT_ID   = os.getenv("IBM_PROJECT_ID", "")
IBM_URL          = os.getenv("IBM_URL", "https://us-south.ml.cloud.ibm.com")
GRANITE_MODEL_ID = os.getenv("GRANITE_MODEL_ID", "ibm/granite-13b-instruct-v2")

IAM_TOKEN_URL    = "https://iam.cloud.ibm.com/identity/token"
GENERATE_URL     = f"{IBM_URL}/ml/v1/text/generation?version=2023-05-29"

# ── Token cache ───────────────────────────────────────────────────────────────
_token_cache = {"token": None, "expires_at": 0}


def _get_iam_token() -> str:
    """Fetch (or return cached) IAM bearer token."""
    now = time.time()
    if _token_cache["token"] and now < _token_cache["expires_at"] - 60:
        return _token_cache["token"]

    resp = requests.post(
        IAM_TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": IBM_API_KEY,
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    _token_cache["token"] = data["access_token"]
    _token_cache["expires_at"] = now + data.get("expires_in", 3600)
    return _token_cache["token"]


def generate_text(prompt: str, max_new_tokens: int = 1024,
                  temperature: float = 0.7, top_p: float = 0.9) -> str:
    """
    Send a prompt to IBM Granite and return the generated text.

    Parameters
    ----------
    prompt          : The instruction/chat prompt to send.
    max_new_tokens  : Maximum tokens to generate.
    temperature     : Sampling temperature (0 = deterministic).
    top_p           : Nucleus sampling threshold.

    Returns
    -------
    Generated text string, or an error message prefixed with [ERROR].
    """
    if not IBM_API_KEY or not IBM_PROJECT_ID:
        # ── Demo / offline fallback ───────────────────────────────────────────
        return _offline_fallback(prompt)

    try:
        token = _get_iam_token()
        payload = {
            "model_id": GRANITE_MODEL_ID,
            "project_id": IBM_PROJECT_ID,
            "input": prompt,
            "parameters": {
                "decoding_method": "sample",
                "max_new_tokens": max_new_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "repetition_penalty": 1.1,
            },
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        resp = requests.post(GENERATE_URL, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        result = resp.json()
        generated = result["results"][0]["generated_text"].strip()
        return generated

    except requests.exceptions.RequestException as exc:
        return f"[ERROR] IBM Granite API call failed: {exc}"
    except (KeyError, IndexError) as exc:
        return f"[ERROR] Unexpected response format: {exc}"


# ── Offline / demo fallback (no credentials required) ────────────────────────
def _offline_fallback(prompt: str) -> str:
    """
    Return a structured demo response when IBM credentials are not configured.
    This lets the application run and be evaluated without live API access.
    """
    prompt_lower = prompt.lower()

    if "nutrition plan" in prompt_lower or "meal plan" in prompt_lower:
        return _demo_nutrition_plan(prompt)
    elif any(w in prompt_lower for w in ["query", "question", "ask", "what", "how", "why", "is ", "can "]):
        return _demo_query_response(prompt)
    else:
        return _demo_nutrition_plan(prompt)


def _demo_nutrition_plan(prompt: str) -> str:
    """Generate a realistic-looking demo nutrition plan."""
    return """## Personalized Nutrition Plan

### Daily Caloric & Macro Targets
| Nutrient | Daily Target |
|----------|-------------|
| Calories | 1,800 – 2,000 kcal |
| Protein  | 70 – 90 g |
| Carbohydrates | 200 – 220 g |
| Healthy Fats  | 55 – 65 g |
| Fiber    | 25 – 30 g |
| Water    | 8 – 10 glasses (2–2.5 L) |

---

### 🌅 Breakfast (7:00 – 8:00 AM)
- **Option A:** Oatmeal with chia seeds, sliced banana, and a handful of walnuts + 1 glass of warm water with lemon
- **Option B:** Whole-grain toast with avocado + 2 boiled eggs + green tea
- **Option C:** Greek yogurt with mixed berries and flaxseeds

### 🌞 Mid-Morning Snack (10:30 AM)
- A handful of almonds (10–12 pieces)
- 1 seasonal fruit (apple / pear / guava)
- Herbal tea or infused water

### 🍽️ Lunch (12:30 – 1:30 PM)
- **Option A:** Brown rice + lentil dal + mixed vegetable curry + cucumber-tomato salad
- **Option B:** Quinoa bowl with roasted chickpeas, leafy greens, lemon-tahini dressing
- **Option C:** Whole-wheat roti (2) + rajma / kidney bean curry + raita

### ☀️ Afternoon Snack (3:30 – 4:00 PM)
- 1 cup buttermilk (chaas) OR coconut water
- Roasted chana / sprouts salad

### 🌙 Dinner (7:00 – 8:00 PM)
- **Option A:** Moong dal khichdi (light) + steamed vegetables + a small bowl of curd
- **Option B:** Vegetable soup + 1–2 multigrain rotis + stir-fried greens (spinach / kale)
- **Option C:** Baked tofu / paneer tikka + quinoa + salad

### 🌛 Post-Dinner (Optional, if hungry)
- Warm turmeric milk (golden milk) — anti-inflammatory benefit
- OR a small bowl of mixed fruit

---

### 💧 Hydration Schedule
| Time | Recommendation |
|------|---------------|
| Wake-up | 1–2 glasses of warm water |
| Before each meal | 1 glass (15 min before) |
| Between meals | Sip water steadily |
| Evening | Herbal tea / infused water |

---

### 🌿 Key Nutritional Guidelines
1. **Prefer whole, unprocessed foods** over packaged/refined options.
2. **Eat mindfully** — chew slowly, avoid screens during meals.
3. **Include seasonal local produce** for maximum nutrient freshness.
4. **Reduce salt** — use herbs and spices (turmeric, cumin, coriander) instead.
5. **Limit sugar** — avoid sugary beverages, opt for natural sweeteners sparingly.
6. **Space meals 3–4 hours apart** to maintain stable blood sugar.

---

### 🏃 Lifestyle & Activity Recommendations
- Aim for **30 minutes of moderate exercise** (walking, yoga, cycling) 5 days a week.
- Prioritize **7–8 hours of quality sleep** nightly.
- Practice **stress-reduction techniques** (deep breathing, meditation).
- Maintain a **food journal** to track progress.

---

### 📋 Foods to Emphasize
✅ Leafy greens (spinach, methi, kale) | ✅ Legumes (lentils, chickpeas, beans)
✅ Whole grains (oats, quinoa, brown rice) | ✅ Nuts & seeds (almonds, walnuts, flaxseeds)
✅ Low-fat dairy or plant-based alternatives | ✅ Seasonal fruits

### ❌ Foods to Limit / Avoid
❌ Refined flour (maida) products | ❌ Processed and packaged snacks
❌ Sugary drinks and sodas | ❌ Excessive red meat (if applicable)
❌ Deep-fried foods | ❌ Alcohol and tobacco
"""


def _demo_query_response(prompt: str) -> str:
    """Generate a demo response for general nutrition queries."""
    prompt_lower = prompt.lower()

    if "diabetes" in prompt_lower or "sugar" in prompt_lower:
        return """**Managing Nutrition with Diabetes**

For individuals with diabetes, nutrition management is crucial:

1. **Choose low glycemic index (GI) foods** — whole grains, legumes, non-starchy vegetables.
2. **Control portion sizes** — use the plate method (½ vegetables, ¼ protein, ¼ whole grains).
3. **Limit refined carbohydrates** — white bread, white rice, sugary snacks.
4. **Increase fiber intake** — slows glucose absorption and improves insulin sensitivity.
5. **Include healthy fats** — avocado, nuts, olive oil (in moderation).
6. **Stay well hydrated** — water is best; avoid sugary beverages.
7. **Eat at regular intervals** — prevents blood sugar spikes and crashes.
8. **Monitor carbohydrate intake** — aim for consistent carb distribution across meals.

*Always consult your endocrinologist or registered dietitian for a personalized diabetes management plan.*"""

    elif "blood pressure" in prompt_lower or "hypertension" in prompt_lower:
        return """**Nutrition for Blood Pressure Management (DASH Diet Principles)**

1. **Reduce sodium (salt)** — aim for less than 2,300 mg/day; ideally 1,500 mg/day.
2. **Increase potassium-rich foods** — bananas, sweet potatoes, spinach, beans.
3. **Eat plenty of fruits and vegetables** — at least 8–10 servings daily.
4. **Choose whole grains** over refined grains.
5. **Include low-fat dairy** for calcium and magnesium.
6. **Limit alcohol** — no more than 1 drink/day for women, 2 for men.
7. **Reduce saturated and trans fats** — opt for healthy fats (olive oil, nuts).
8. **Maintain a healthy weight** — even modest weight loss reduces blood pressure.

*Please consult your cardiologist before making significant dietary changes.*"""

    elif "weight loss" in prompt_lower or "lose weight" in prompt_lower:
        return """**Evidence-Based Nutrition for Healthy Weight Management**

1. **Create a moderate calorie deficit** — 300–500 kcal/day below maintenance.
2. **Prioritize protein** — 1.2–1.6 g/kg body weight helps preserve muscle.
3. **Eat high-volume, low-calorie foods** — vegetables, leafy greens, fruits.
4. **Limit ultra-processed foods** — they promote overeating and fat storage.
5. **Practice mindful eating** — eat slowly, recognize hunger/satiety cues.
6. **Don't skip meals** — especially breakfast; it helps regulate appetite.
7. **Stay active** — combine cardio with strength training for best results.
8. **Stay hydrated** — sometimes thirst is mistaken for hunger.

*Sustainable weight loss is 0.5–1 kg per week. Rapid diets are not recommended.*"""

    else:
        return """**General Nutrition Guidance**

Maintaining good nutrition is foundational to health and wellbeing. Here are evidence-based principles:

1. **Eat a balanced, varied diet** — include all food groups in appropriate portions.
2. **Focus on whole foods** — minimize ultra-processed and packaged foods.
3. **Stay hydrated** — drink 8–10 glasses of water daily.
4. **Include colorful vegetables** — different colors provide different micronutrients.
5. **Choose healthy fats** — omega-3s from flaxseeds, walnuts, and fatty fish.
6. **Moderate your portions** — use smaller plates and practice mindful eating.
7. **Limit added sugar and sodium** — these contribute to chronic disease risk.
8. **Maintain regular meal times** — helps regulate metabolism and hormones.

For personalized guidance, always consult a registered dietitian or nutritionist in your area."""
