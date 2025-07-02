"""
tools.py
========

Specialist agents implemented as tools for the multi-agent orchestrator.
Each specialist is a domain expert that can be plugged into the main agent.
"""

import platform
import os
from strands import Agent
from strands.tools import tool
from strands_tools import calculator, http_request
from bedrock_model import bedrock_model

# Conditional imports for platform-specific tools
try:
    # These tools may use fcntl on Unix systems
    from strands_tools import python_repl, shell
    UNIX_TOOLS_AVAILABLE = True
except ImportError:
    # Fallback for Windows - these tools use fcntl which isn't available
    UNIX_TOOLS_AVAILABLE = False
    print("⚠️  Warning: shell and python_repl tools not available on Windows")

# System prompts for each specialist
MATH_ASSISTANT_PROMPT = (
    "You are Math Assistant, an expert at solving mathematical problems. "
    "Always show detailed workings and explanations. Use the calculator tool "
    "for complex calculations when needed."
)

COMPUTER_SCIENCE_ASSISTANT_PROMPT = (
    "You are Computer Science Assistant, an expert in programming and technical concepts. "
    "Write clean, well-documented code and explain technical concepts clearly. "
    "Note: Some interactive tools may not be available on Windows systems."
)

LANGUAGE_ASSISTANT_PROMPT = (
    "You are Language Assistant, skilled at translation and linguistic queries. "
    "Provide clear, culturally appropriate answers. Use http_request tool "
    "for accessing translation APIs when needed."
)

WEB_RESEARCH_ASSISTANT_PROMPT = (
    "You are Web Research Assistant, specialized in finding and analyzing information online. "
    "Use http_request tool to gather data from APIs and web services. "
    "Always cite your sources and provide accurate, up-to-date information."
)

GENERAL_ASSISTANT_PROMPT = (
    "You are General Assistant. Provide concise, accurate answers to "
    "non-specialized questions. You have access to basic tools for calculations "
    "and simple tasks."
)

# Load the calendar system prompt
with open('calendar_prompt.txt', 'r') as f:
    CALENDAR_SYSTEM_PROMPT = f.read()

@tool
def math_assistant(query: str) -> str:
    """
    Handle mathematics-related questions and calculations.
    
    Args:
        query (str): The mathematical question or problem to solve
        
    Returns:
        str: Detailed solution with step-by-step explanations
    """
    print("🔢 Routed to Math Assistant")
    
    # Use available tools based on platform
    tools = [calculator]
    if UNIX_TOOLS_AVAILABLE:
        tools.append(python_repl)
    
    math_agent = Agent(
        system_prompt=MATH_ASSISTANT_PROMPT,
        tools=tools
    )
    return math_agent(query)


@tool
def computer_science_assistant(query: str) -> str:
    """
    Handle programming and computer science related queries.
    
    Args:
        query (str): The programming or CS question
        
    Returns:
        str: Code examples, explanations, and technical guidance
    """
    print("💻 Routed to Computer Science Assistant")
    
    # Use available tools based on platform
    tools = [calculator]
    if UNIX_TOOLS_AVAILABLE:
        tools.extend([python_repl, shell])
    
    cs_agent = Agent(
        system_prompt=COMPUTER_SCIENCE_ASSISTANT_PROMPT,
        tools=tools
    )
    return cs_agent(query)


@tool
def language_assistant(query: str) -> str:
    """
    Handle translation and linguistic queries.
    
    Args:
        query (str): The language or translation question
        
    Returns:
        str: Translations, linguistic explanations, and language guidance
    """
    print("🌐 Routed to Language Assistant")
    
    lang_agent = Agent(
        system_prompt=LANGUAGE_ASSISTANT_PROMPT,
        tools=[http_request]  # Web access for translation APIs
    )
    return lang_agent(query)


@tool
def web_research_assistant(query: str) -> str:
    """
    Handle web research and information gathering queries.
    
    Args:
        query (str): The research question or information request
        
    Returns:
        str: Research findings with sources and analysis
    """
    print("🔍 Routed to Web Research Assistant")
    
    # Use available tools based on platform
    tools = [http_request]
    if UNIX_TOOLS_AVAILABLE:
        tools.append(python_repl)
    
    research_agent = Agent(
        system_prompt=WEB_RESEARCH_ASSISTANT_PROMPT,
        tools=tools
    )
    return research_agent(query)


@tool
def general_assistant(query: str) -> str:
    """
    Fallback assistant for general questions that don't fit other specialties.
    
    Args:
        query (str): The general question
        
    Returns:
        str: General knowledge response
    """
    print("📝 Routed to General Assistant")
    
    gen_agent = Agent(
        system_prompt=GENERAL_ASSISTANT_PROMPT,
        tools=[calculator]  # Basic tools only
    )
    return gen_agent(query)


@tool
def calendar_intent_agent(query: str) -> str:
    """
    Extracts calendar intent and event details from user input.
    Returns a JSON list of event objects.
    """
    agent = Agent(
        system_prompt=CALENDAR_SYSTEM_PROMPT,
        model=bedrock_model
    )
    return agent(query)


# List of all available specialist tools
SPECIALIST_TOOLS = [
    math_assistant,
    computer_science_assistant,
    language_assistant,
    web_research_assistant,
    general_assistant,
    calendar_intent_agent,
] 