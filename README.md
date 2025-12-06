# Founder Dataset Generation Pipeline

A Python pipeline that transforms Tinder dating app profiles into synthetic startup founder profiles using LLM enrichment and behavioral scoring.

## Project Structure

```
Project/
├── config.py                        # Constants and controlled vocabularies
├── prompts.py                       # LLM prompt builder
├── llm_client.py                    # LLM interface (configured for Google Gemini Flash)
├── parser.py                        # JSON parsing and validation
├── behavioral_scores.py             # Engagement metrics normalization
├── main.py                          # Pipeline orchestration
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Google Gemini API

The pipeline is pre-configured to use Google's `gemini-2.5-flash` model.

**Important:** The API key is currently hardcoded in `llm_client.py` for convenience. In a production environment, you should use environment variables:

1. Edit `llm_client.py`:
   ```python
   # Recommended approach
   import os
   API_KEY = os.environ.get("GOOGLE_API_KEY")
   ```
2. Set the variable in your shell:
   ```bash
   export GOOGLE_API_KEY="your-api-key"
   ```

### 3. Add Your Data

Place `Tinder_Data_v3_Clean_Edition.csv` in the project directory. The file should be semicolon-separated with columns including:
- `_id` (user ID)
- `bio`, `jobTitle`, `user_age`, `gender`
- `sum_app_opens`, `nrOfConversations`, `averageConversationLength`
- `averageConversationLengthInDays`, `longestConversationInDays`

## Usage

### Run Full Pipeline

```bash
python main.py
```

This will:
1. Load the Tinder CSV
2. Compute behavioral scores (collaboration openness, communication intensity, responsiveness)
3. Generate founder profiles for each user using Google Gemini Flash
4. Validate and fix all fields according to controlled vocabularies
5. Save results to `founders_dataset.csv`

### Load Existing Dataset

```python
from main import load_founders_dataset

founders_df = load_founders_dataset("founders_dataset.csv")
```

This automatically deserializes JSON list fields (roles, tech_stack, etc.).

## Output Schema

The generated `founders_dataset.csv` contains the following columns:

**Identity**
- `founder_id`: Unique ID from original Tinder data
- `age`: User age
- `gender`: User gender

**Roles & Industry**
- `roles`: JSON list of roles (subset of: CEO, CTO, CPO, COO)
- `preferred_role`: Primary role (must be in roles list)
- `industry`: Primary industry (controlled vocabulary of 13 options)
- `secondary_industries`: JSON list of 0-2 additional industries

**Experience & Background**
- `years_of_experience`: Years of professional experience
- `is_technical`: Boolean technical background flag
- `education_level`: Education level (e.g., "bachelor", "master", "phd")
- `tech_stack`: JSON list of technologies/tools

**Strengths & Weaknesses**
- `strengths`: JSON list of 3 strengths (from controlled vocab of 14)
- `weaknesses`: JSON list of 2 weaknesses (from controlled vocab of 14)

**Personality Traits** (integers 1-5)
- `risk_tolerance`
- `leadership`
- `autonomy`
- `vision`
- `communication`
- `execution_speed`

**Startup Idea**
- `idea_title`: Title of founder's startup idea
- `idea_description`: 3-6 sentence description
- `problem_space`: 1-2 sentence problem statement

**Behavioral Scores** (floats 0-1, derived from engagement metrics)
- `collaboration_openness_score`
- `communication_intensity_score`
- `responsiveness_score`

## How It Works

### 1. Behavioral Score Computation

Three scores are computed from Tinder engagement data using min-max normalization:

- **Collaboration Openness**: `0.5 * app_opens + 0.5 * conversations`
- **Communication Intensity**: `0.7 * conversations + 0.3 * avg_conv_length`
- **Responsiveness**: `1/(avg_days+1) + 0.5/(longest_days+1)` (inverse of time)

### 2. LLM Enrichment

For each profile, Google Gemini generates:
- Founder roles and preferences
- Industry and domain focus
- Experience and technical background
- Tech stack
- Personality traits
- Startup idea aligned with chosen industry

### 3. Validation & Fixing

The parser automatically:
- Filters values to controlled vocabularies
- Fixes mismatched roles/preferred_role
- Pads strengths/weaknesses if too few
- Clips personality traits to [1,5] range
- Sets defaults for missing fields

## Module Details

### `config.py`
Defines all controlled vocabularies and constants used throughout the pipeline.

### `prompts.py`
Contains `build_prompt()` which creates the LLM prompt from profile data, handling missing values gracefully.

### `llm_client.py`
Configured to use Google Gemini Flash (`gemini-2.5-flash`) for fast and efficient profile generation.

### `parser.py`
Parses LLM JSON responses, strips markdown fences, validates all fields against vocabularies, and applies fixes/defaults.

### `behavioral_scores.py`
Computes normalized behavioral scores from engagement metrics using min-max normalization.

### `main.py`
Orchestrates the full pipeline: loads data, computes scores, calls LLM for each row, validates, and saves output.

## Troubleshooting

**"RuntimeError: Gemini API call failed"**
→ Check your internet connection and API key validity.

**"File not found: Tinder_Data_v3_Clean_Edition.csv"**
→ Place the CSV file in the project directory.

**"ImportError: No module named 'google'"**
→ Run `pip install -r requirements.txt`.

## License

This is a student ML project for educational purposes.
