import pandas as pd
import re

def clean_and_process_data(new_df, ndd_df, data_df):
    
    # Conversions dictionary
    conversions = {
        'new_df' : {'Balance' : float},
        'ndd_df' : {'Next Pymt Amt' : float, 'Escrow Balance' : float},
        'data_df' : {'Loan id' : int, 'Tax Due' : float, 'Total Tax' : float, 'Net Tax' : float}
    }

    # Iterate over the DataFrames and their respective columns in the conversions dictionary
    for df, cols in zip([new_df, ndd_df, data_df], [conversions['new_df'], conversions['ndd_df'], conversions['data_df']]):
        for col, dtype in cols.items():
            # Check if the column contains commas or quotes and clean up
            if df[col].dtype == object:  # Only apply if the column is of type 'object' (string)
                # Remove commas, quotes, or any other non-numeric symbols
                df[col] = df[col].replace({',': '', '"': ''}, regex=True)
                
            # Convert the column to the appropriate data type
            df[col] = pd.to_numeric(df[col], errors='coerce').astype(dtype)
    
    #Display the largest date
    latest_date = data_df["Due Date"].max()

    # Columns to drop from 'ndd_df'
    cols_to_drop = [
        'Last Pymt Amt',        
        'Last Pymt Disb Dt',    
        'Payee ID',             
        'Insurance Type Cd',    
        'Account Nbr.1',        
        'UF-LORI',                         
    ]

    # Drop the specified columns from 'ndd_df'
    ndd_df = ndd_df.drop(cols_to_drop, axis=1)  # axis=1 indicates column-wise operation

    # Drop rows where any value is missing (NaN) in the 'Next Sched Pymt Dt' or 'Tax Type Cd' columns
    ndd_df = ndd_df.dropna(subset=["Next Sched Pymt Dt", "Tax Type Cd"], how="any")

    # Remove rows where 'Tax Type Cd' is equal to 'WTSW'
    ndd_df = ndd_df[ndd_df['Tax Type Cd'] != 'WTSW']

    # Convert the 'Next Sched Pymt Dt' column to datetime format using a specific date format
    ndd_df['Next Sched Pymt Dt'] = pd.to_datetime(ndd_df['Next Sched Pymt Dt'], format='%d-%b-%Y').dt.date

    ndd_df = ndd_df[ndd_df["Next Sched Pymt Dt"] <= latest_date]

    # Return the cleaned dataframes
    return new_df, ndd_df, data_df

