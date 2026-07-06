"""
EduGuardian MCP Server
======================
This is the Model Context Protocol (MCP) server for EduGuardian.
It acts as the "hands" of our AI agents — exposing 4 tools that any
agent can call to get data, save plans, and find resources.

Tools exposed:
  1. search_study_material  — Find explanations for any topic
  2. get_wellness_resources — Get mental health tips and coping strategies
  3. save_study_plan        — Save a student's study schedule
  4. check_student_history  — Recall what the student previously asked/studied
"""

# Fix Windows encoding so this subprocess handles all characters correctly
import sys
import io
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from mcp.server.fastmcp import FastMCP
from datetime import datetime
import json
import os

# -----------------------------------------------------------------
# Initialize the MCP server with a friendly name
# -----------------------------------------------------------------
mcp = FastMCP("EduGuardian MCP Server")

# Simple in-memory store for student history and study plans
# (In a real app, this would be a database)
_student_history: list[dict] = []
_study_plans: list[dict] = []

# -----------------------------------------------------------------
# TOOL 1: Search Study Material
# -----------------------------------------------------------------
@mcp.tool()
def search_study_material(topic: str, grade_level: str = "high school") -> str:
    """
    Search for study material and explanations for a given academic topic.
    
    Args:
        topic: The subject or concept the student wants to learn (e.g. 'photosynthesis', 'quadratic equations')
        grade_level: The student's approximate grade level (default: 'high school')
    
    Returns:
        A structured explanation of the topic with key points and a study tip.
    """
    # Log this interaction for history
    _student_history.append({
        "timestamp": datetime.now().isoformat(),
        "type": "study",
        "topic": topic,
        "grade_level": grade_level
    })
    
    # Return structured guidance that the Tutor Agent will use
    return json.dumps({
        "topic": topic,
        "grade_level": grade_level,
        "instruction": (
            f"Provide a clear, beginner-friendly explanation of '{topic}' "
            f"suitable for {grade_level} students. "
            "Structure your response with: "
            "1) A simple definition, "
            "2) A real-world analogy, "
            "3) Three key points to remember, "
            "4) One practice question with the answer. "
            "Use encouraging and supportive language."
        ),
        "status": "ready"
    })


# -----------------------------------------------------------------
# TOOL 2: Get Wellness Resources
# -----------------------------------------------------------------
@mcp.tool()
def get_wellness_resources(stress_level: str, concern: str = "general") -> str:
    """
    Retrieve mental wellness tips and coping strategies for students.
    
    Args:
        stress_level: How stressed the student is — 'low', 'medium', 'high', or 'crisis'
        concern: What they are stressed about (e.g. 'exams', 'social pressure', 'family')
    
    Returns:
        Age-appropriate wellness resources and coping strategies.
        If stress_level is 'crisis', returns a HUMAN_REVIEW_REQUIRED flag for safety.
    """
    # Log wellness check
    _student_history.append({
        "timestamp": datetime.now().isoformat(),
        "type": "wellness_check",
        "stress_level": stress_level,
        "concern": concern
    })
    
    # SAFETY FEATURE: Human-in-the-loop for crisis situations
    if stress_level.lower() == "crisis":
        return json.dumps({
            "HUMAN_REVIEW_REQUIRED": True,
            "message": (
                "This student may need immediate human support. "
                "Please refer them to: "
                "International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/ "
                "Crisis Text Line: Text HOME to 741741. "
                "Always validate their feelings first and encourage them to talk to a trusted adult."
            ),
            "immediate_response": (
                "I hear you, and I'm really glad you told me how you're feeling. "
                "You are not alone. Please talk to a trusted adult right now — "
                "a parent, teacher, or school counselor. Your feelings matter and help is available."
            )
        })
    
    # Standard wellness resources
    strategies = {
        "low": [
            "Take a 5-minute stretch break every 45 minutes of studying",
            "Try the 4-7-8 breathing technique: breathe in for 4 seconds, hold for 7, out for 8",
            "Write down 3 things you are grateful for today",
        ],
        "medium": [
            "Break your tasks into smaller 25-minute chunks (Pomodoro technique)",
            "Go for a 10-minute walk outside to reset your mind",
            "Talk to a friend or family member about how you're feeling",
            "Remember: it's okay to not be perfect. Progress matters more than perfection.",
        ],
        "high": [
            "Pause everything. Take 10 slow, deep breaths right now.",
            "Write your worries on paper — getting them out of your head helps",
            "Prioritize: what is ONE thing you can do today? Focus only on that.",
            "Consider speaking with your school counselor or a trusted teacher",
            "Remember past challenges you've overcome — you are stronger than you think.",
        ]
    }
    
    level = stress_level.lower() if stress_level.lower() in strategies else "medium"
    
    return json.dumps({
        "stress_level": level,
        "concern": concern,
        "coping_strategies": strategies[level],
        "affirmation": "You are doing better than you think. Every small step counts.",
        "instruction": (
            f"The student is feeling {level} stress about '{concern}'. "
            "Respond with warmth and empathy first, THEN gently introduce these strategies. "
            "Never dismiss their feelings. End with an encouraging affirmation."
        )
    })


