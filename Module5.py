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
        "06": "CT"   # Connecticut
    }
    
    # Get the unique state abbreviations from the "Agency" column
    states = df['Agency'].unique()
    
    # Loop through each state abbreviation
    for state in states:
        # Extract the first two characters to map to state codes
        state_num = state.split()[0][:2]
        
        # Check if the state_num exists in the state_codes dictionary
        if state_num in state_codes:
            # Filter the DataFrame for the current state
            state_df = df[df["Agency"] == state]
            
            # Store the filtered DataFrame in the dictionary with state abbreviation as the key
            filtered_state_dfs[state_codes[state_num]] = state_df
        else:
            # If the state_num is not found, print an error message
            st.write(f"Cannot identify state for code: {state_num}")
    
    # Return the dictionary of filtered DataFrames
    return filtered_state_dfs


