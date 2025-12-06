"""
Behavioral score computation module using min-max normalization
on Tinder engagement metrics.
"""

import pandas as pd
import numpy as np
from typing import Optional


def safe_min_max_normalize(series: pd.Series, epsilon: float = 1e-10) -> pd.Series:
    """
    Safely normalize a series to [0, 1] range using min-max normalization.
    
    Args:
        series: Pandas Series to normalize
        epsilon: Small value to avoid division by zero
    
    Returns:
        Normalized series in [0, 1] range
    """
    # Fill NaN with 0
    series = series.fillna(0)
    
    min_val = series.min()
    max_val = series.max()
    
    # Avoid division by zero
    if max_val - min_val < epsilon:
        # All values are the same, return 0.5 for all
        return pd.Series([0.5] * len(series), index=series.index)
    
    normalized = (series - min_val) / (max_val - min_val)
    
    # Clip to [0, 1] just in case
    return normalized.clip(0, 1)


def compute_collaboration_openness_score(df: pd.DataFrame) -> pd.Series:
    """
    Compute collaboration openness score from app usage and conversations.
    
    Formula: normalize(0.5 * sum_app_opens + 0.5 * nrOfConversations)
    
    Args:
        df: DataFrame with engagement metrics
    
    Returns:
        Series of collaboration openness scores [0, 1]
    """
    sum_app_opens = df['sum_app_opens'].fillna(0)
    nr_conversations = df['nrOfConversations'].fillna(0)
    
    # Combine metrics
    raw_score = 0.5 * sum_app_opens + 0.5 * nr_conversations
    
    # Normalize
    return safe_min_max_normalize(raw_score)


def compute_communication_intensity_score(df: pd.DataFrame) -> pd.Series:
    """
    Compute communication intensity score from conversation metrics.
    
    Formula: normalize(0.7 * nrOfConversations + 0.3 * averageConversationLength)
    
    Args:
        df: DataFrame with engagement metrics
    
    Returns:
        Series of communication intensity scores [0, 1]
    """
    nr_conversations = df['nrOfConversations'].fillna(0)
    avg_conv_length = df['averageConversationLength'].fillna(0)
    
    # Combine metrics
    raw_score = 0.7 * nr_conversations + 0.3 * avg_conv_length
    
    # Normalize
    return safe_min_max_normalize(raw_score)


def compute_responsiveness_score(df: pd.DataFrame, epsilon: float = 1.0) -> pd.Series:
    """
    Compute responsiveness score from conversation timing metrics.
    
    Formula: normalize(1/(avgConvLengthInDays + eps) + 0.5/(longestConvInDays + eps))
    
    Lower conversation length in days = more responsive = higher score
    
    Args:
        df: DataFrame with engagement metrics
        epsilon: Small value to avoid division by zero (default 1.0 day)
    
    Returns:
        Series of responsiveness scores [0, 1]
    """
    avg_conv_days = df['averageConversationLengthInDays'].fillna(0)
    longest_conv_days = df['longestConversationInDays'].fillna(0)
    
    # Inverse relationship: shorter time = more responsive
    raw_score = 1.0 / (avg_conv_days + epsilon) + 0.5 / (longest_conv_days + epsilon)
    
    # Normalize
    return safe_min_max_normalize(raw_score)


def compute_behavioral_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute all behavioral scores and add them to the DataFrame.
    
    This function adds three new columns:
    - collaboration_openness_score
    - communication_intensity_score
    - responsiveness_score
    
    Args:
        df: DataFrame with required engagement columns:
            - sum_app_opens
            - nrOfConversations
            - averageConversationLength
            - averageConversationLengthInDays
            - longestConversationInDays
    
    Returns:
        DataFrame with added behavioral score columns
    """
    # Make a copy to avoid modifying the original
    df = df.copy()
    
    # Compute each score
    df['collaboration_openness_score'] = compute_collaboration_openness_score(df)
    df['communication_intensity_score'] = compute_communication_intensity_score(df)
    df['responsiveness_score'] = compute_responsiveness_score(df)
    
    return df


def get_required_columns() -> list:
    """
    Get list of required columns for behavioral score computation.
    
    Returns:
        List of required column names
    """
    return [
        'sum_app_opens',
        'nrOfConversations',
        'averageConversationLength',
        'averageConversationLengthInDays',
        'longestConversationInDays'
    ]


def validate_required_columns(df: pd.DataFrame) -> bool:
    """
    Check if DataFrame has all required columns for behavioral score computation.
    
    Args:
        df: DataFrame to validate
    
    Returns:
        True if all required columns present, False otherwise
    """
    required = get_required_columns()
    missing = [col for col in required if col not in df.columns]
    
    if missing:
        print(f"Warning: Missing required columns: {missing}")
        return False
    
    return True

