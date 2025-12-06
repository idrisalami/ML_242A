"""
Main pipeline orchestration for founder dataset generation.

This module loads Tinder data, enriches it with LLM-generated founder profiles,
computes behavioral scores, and outputs a structured founders dataset.
"""

import pandas as pd
import json
from typing import Optional, Dict, Any
from tqdm import tqdm
import concurrent.futures
import random

from prompts import build_prompt
from llm_client import call_llm
from parser import parse_founder_json
from behavioral_scores import compute_behavioral_scores, validate_required_columns
from config import PERSONALITY_TRAITS, ALLOWED_ROLES, ALLOWED_INDUSTRIES


def process_single_founder(
    row: pd.Series, 
    suggested_role: Optional[str] = None, 
    suggested_industry: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Process a single Tinder profile row into a founder profile.
    
    Args:
        row: Pandas Series with Tinder profile data
        suggested_role: Optional suggested role (soft hint for distribution)
        suggested_industry: Optional suggested industry (soft hint for distribution)
    
    Returns:
        Founder profile dictionary or None if processing fails
    """
    try:
        # Extract input fields
        bio = row.get('bio', '')
        job_title = row.get('jobTitle', '')
        age = row.get('user_age', 0)
        gender = row.get('gender', '')
        
        # Build prompt with suggested soft hints
        prompt = build_prompt(
            bio, 
            job_title, 
            age, 
            gender, 
            suggested_role=suggested_role, 
            suggested_industry=suggested_industry
        )
        
        # Call LLM - Now mandatory
        try:
            response = call_llm(prompt)
        except Exception as e:
            print(f"LLM Call Failed for user {row.get('_id', 'unknown')}: {e}")
            return None
        
        # Parse and validate JSON
        founder_data = parse_founder_json(response)
        
        if founder_data is None:
            print(f"Failed to parse founder data for user {row.get('_id', 'unknown')}")
            return None
        
        # Add identity fields
        founder_data['founder_id'] = row.get('_id', '')
        founder_data['age'] = row.get('user_age', 0)
        founder_data['gender'] = row.get('gender', '')
        
        # Add behavioral scores
        founder_data['collaboration_openness_score'] = row.get('collaboration_openness_score', 0.5)
        founder_data['communication_intensity_score'] = row.get('communication_intensity_score', 0.5)
        founder_data['responsiveness_score'] = row.get('responsiveness_score', 0.5)
        
        return founder_data
        
    except Exception as e:
        print(f"Error processing row {row.get('_id', 'unknown')}: {e}")
        return None


def flatten_founder_profile(founder_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flatten nested structures in founder profile for DataFrame conversion.
    
    Args:
        founder_data: Founder profile dictionary
    
    Returns:
        Flattened dictionary suitable for DataFrame row
    """
    flattened = founder_data.copy()
    
    # Flatten personality traits from nested dict to top-level columns
    if 'personality_traits' in flattened:
        traits = flattened.pop('personality_traits')
        for trait_name in PERSONALITY_TRAITS:
            flattened[trait_name] = traits.get(trait_name, 3)
    
    # Convert lists to JSON strings for CSV storage
    list_fields = ['roles', 'secondary_industries', 'tech_stack', 'strengths', 'weaknesses']
    for field in list_fields:
        if field in flattened and isinstance(flattened[field], list):
            flattened[field] = json.dumps(flattened[field])
    
    return flattened


def build_founders_dataset(
    csv_path: str = "Tinder_Data_v3_Clean_Edition.csv",
    output_path: str = "founders_dataset.csv",
    max_rows: Optional[int] = None,
    max_workers: int = 10
) -> pd.DataFrame:
    """
    Build the complete founders dataset from Tinder data.
    
    Args:
        csv_path: Path to input Tinder CSV file
        output_path: Path for output founders CSV file
        max_rows: Maximum number of rows to process (None for all)
        max_workers: Number of parallel threads for LLM calls
    
    Returns:
        DataFrame with founder profiles
    """
    print(f"Loading Tinder data from {csv_path}...")
    
    # Load CSV with semicolon separator
    try:
        df = pd.read_csv(csv_path, sep=";")
        print(f"Loaded {len(df)} rows")
    except FileNotFoundError:
        print(f"Error: File not found at {csv_path}")
        print("Please ensure Tinder_Data_v3_Clean_Edition.csv is in the project directory.")
        raise
    
    # Validate required columns for behavioral scores
    if not validate_required_columns(df):
        print("Warning: Some required columns missing, behavioral scores may be inaccurate")
    
    # Compute behavioral scores
    print("Computing behavioral scores...")
    df = compute_behavioral_scores(df)
    print("Behavioral scores computed successfully")
    
    # Limit rows if specified (useful for testing)
    if max_rows is not None:
        df = df.head(max_rows)
        print(f"Processing first {max_rows} rows only")
    
    # Define weights for roles: Higher for CEO/CTO
    role_options = ["CEO", "CTO", "CPO", "COO"]
    role_weights = [0.35, 0.35, 0.15, 0.15]  # 70% CEO/CTO, 30% others
    
    # Process each row in parallel
    print(f"Processing {len(df)} profiles with LLM using {max_workers} threads...")
    founder_profiles = []
    failed_rows = 0
    
    rows_to_process = [row for _, row in df.iterrows()]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks with weighted random SUGGESTIONS
        future_to_row = {}
        for row in rows_to_process:
            # Weighted random choice for suggested role
            suggested_role = random.choices(role_options, weights=role_weights, k=1)[0]
            
            # Simple random choice for suggested industry
            suggested_industry = random.choice(ALLOWED_INDUSTRIES)
            
            future = executor.submit(process_single_founder, row, suggested_role, suggested_industry)
            future_to_row[future] = row
        
        # Process results as they complete
        for future in tqdm(concurrent.futures.as_completed(future_to_row), total=len(rows_to_process), desc="Generating founder profiles"):
            try:
                founder_data = future.result()
                if founder_data is not None:
                    # Flatten nested structures
                    flattened = flatten_founder_profile(founder_data)
                    founder_profiles.append(flattened)
                else:
                    failed_rows += 1
            except Exception as e:
                print(f"Task generated an exception: {e}")
                failed_rows += 1
    
    # Create founders DataFrame
    print(f"Successfully processed {len(founder_profiles)} founder profiles")
    print(f"Failed rows: {failed_rows}")
    
    if not founder_profiles:
        print("Warning: No founder profiles were successfully generated")
        return pd.DataFrame()
    
    founders_df = pd.DataFrame(founder_profiles)
    
    # Save to CSV
    print(f"Saving founders dataset to {output_path}...")
    founders_df.to_csv(output_path, index=False)
    print(f"Dataset saved successfully with {len(founders_df)} rows")
    
    return founders_df


def load_founders_dataset(csv_path: str = "founders_dataset.csv") -> pd.DataFrame:
    """
    Load a previously generated founders dataset.
    
    This helper function deserializes list fields that were stored as JSON strings.
    
    Args:
        csv_path: Path to founders CSV file
    
    Returns:
        DataFrame with deserialized list fields
    """
    df = pd.read_csv(csv_path)
    
    # Deserialize list fields
    list_fields = ['roles', 'secondary_industries', 'tech_stack', 'strengths', 'weaknesses']
    
    for field in list_fields:
        if field in df.columns:
            df[field] = df[field].apply(lambda x: json.loads(x) if pd.notna(x) else [])
    
    return df


if __name__ == "__main__":
    """
    Main entry point for the pipeline.
    """
    
    try:
        # Check if API is configured (basic check by trying import)
        import openai
        
        founders_df = build_founders_dataset(
            csv_path="Tinder_Data_v3_Clean_Edition.csv",
            output_path="founders_dataset.csv",
            max_rows=None,  # Process all rows
            max_workers=10  # Parallel threads
        )
        
        print("\n" + "="*60)
        print("PIPELINE COMPLETE!")
        print("="*60)
        print(f"Total founders: {len(founders_df)}")
        if not founders_df.empty:
            print(f"\nDataset columns ({len(founders_df.columns)}):")
            for col in sorted(founders_df.columns):
                print(f"  - {col}")
            print("\nFirst few rows:")
            print(founders_df.head())
        
    except ImportError:
        print("\nError: openai package not found.")
        print("Please run: pip install -r requirements.txt")
    except FileNotFoundError:
        print("\n" + "="*60)
        print("FILE NOT FOUND")
        print("="*60)
        print("Please add Tinder_Data_v3_Clean_Edition.csv to the project directory.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        raise
