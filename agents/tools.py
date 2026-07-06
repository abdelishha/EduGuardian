"""
EduGuardian — Tool Definitions
================================
All tools available to EduGuardian agents, implemented as
native ADK FunctionTools (no external MCP subprocess needed).

NOTE: ADK FunctionTool does NOT support default parameter values.
All parameters are required. Defaults are handled inside function bodies.
"""

import json
from datetime import datetime
from google.adk.tools import FunctionTool

# In-memory student history store
_student_history: list[dict] = []


def search_study_material(topic: str, grade_level: str) -> str:
    """
    Search for structured study material on any academic topic.

    Args:
        topic: The academic topic to explain (e.g. photosynthesis, quadratic equations)
        grade_level: The student level (e.g. middle school, high school, university)

    Returns:
        Structured teaching instructions for the topic.
    """
    if not grade_level:
        grade_level = "high school"

    _student_history.append({
        "timestamp": datetime.now().isoformat(),
        "type": "study",
        "topic": topic
    })

    return json.dumps({
        "tool": "search_study_material",
        "topic": topic,
        "grade_level": grade_level,
        "instructions": (
            f"Teach '{topic}' to a {grade_level} student using this structure:\n"
            "1. DEFINITION: Give a clear, simple one-sentence definition.\n"
            "2. ANALOGY: Explain using a relatable real-world comparison.\n"
            "3. KEY POINTS: List exactly 3 key facts or steps (numbered).\n"
            "4. PRACTICE QUESTION: End with one quiz question. Do NOT give the answer yet.\n"
            "5. HINT SYSTEM: If student is wrong, give 3 progressive hints before revealing the answer.\n"
            "Tone: Friendly, encouraging, patient. Never make the student feel bad."
        )
    })


def get_wellness_resources(stress_level: str, concern: str) -> str:
    """
    Get mental health support resources and coping strategies for a student.

    Args:
        stress_level: Assessed stress level - low, medium, high, or crisis
        concern: Specific concern (e.g. exams, social, sleep, overwhelmed)

    Returns:
        Wellness resources, coping strategies, and crisis escalation flag if needed.
    """
    if not concern:
        concern = "general"

    _student_history.append({
        "timestamp": datetime.now().isoformat(),
        "type": "wellness",
        "stress_level": stress_level,
        "concern": concern
    })

    crisis_keywords = ["crisis", "self-harm", "hopeless", "end it", "give up on life"]
    is_crisis = stress_level.lower() == "crisis" or any(k in concern.lower() for k in crisis_keywords)

    if is_crisis:
        return json.dumps({
            "tool": "get_wellness_resources",
            "stress_level": "crisis",
            "HUMAN_REVIEW_REQUIRED": True,
            "instructions": (
                "CRITICAL: This student may be in crisis. You MUST:\n"
                "1. Respond with immediate warmth and validation.\n"
                "2. Tell them they are not alone and their feelings matter.\n"
                "3. Share these emergency resources:\n"
                "   - Crisis Text Line: Text HOME to 741741 (US)\n"
                "   - International: https://www.iasp.info/resources/Crisis_Centres/\n"
                "   - Talk to a trusted adult: parent, teacher, school counselor\n"
                "4. Strongly encourage them to speak to a trusted adult right now.\n"
                "5. Do NOT attempt to handle this alone as an AI.\n"
                "6. Keep your response short, warm, and focused on getting them human help."
            )
        })

    strategies = {
        "low": [
            "Take a 5-minute breathing break: in for 4 counts, hold for 4, out for 4.",
            "Write down 3 things you are grateful for today.",
            "Drink a glass of water and stretch for 2 minutes."
        ],
        "medium": [
            "Try the Pomodoro Technique: 25 minutes of focused study, then a 5-minute break.",
            "Write your worries in a journal to get them out of your head.",
            "Call or text a friend for 10 minutes. Social connection reduces stress.",
            "Go for a 10-minute walk. Physical movement reduces anxiety."
        ],
        "high": [
            "Stop studying for now. Rest is not laziness, it is necessary for learning.",
            "Do the 5-4-3-2-1 grounding exercise: name 5 things you see, 4 you hear, 3 you can touch.",
            "Talk to someone you trust about how you are feeling.",
            "Remember: one exam does not define your future.",
            "Sleep is more important than cramming. A rested brain performs significantly better."
        ]
    }

    level = stress_level.lower()
    if level not in strategies:
        level = "medium"

    tips = "\n".join(f"   - {s}" for s in strategies[level][:3])
    return json.dumps({
        "tool": "get_wellness_resources",
        "stress_level": stress_level,
        "HUMAN_REVIEW_REQUIRED": False,
        "instructions": (
            f"Support this student feeling {stress_level} stress about '{concern}'.\n"
            "Steps:\n"
            "1. VALIDATE: Acknowledge their feelings with empathy (1-2 sentences).\n"
            "2. NORMALIZE: Let them know it is okay to feel this way.\n"
            f"3. STRATEGIES: Offer these coping strategies:\n{tips}\n"
            "4. ENCOURAGE: End with a genuine, specific encouragement.\n"
            "5. OFFER MORE: Ask if they want to talk more or need a study plan."
        )
    })


