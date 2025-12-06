"""
Prompt building module for LLM-based founder profile generation.
"""

import random
from config import (
    ALLOWED_ROLES,
    ALLOWED_INDUSTRIES,
    STRENGTHS_VOCAB,
    WEAKNESSES_VOCAB,
    PERSONALITY_TRAITS
)

def build_prompt(bio: str, job_title: str, age: int, gender: str) -> str:
    """
    Build a prompt for the LLM to generate a founder profile from dating app data.
    
    Args:
        bio: User's bio text (can be empty/None)
        job_title: User's job title (can be "unknown" or None)
        age: User's age
        gender: User's gender
    
    Returns:
        Formatted prompt string for LLM
    """
    # Handle missing or null values
    bio = bio if bio and str(bio).strip() and str(bio).lower() != 'nan' else "No bio provided"
    job_title = job_title if job_title and str(job_title).strip() and str(job_title).lower() not in ['nan', 'unknown'] else "Not specified"
    age = age if age and str(age).lower() != 'nan' else "Unknown"
    gender = gender if gender and str(gender).strip() and str(gender).lower() != 'nan' else "Not specified"
    
    # --- Randomize example values to prevent overfitting ---
    
    # Role & Industry
    ex_role = random.choice(ALLOWED_ROLES)
    ex_industry = random.choice(ALLOWED_INDUSTRIES)
    # Ensure role list has the preferred role plus maybe another one
    ex_roles_list = list(set([ex_role, random.choice(ALLOWED_ROLES)]))
    
    # Experience & Technical
    ex_years = random.randint(2, 12)
    ex_is_technical = random.choice([True, False])
    
    # Education
    education_levels = ["bachelor", "master", "phd", "bootcamp", "self-taught"]
    ex_education = random.choice(education_levels)
    
    # Tech Stack (just a few random examples)
    tech_options = [
        "Python", "Django", "React", "Node.js", "AWS", "Firebase", 
        "Figma", "Notion", "Webflow", "Bubble", "Excel", "Tableau", 
        "PostgreSQL", "MongoDB", "Docker", "Kubernetes", "Swift"
    ]
    ex_tech_stack = random.sample(tech_options, k=random.randint(2, 4))
    
    # Strengths & Weaknesses
    ex_strengths = random.sample(STRENGTHS_VOCAB, k=3)
    ex_weaknesses = random.sample(WEAKNESSES_VOCAB, k=2)
    
    # Personality Traits
    ex_traits = {trait: random.randint(2, 5) for trait in PERSONALITY_TRAITS}
    
    # Example Idea (Generic placeholders based on industry to be safe)
    ex_idea_title = f"{ex_industry} Innovation Project"
    
    prompt = f"""You are transforming a dating app user profile into a tech startup founder profile.

INPUT PROFILE:
- Bio: {bio}
- Job title: {job_title}
- Age: {age}
- Gender: {gender}

TASK:
Generate a realistic structured JSON founder profile. 
CRITICAL: Do NOT copy the example values below. Infer unique values based on the specific Input Profile above.
If the input bio/job is generic, hallucinate a creative and plausible persona (e.g., a former lawyer building legal tech, a chef building food tech, etc.).

REQUIRED JSON STRUCTURE:

{{
  "roles": {str(ex_roles_list).replace("'", '"')},    // non-empty subset of: ["CEO","CTO","CPO","COO"]
  "preferred_role": "{ex_role}",       // exactly one of these roles. VARY THIS based on profile.

  "industry": "{ex_industry}",         // exactly one of allowed industries

  "secondary_industries": ["Fintech"], // optional, 0–2 values from allowed list

  "years_of_experience": {ex_years},
  "is_technical": {str(ex_is_technical).lower()},               // true or false based on bio/job
  "education_level": "{ex_education}",       // e.g. "bachelor", "master", "phd", "bootcamp", "self-taught"

  "tech_stack": {str(ex_tech_stack).replace("'", '"')},   // LIST of tools/languages relevant to their role/idea

  "strengths": {str(ex_strengths).replace("'", '"')},     // Select 3 relevant to the PERSONA
  "weaknesses": {str(ex_weaknesses).replace("'", '"')},   // Select 2 relevant to the PERSONA

  "personality_traits": {{
    "risk_tolerance": {ex_traits['risk_tolerance']},               // 1-5 integer
    "leadership": {ex_traits['leadership']},                   // 1-5 integer
    "autonomy": {ex_traits['autonomy']},                     // 1-5 integer
    "vision": {ex_traits['vision']},                       // 1-5 integer
    "communication": {ex_traits['communication']},                // 1-5 integer
    "execution_speed": {ex_traits['execution_speed']}               // 1-5 integer
  }},

  "idea_title": "{ex_idea_title}",
  "idea_description": "3 to 6 sentences describing a unique startup idea related to the chosen industry.",
  "problem_space": "One or two sentences summarizing the problem being solved."
}}

CRITICAL VOCABULARY RULES:

1. Strengths must be selected ONLY from this list:
   {str(STRENGTHS_VOCAB).replace("'", '"')}

2. Weaknesses must be selected ONLY from this list:
   {str(WEAKNESSES_VOCAB).replace("'", '"')}

3. The startup idea MUST be directly and logically linked to the selected "industry".
   - If industry = Fintech → idea must involve payments, credit, compliance, banking, etc.
   - If industry = Healthtech → idea must involve health, diagnostics, care delivery, etc.
   - If industry = AI / Deeptech → idea must involve ML, AI agents, infrastructure, etc.
   - If industry = Marketplaces → idea must involve a two-sided market.
   - NO cross-domain or unrelated ideas.

GENERAL RULES:
- Use ONLY the allowed values for roles and industry.
- Output VALID JSON only (no markdown, no explanation).
- Use the dating bio and job title to infer background and personality.
- DIVERSITY REQUIREMENT: Vary the industries, roles, and ideas. Do not default to AI/CTO unless the profile strongly suggests it.
"""
    
    return prompt
