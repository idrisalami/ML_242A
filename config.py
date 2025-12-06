"""
Configuration file containing all controlled vocabularies and constants
for the founder dataset generation pipeline.
"""

# Allowed roles for founders
ALLOWED_ROLES = ["CEO", "CTO", "CPO", "COO"]

# Allowed industries (controlled vocabulary)
ALLOWED_INDUSTRIES = [
    "SaaS",
    "Fintech",
    "Healthtech",
    "Consumer / Social",
    "Marketplaces",
    "Climate / Greentech",
    "AI / Deeptech",
    "E-commerce",
    "Edtech",
    "Gaming / Entertainment",
    "Biotech",
    "Web3 / Crypto",
    "Other"
]

# Strengths vocabulary (14 items)
STRENGTHS_VOCAB = [
    "Strategic thinking",
    "High ownership",
    "Strong leadership",
    "Fast execution",
    "Technical depth",
    "Product intuition",
    "Analytical problem-solving",
    "Creativity and vision",
    "Resilience",
    "Communication skills",
    "Team-building",
    "User empathy",
    "Ability to learn quickly",
    "Scrappiness"
]

# Weaknesses vocabulary (14 items)
WEAKNESSES_VOCAB = [
    "Impatient with slow processes",
    "Overly perfectionist",
    "Difficulty delegating",
    "Limited business experience",
    "Limited technical experience",
    "Poor work-life balance",
    "Struggles with prioritization",
    "Risk-averse",
    "Overly optimistic",
    "Easily distracted by new ideas",
    "Weak in sales",
    "Weak in hiring",
    "Lack of focus",
    "Overly detail-oriented"
]

# Default fallbacks for validation failures
DEFAULT_ROLES = ["CEO"]
DEFAULT_INDUSTRY = "Other"
DEFAULT_STRENGTHS = ["Strategic thinking", "Fast execution", "Resilience"]
DEFAULT_WEAKNESSES = ["Struggles with prioritization", "Limited business experience"]

# Personality trait bounds
PERSONALITY_TRAIT_MIN = 1
PERSONALITY_TRAIT_MAX = 5

# Personality trait names
PERSONALITY_TRAITS = [
    "risk_tolerance",
    "leadership",
    "autonomy",
    "vision",
    "communication",
    "execution_speed"
]

