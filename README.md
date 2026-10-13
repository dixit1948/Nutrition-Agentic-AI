# 🥗 NutriAI — IBM Granite Nutrition Agent

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)
![IBM Granite](https://img.shields.io/badge/IBM%20Granite-LLM-054ADA?logo=ibm&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Agentic AI](https://img.shields.io/badge/Agentic-AI-purple)

**Personalized AI-powered Nutrition Planning using IBM Granite LLM**

[Live Demo](#-quick-start) · [Features](#-features) · [Architecture](#-architecture) · [API Docs](#-api-reference) · [Deploy](#-deployment)

</div>

---

## 📖 Overview

**NutriAI** is a full-stack **Agentic AI** web application that generates science-backed, culturally aware, and medically mindful personalized nutrition plans. It collects user details — name, age, diet preference, medical history, and location — then uses **IBM Granite LLM** via watsonx.ai to craft detailed, actionable meal plans with proper guardrails and medical disclaimers.

### 🎯 Key Highlights
- **IBM Granite LLM** (watsonx.ai) for intelligent, evidence-based nutrition guidance
- **5-phase Agentic AI loop**: Perceive → Reason → Act → Reflect → Respond
- **4 Agentic Tools**: Plan Generator, Q&A Engine, Local Food Advisor, BMI Calculator
- **AI Ethics & Guardrails**: HAM principles, harmful content filtering, medical disclaimers
- **Demo Mode**: Fully functional without IBM credentials — built-in knowledge base
- **Plan Persistence**: Download your plan as a `.md` Markdown file

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **IBM Granite LLM** | Enterprise-grade AI via watsonx.ai REST API with token caching |
| 👤 **User Profiling** | Name, age, diet, 12 medical conditions, location, weight, height, goals |
| 📋 **Personalized Plans** | Complete meal plans with macros, micros, hydration & cultural food choices |
| 🏥 **Medical Awareness** | Diabetes, hypertension, kidney disease, thyroid, PCOS and more |
| 🌍 **Cultural Sensitivity** | Locally available foods based on user's city and country |
| 🛡️ **AI Guardrails** | Input screening, output filtering, HAM tone, bias mitigation |
| 💬 **Agentic Chatbot** | Multi-turn conversation with session memory and quick prompts |
| 📊 **BMI Calculator** | Integrated tool with health classification and recommendations |
| 💾 **Save as .md** | Download personalized plans as Markdown files |
| 🔄 **Demo Mode** | Full functionality without IBM API credentials |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web Browser (SPA)                    │
│          index.html + style.css + app.js                │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP REST API
┌───────────────────────▼─────────────────────────────────┐
│             Flask Backend  (app.py)                     │
│  POST /api/generate-plan   POST /api/chat               │
│  GET  /api/plans           GET  /api/health             │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│          Agentic AI Engine  (agent.py)                  │
│                                                         │
│   PERCEIVE → REASON → ACT → REFLECT → RESPOND          │
│                                                         │
│   Tools: generate_plan | answer_query |                 │
│           local_food_tips | calculate_bmi               │
└──────┬────────────────┬───────────────┬─────────────────┘
       │                │               │
  guardrails.py   granite_client.py  plan_saver.py
  (safety/HAM)    (IBM Granite API)  (.md files)
```

---

## 📁 Project Structure

```
Nutrition-Agentic-AI/
├── app.py                  # Flask backend — REST API (6 endpoints)
├── agent.py                # Agentic loop + 4 tools + session memory
├── granite_client.py       # IBM Granite LLM client + demo fallback
├── guardrails.py           # AI ethics, safety filters, HAM tone
├── plan_saver.py           # Markdown (.md) plan persistence
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── run.bat                 # One-click Windows launcher
├── sample_plan_output.md   # Reference output example
├── README.md               # This file
└── static/
    ├── index.html          # Single-page app (5 tabs)
    ├── style.css           # Responsive CSS (green nutrition theme)
    └── app.js              # Frontend JS — API calls, chat, Markdown
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** — [Download](https://www.python.org/downloads/)
- **pip** (comes with Python)
- **Git** — [Download](https://git-scm.com/)
- IBM watsonx.ai credentials *(optional — app works in Demo Mode without them)*

---

### Option 1: Windows — Double-Click Launcher

```
1. Clone or download this repository
2. Open the project folder
3. Double-click  run.bat
4. Browser opens automatically at http://localhost:5000
```

The `.bat` file handles everything: creates a virtual environment, installs all dependencies, copies `.env.example` → `.env`, and starts the Flask server.

---

### Option 2: Manual Setup (All Platforms)

```bash
# 1. Clone the repository
git clone https://github.com/dixit1948/Nutrition-Agentic-AI.git
cd Nutrition-Agentic-AI

# 2. Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env          # Windows
cp   .env.example .env          # macOS / Linux

# 5. (Optional) Add IBM credentials to .env
#    See Configuration section below

# 6. Start the application
python app.py

# 7. Open browser → http://localhost:5000
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and fill in your IBM watsonx.ai credentials:

```env
# IBM watsonx.ai credentials
IBM_API_KEY=your_ibm_api_key_here
IBM_PROJECT_ID=your_ibm_project_id_here
IBM_URL=https://us-south.ml.cloud.ibm.com

# IBM Granite model
GRANITE_MODEL_ID=ibm/granite-13b-instruct-v2

# Flask
FLASK_SECRET_KEY=nutrition-ai-secret-2024
PORT=5000
```

### Getting IBM watsonx.ai Credentials

1. Sign in / create account at [IBM Cloud](https://cloud.ibm.com)
2. Create a **watsonx.ai** service instance
3. Navigate to **IAM → API Keys** → create a new API key
4. Copy your **Project ID** from the watsonx.ai console

> **No credentials?** The app runs in **Demo Mode** — all features remain fully functional using the built-in nutrition knowledge base.

---

## 🔄 Agentic AI SDLC Phases

### Phase 1 — Requirements & Problem Definition
- Users need personalized nutrition guidance considering medical conditions, culture, and location
- Solution: Agentic AI with IBM Granite that perceives context and generates tailored plans
- Ethics: Apply HAM (Helpful, Accurate, Mindful) principles with strict guardrails

### Phase 2 — Design
- Multi-tool agentic system with in-process session memory
- Intent-based tool router for dynamic tool selection
- Layered guardrails: input → LLM → output → response

### Phase 3 — Development
- `agent.py`: Full Perceive→Reason→Act→Reflect→Respond loop
- `granite_client.py`: IBM Granite via watsonx.ai REST API with IAM token caching
- `guardrails.py`: Harmful content blocking, HAM tone, medical disclaimers
- `plan_saver.py`: Markdown file persistence with user profile metadata

### Phase 4 — Testing & Validation
- `/api/health` endpoint for service status monitoring
- Input validation at frontend (HTML5) + backend (Python) layers
- Demo mode for testing without live API credentials
- Guardrail edge-case coverage (harmful, off-topic, invalid profile inputs)

### Phase 5 — Deployment & Monitoring
- `run.bat` single-command launcher for Windows
- GitHub repository for version control and sharing
- Session-based memory management with automatic cleanup
- All plans persisted as `.md` files for auditability

---

## 🔧 Agentic Tools

| Tool | Trigger Keywords | Purpose |
|------|-----------------|---------|
| `generate_nutrition_plan` | "plan", "meal plan", "diet plan" | Full personalized meal plan with macros |
| `answer_nutrition_query` | Any nutrition question | Context-aware Q&A with memory |
| `get_local_food_tips` | "local food", "cuisine", "traditional" | Regional & cultural food recommendations |
| `calculate_bmi` | "bmi", "body mass" | BMI score, category & health recommendation |

---

## 🔌 API Reference

### `GET /api/health`
Returns service status and IBM Granite configuration mode.

```json
{
  "status": "healthy",
  "service": "NutriAI — IBM Granite Nutrition Agent",
  "version": "1.0.0",
  "ibm_granite_configured": false,
  "mode": "demo"
}
```

### `POST /api/generate-plan`

**Request:**
```json
{
  "name": "Priya Sharma",
  "age": "32",
  "diet": "veg",
  "medical_history": "Type 2 Diabetes, High Blood Pressure",
  "city": "Mumbai",
  "country": "India",
  "goals": "manage blood sugar levels",
  "weight": "68",
  "height": "162"
}
```

**Response:**
```json
{
  "plan": "## Personalized Nutrition Plan...",
  "filename": "nutrition_plan_Priya_Sharma_20241201_143022.md",
  "session_id": "uuid",
  "status": "success"
}
```

### `POST /api/chat`

**Request:**
```json
{
  "message": "What foods should I avoid with diabetes?",
  "profile": { "name": "Priya", "age": "32", "diet": "veg", "..." : "..." },
  "session_id": "uuid"
}
```

**Response:**
```json
{
  "response": "...",
  "tool_used": "answer_nutrition_query",
  "safe": true,
  "session_id": "uuid"
}
```

### Other Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/plans` | GET | List all saved `.md` plan files |
| `/api/plans/<filename>` | GET | Download a specific plan |
| `/api/session/<id>` | GET | Get conversation history |
| `/api/session/<id>` | DELETE | Clear session memory |

---

## 🛡️ AI Ethics & Guardrails

NutriAI implements responsible AI principles at every layer:

### Input Guardrails
- ✅ Blocks self-harm, dangerous diets, and harmful content
- ✅ Validates user profile (age range, diet type, required fields)
- ✅ Input length limit (5,000 characters) to prevent prompt injection
- ✅ Off-topic redirect for non-nutrition queries

### Output Guardrails
- ✅ Filters dangerous medical claims (e.g., "stop your medication")
- ✅ Enforces HAM (**H**elpful, **A**ccurate, **M**indful) tone
- ✅ Auto-appends medical disclaimer to every plan and response
- ✅ No definitive disease cure claims

### Ethical AI Principles
- **Bias mitigation**: Culturally inclusive, no stereotype-based dietary assumptions
- **Transparency**: Clearly labeled as AI-generated, not medical advice
- **Privacy**: No PII stored beyond the current session
- **Accountability**: All plans saved with metadata for auditability

---

## 🖥️ Web Application — Screenshots Description

The SPA has 5 tabs:

1. **Home** — Hero banner, feature cards, SDLC phase display
2. **Profile** — Multi-section form: personal info, diet, medical conditions (12 checkboxes), location
3. **My Plan** — Rendered Markdown plan with download button and follow-up chat link
4. **Chat** — Real-time chatbot with quick prompts, typing indicator, and tool badge
5. **Saved Plans** — Grid of all downloaded plan files with metadata

---

## 🏭 Technology Stack

| Layer | Technology |
|-------|-----------|
| AI Model | IBM Granite 13B Instruct (ibm/granite-13b-instruct-v2) |
| AI Platform | IBM watsonx.ai (REST API v2023-05-29) |
| Authentication | IBM IAM (token-based, cached) |
| Backend | Python 3.9+ / Flask 3.0 / Flask-CORS |
| Frontend | HTML5 / CSS3 / Vanilla JavaScript |
| Markdown Rendering | Marked.js (CDN) |
| Plan Storage | Local filesystem (`.md` files) |
| Launcher | Windows Batch script (`run.bat`) |

---

## ⚠️ Medical Disclaimer

> This application is powered by **IBM Granite AI** and provides nutritional information for **educational purposes only**. It is **NOT** a substitute for professional medical advice, diagnosis, or treatment.
>
> Always consult a qualified **physician, registered dietitian, or licensed nutritionist** before making significant dietary changes, especially if you have pre-existing medical conditions (diabetes, hypertension, kidney disease, heart disease, etc.).
>
> In case of a medical emergency, contact your local emergency services immediately.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

<div align="center">

Built with ❤️ using **IBM Granite LLM** · Agentic AI · Flask · HAM Principles · Responsible AI

</div>
