# EduGuardian 🎓
## Multi-Agent AI Study Companion & Mental Wellness Advisor

[![ADK](https://img.shields.io/badge/Google%20ADK-Multi--Agent-blue)](https://github.com/google/adk-python)
[![MCP](https://img.shields.io/badge/MCP-Server-purple)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/Python-3.10+-green)](https://python.org)

---

## 🌟 What is EduGuardian?

EduGuardian is a **24/7 AI-powered study companion and mental wellness advisor** for students. 
It combines a team of **4 specialized AI agents** to help students:

- 📚 **Understand** any academic subject with clear explanations and quizzes
- 🧘 **Manage** exam stress and emotional wellbeing safely
- 📅 **Plan** personalized study schedules based on their goals
- 🛡️ **Stay safe** with crisis detection and human-in-the-loop escalation

---

## 🧠 Architecture: 4-Agent Multi-Agent System

```
User
 │
 ▼
Orchestrator Agent (EduGuardian)
 ├── Tutor Agent         ← Academic help, quizzes, hints
 ├── Wellness Agent      ← Stress support, crisis detection (HITL)
 └── Study Plan Agent    ← Personalized schedules
         │
         ▼
    MCP Server (edu_mcp_server.py)
         │
         ├── search_study_material()
         ├── get_wellness_resources()
         ├── save_study_plan()
         └── check_student_history()
```

---

## ✅ Course Concepts Demonstrated

| Concept | Implementation |
|---|---|
| **Multi-Agent System (ADK)** | 4 agents: Orchestrator + 3 specialists |
| **MCP Server** | Custom FastMCP server with 4 tools |
| **Agent Skills** | Each agent has specialized, composable instructions |
| **Security / HITL** | Wellness agent detects crisis and escalates to human |

---

## 🚀 Quick Start

### Step 1: Get a Google API Key
1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Click **"Get API Key"**
3. Copy your key

### Step 2: Set up the project
```powershell
# Navigate to the project folder
cd "c:\Downloads\New folder (3)\edu-guardian"

# Create a virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure your API key
```powershell
# Copy the example env file
copy .env.example .env

# Open .env in Notepad and paste your API key
notepad .env
```

### Step 4: Run EduGuardian
```powershell
python main.py
```

### Step 5: Open in browser
Visit: **http://localhost:5000** 🎉

---

## 📁 Project Structure

```
edu-guardian/
├── agents/
│   ├── __init__.py
│   ├── orchestrator_agent.py   ← Root agent, routes requests
│   ├── tutor_agent.py          ← Academic expert
│   ├── wellness_agent.py       ← Mental health counselor
│   └── study_plan_agent.py     ← Schedule coach
│
├── mcp_server/
│   ├── __init__.py
│   └── edu_mcp_server.py       ← FastMCP server with 4 tools
│
├── ui/
│   ├── index.html              ← Web interface
│   ├── style.css               ← Premium dark-mode design
│   └── app.js                  ← Frontend logic
│
├── main.py                     ← Entry point
├── requirements.txt            ← Dependencies
├── .env.example                ← API key template
└── README.md                   ← This file
```

---

## 🛡️ Safety Features

EduGuardian implements **Human-in-the-Loop (HITL)** safety:

- The Wellness Agent continuously monitors for crisis signals in student messages
- If detected, it **immediately escalates** to human support resources
- Emergency contacts and crisis lines are provided instantly
- The agent clearly communicates its limitations as an AI

---

## 🔗 Links

- **Live Demo**: [YouTube Demo Video]
- **GitHub**: [This repository]

---

## 👤 Author

Built with ❤️
