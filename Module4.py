import pandas as pd

def summary_sheet(df):
    # Convert the relevant columns to numeric (in case they are not already)
    df["Tax Due"] = pd.to_numeric(df["Tax Due"], errors='coerce')
    df["Net Tax"] = pd.to_numeric(df["Net Tax"], errors='coerce')
    df["Exclude"] = pd.to_numeric(df["Exclude"], errors='coerce')

    # Fill NaN values with 0 for aggregation
    df["Tax Due"] = df["Tax Due"].fillna(0)
    df["Net Tax"] = df["Net Tax"].fillna(0)
    df["Exclude"] = df["Exclude"].fillna(0)

    # Create a pivot table with proper aggregation
    pivot_table = df.pivot_table(
        values=["Tax Due", "Exclude", "Net Tax"],
        index=["Agency"], 
        aggfunc={
            "Tax Due": "sum",  # Sum the Tax Due column
            "Exclude": "sum",  # Sum the Exclude column
            "Net Tax": "sum"   # Sum the Net Tax column for Grand Total
        },
        fill_value=0,  # Fill missing values with 0 for numerical calculations
        margins=True,  # Add a summary row (grand total)
        margins_name="Grand Total"  # Name for the summary row
    )

    return pivot_table

def generate_summary_sheet(filtered_state_dfs):
    sum_sheet_df = {}
    
    # Check if there are multiple dataframes in the dictionary
    if len(filtered_state_dfs.keys()) > 1:
        for key in filtered_state_dfs.keys():
            df = filtered_state_dfs[key].copy()  # Make a copy of the dataframe
            sum_sheet_df[key] = summary_sheet(df)  # Add the summary sheet to the result
    else:
        # If there is only one dataframe, fetch it explicitly
        key = next(iter(filtered_state_dfs))  # Get the first (and only) key
        df = filtered_state_dfs[key].copy()  # Make a copy of the dataframe
        sum_sheet_df[key] = summary_sheet(df)  # Add the summary sheet to the result
    
    return sum_sheet_df