# -----------------------------------------------------------------
# TOOL 3: Save Study Plan
# -----------------------------------------------------------------
@mcp.tool()
def save_study_plan(
    subjects: str,
    exam_date: str,
    daily_hours: int = 2,
    preferred_time: str = "evening"
) -> str:
    """
    Create and save a personalized study plan for the student.
    
    Args:
        subjects: Comma-separated list of subjects to study (e.g. 'Math, Biology, History')
        exam_date: When the exam or deadline is (e.g. 'July 10', 'next Monday')
        daily_hours: How many hours per day the student can study (default: 2)
        preferred_time: Preferred study time — 'morning', 'afternoon', or 'evening'
    
    Returns:
        A structured weekly study plan with breaks and tips.
    """
    subject_list = [s.strip() for s in subjects.split(",")]
    
    plan = {
        "created_at": datetime.now().isoformat(),
        "exam_date": exam_date,
        "daily_study_hours": daily_hours,
        "preferred_time": preferred_time,
        "subjects": subject_list,
        "schedule_note": (
            f"Study plan for: {', '.join(subject_list)}. "
            f"Daily commitment: {daily_hours} hours in the {preferred_time}. "
            f"Target date: {exam_date}."
        )
    }
    
    _study_plans.append(plan)
    
    return json.dumps({
        "status": "saved",
        "plan": plan,
        "instruction": (
            f"Create a detailed, motivating {daily_hours}-hour daily study schedule "
            f"for the subjects: {subjects}. The student prefers studying in the {preferred_time}. "
            f"Exam/deadline is: {exam_date}. "
            "Include: specific time blocks for each subject, 5-10 minute breaks every 45 minutes, "
            "one longer rest break, a daily review session at the end. "
            "Format it as a clear, easy-to-follow timetable. Be encouraging and realistic."
        )
    })


# -----------------------------------------------------------------
# TOOL 4: Check Student History
# -----------------------------------------------------------------
@mcp.tool()
def check_student_history(limit: int = 5) -> str:
    """
    Retrieve the student's recent interaction history to personalize responses.
    
    Args:
        limit: How many recent interactions to retrieve (default: 5)
    
    Returns:
        A summary of recent topics studied and wellness checks.
    """
    recent = _student_history[-limit:] if len(_student_history) >= limit else _student_history
    
    if not recent:
        return json.dumps({
            "history": [],
            "summary": "This appears to be a new student with no previous history."
        })
    
    topics = [h.get("topic", "") for h in recent if h.get("type") == "study" and h.get("topic")]
    wellness_checks = [h for h in recent if h.get("type") == "wellness_check"]
    
    return json.dumps({
        "total_interactions": len(_student_history),
        "recent_topics_studied": topics,
        "wellness_checks_count": len(wellness_checks),
        "last_interaction": recent[-1] if recent else None,
        "summary": (
            f"Student has had {len(_student_history)} total interactions. "
            f"Recently studied: {', '.join(topics) if topics else 'nothing yet'}. "
            f"Had {len(wellness_checks)} wellness check-ins."
        )
    })


# -----------------------------------------------------------------
# Run the MCP server (stdio transport for local use)
# -----------------------------------------------------------------
if __name__ == "__main__":
    print("[OK] EduGuardian MCP Server is running...")
    mcp.run(transport="stdio")
