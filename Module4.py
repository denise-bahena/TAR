import pandas as pd

def summary_sheet(df):
    # Ensure there are no trailing spaces in column names
    df.columns = df.columns.str.strip()

    # Create a pivot table
    pivot_table = df.pivot_table(
        values=["Tax Due", "Exclude", "Net Tax"],
        index="Agency",  # Remove any extra space from column name "Agency"
        aggfunc="sum",  # Sum the values
        fill_value=0,  # Fill missing values with 0 for numerical calculations
        margins=True,  # Add a summary row (grand total)
        margins_name="Grand Total"  # Name for the summary row
    )

    return pivot_table
