import streamlit as st

def filter_state_dfs(df):
    # Create an empty dictionary to store DataFrames for each state
    filtered_state_dfs = {}
    
    # Define the state codes and their corresponding state abbreviations
    state_codes = {
        "18": "ME",  # Maine
        "20": "MA",  # Massachusetts
        "38": "RI",  # Rhode Island
        "28": "NH",  # New Hampshire
        "06": "CT",
        "09": "FL",
        "31": "NY",
        "32": "NC",
        "41": "TN"
    }
    
    # Group by the first two digits of the 'Agency' column
    grouped = df.groupby(df['Agency'].str[:2])

    # Create a dictionary to store each group
    filtered_state_dfs = {}

    # Save each group to the dictionary as a new DataFrame with state name as the key
    for name, group in grouped:
        state = state_codes.get(name)  # Default to 'Unknown' if no match
        filtered_state_dfs[state] = group
    
    # Return the dictionary of filtered DataFrames
    return filtered_state_dfs


