"""
JSON parsing and validation module for founder profiles.
"""

import json
import re
from typing import Optional, Dict, Any, List

from config import (
    ALLOWED_ROLES,
    ALLOWED_INDUSTRIES,
    STRENGTHS_VOCAB,
    WEAKNESSES_VOCAB,
    DEFAULT_ROLES,
    DEFAULT_INDUSTRY,
    DEFAULT_STRENGTHS,
    DEFAULT_WEAKNESSES,
    PERSONALITY_TRAIT_MIN,
    PERSONALITY_TRAIT_MAX,
    PERSONALITY_TRAITS
)


def strip_markdown_fences(text: str) -> str:
    """
    Remove markdown code fences from the response text.
    
    Args:
        text: Raw LLM response text
    
    Returns:
        Cleaned text with fences removed
    """
    # Remove ```json ... ``` or ``` ... ```
    text = text.strip()
    
    # Pattern to match code fences
    patterns = [
        r'^```json\s*\n?(.*?)\n?```$',
        r'^```\s*\n?(.*?)\n?```$'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
    
    return text


def validate_and_fix_roles(data: Dict[str, Any]) -> None:
    """
    Validate and fix roles fields in-place.
    
    Args:
        data: Parsed JSON data
    """
    # Validate roles
    roles = data.get('roles', [])
    if not isinstance(roles, list):
        roles = [roles] if roles else []
    
    # Filter to allowed roles
    roles = [r for r in roles if r in ALLOWED_ROLES]
    
    # Default if empty
    if not roles:
        roles = DEFAULT_ROLES.copy()
    
    data['roles'] = roles
    
    # Validate preferred_role
    preferred_role = data.get('preferred_role', '')
    if preferred_role not in roles:
        # Fallback to first role
        preferred_role = roles[0]
    
    data['preferred_role'] = preferred_role


def validate_and_fix_industry(data: Dict[str, Any]) -> None:
    """
    Validate and fix industry fields in-place.
    
    Args:
        data: Parsed JSON data
    """
    # Validate primary industry
    industry = data.get('industry', '')
    if industry not in ALLOWED_INDUSTRIES:
        industry = DEFAULT_INDUSTRY
    
    data['industry'] = industry
    
    # Validate secondary industries
    secondary = data.get('secondary_industries', [])
    if not isinstance(secondary, list):
        secondary = [secondary] if secondary else []
    
    # Filter to allowed, limit to 2
    secondary = [s for s in secondary if s in ALLOWED_INDUSTRIES][:2]
    
    data['secondary_industries'] = secondary


def validate_and_fix_strengths_weaknesses(data: Dict[str, Any]) -> None:
    """
    Validate and fix strengths and weaknesses in-place.
    
    Args:
        data: Parsed JSON data
    """
    # Validate strengths
    strengths = data.get('strengths', [])
    if not isinstance(strengths, list):
        strengths = [strengths] if strengths else []
    
    # Filter to vocab
    strengths = [s for s in strengths if s in STRENGTHS_VOCAB]
    
    # Pad with defaults if needed
    while len(strengths) < 3:
        for default in DEFAULT_STRENGTHS:
            if default not in strengths:
                strengths.append(default)
                break
    
    # Limit to 3
    data['strengths'] = strengths[:3]
    
    # Validate weaknesses
    weaknesses = data.get('weaknesses', [])
    if not isinstance(weaknesses, list):
        weaknesses = [weaknesses] if weaknesses else []
    
    # Filter to vocab
    weaknesses = [w for w in weaknesses if w in WEAKNESSES_VOCAB]
    
    # Pad with defaults if needed
    while len(weaknesses) < 2:
        for default in DEFAULT_WEAKNESSES:
            if default not in weaknesses:
                weaknesses.append(default)
                break
    
    # Limit to 2
    data['weaknesses'] = weaknesses[:2]


def validate_and_fix_personality_traits(data: Dict[str, Any]) -> None:
    """
    Validate and fix personality traits in-place.
    
    Args:
        data: Parsed JSON data
    """
    traits = data.get('personality_traits', {})
    
    if not isinstance(traits, dict):
        traits = {}
    
    # Ensure all required traits exist and are in valid range
    for trait_name in PERSONALITY_TRAITS:
        value = traits.get(trait_name, 3)  # Default to middle value
        
        # Try to convert to int and clip
        try:
            value = int(value)
        except (ValueError, TypeError):
            value = 3
        
        value = max(PERSONALITY_TRAIT_MIN, min(PERSONALITY_TRAIT_MAX, value))
        traits[trait_name] = value
    
    data['personality_traits'] = traits


def validate_basic_fields(data: Dict[str, Any]) -> None:
    """
    Validate and set defaults for basic fields in-place.
    
    Args:
        data: Parsed JSON data
    """
    # Years of experience
    try:
        data['years_of_experience'] = int(data.get('years_of_experience', 0))
    except (ValueError, TypeError):
        data['years_of_experience'] = 0
    
    # Is technical
    data['is_technical'] = bool(data.get('is_technical', False))
    
    # Education level
    if 'education_level' not in data or not data['education_level']:
        data['education_level'] = 'bachelor'
    
    # Tech stack
    tech_stack = data.get('tech_stack', [])
    if not isinstance(tech_stack, list):
        tech_stack = [tech_stack] if tech_stack else []
    data['tech_stack'] = tech_stack
    
    # Idea fields
    data['idea_title'] = data.get('idea_title', 'Untitled Startup Idea')
    data['idea_description'] = data.get('idea_description', 'No description provided.')
    data['problem_space'] = data.get('problem_space', 'No problem space defined.')


def parse_founder_json(response_text: str) -> Optional[Dict[str, Any]]:
    """
    Parse and validate founder profile JSON from LLM response.
    
    Args:
        response_text: Raw text response from LLM
    
    Returns:
        Validated founder profile dictionary, or None if parsing fails
    """
    try:
        # Strip markdown fences
        cleaned_text = strip_markdown_fences(response_text)
        
        # Parse JSON
        data = json.loads(cleaned_text)
        
        # Validate and fix all fields
        validate_and_fix_roles(data)
        validate_and_fix_industry(data)
        validate_and_fix_strengths_weaknesses(data)
        validate_and_fix_personality_traits(data)
        validate_basic_fields(data)
        
        return data
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error parsing founder JSON: {e}")
        return None