def save_study_plan(subjects: str, exam_date: str, daily_hours: float, preferred_time: str) -> str:
    """
    Create and save a personalized daily study plan for a student.

    Args:
        subjects: Comma-separated list of subjects (e.g. Math, Biology, History)
        exam_date: When the exams are (e.g. in 5 days, next Monday, July 10)
        daily_hours: How many hours per day the student can study (e.g. 2)
        preferred_time: Preferred study time - morning, afternoon, or evening

    Returns:
        A structured day-by-day study schedule with tips.
    """
    if not daily_hours or daily_hours <= 0:
        daily_hours = 2.0
    if not preferred_time:
        preferred_time = "evening"

    _student_history.append({
        "timestamp": datetime.now().isoformat(),
        "type": "study_plan",
        "subjects": subjects,
        "exam_date": exam_date
    })

    subject_list = [s.strip() for s in subjects.split(",")]
    num_subjects = len(subject_list)

    return json.dumps({
        "tool": "save_study_plan",
        "subjects": subject_list,
        "exam_date": exam_date,
        "daily_hours": daily_hours,
        "preferred_time": preferred_time,
        "instructions": (
            f"Create a detailed day-by-day study schedule for: {subjects}\n"
            f"Exam date: {exam_date} | Study time: {daily_hours} hours/day | Preferred: {preferred_time}\n\n"
            "Format:\n"
            "1. Brief encouraging intro (1 sentence)\n"
            "2. Day-by-day schedule with bold headings like **Day 1:**\n"
            f"   - Rotate through all {num_subjects} subjects\n"
            "   - Sessions of 45-60 minutes with 10-minute breaks\n"
            "   - Include specific times (e.g. 7:00 PM - 7:45 PM: Math)\n"
            "   - Use spaced repetition: revisit older material each day\n"
            "3. Include 2-3 study technique tips\n"
            "4. Add a motivational closing message\n"
            "Make it realistic. Do not overload the student."
        )
    })


def check_student_history(limit: int) -> str:
    """
    Retrieve recent interaction history for a student to personalize responses.

    Args:
        limit: How many recent history entries to retrieve (use 5 for standard queries)

    Returns:
        Recent student interactions as a JSON string.
    """
    if not limit or limit <= 0:
        limit = 5

    recent = _student_history[-limit:] if _student_history else []
    return json.dumps({
        "tool": "check_student_history",
        "history_count": len(recent),
        "recent_interactions": recent,
        "personalization_note": (
            "Use this history to personalize your response. "
            "Reference topics the student has studied before."
        )
    })


# Export as ADK FunctionTools
search_study_material_tool = FunctionTool(func=search_study_material)
get_wellness_resources_tool = FunctionTool(func=get_wellness_resources)
save_study_plan_tool = FunctionTool(func=save_study_plan)
check_student_history_tool = FunctionTool(func=check_student_history)

ALL_TOOLS = [
    search_study_material_tool,
    get_wellness_resources_tool,
    save_study_plan_tool,
    check_student_history_tool,
]
