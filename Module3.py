import pandas as pd

def merge_and_clean_data(data_df, lockouts_df, new_df, closed_df, ndd_df):
    dfs = [lockouts_df, new_df, closed_df, ndd_df]
    # Merge dictionary
    merge_dict = {
        "lockouts_df": ["Account Nbr", "Lockout Flag Cd"],
        "new_df": ["Account Nbr", "Origination Dt"],
        "closed_df": ["Account Nbr", "Closed Dt"],
        "ndd_df": ["Account Nbr", "Next Sched Pymt Dt"]
    }

    # Store DataFrames in a dictionary for easy access
    dfs_dict = {
        "lockouts_df": lockouts_df,
        "new_df": new_df,
        "closed_df": closed_df,
        "ndd_df": ndd_df
    }

    # Perform merges for each dataframe in merge_dict
    for df_name, cols in merge_dict.items():
        # Access the dataframe from the dictionary
        df = dfs_dict[df_name]
        
        # Merge data_df with the current dataframe based on the specified columns
        data_df = data_df.merge(df[cols], left_on="Loan id", right_on=cols[0], how="left")
        
        # Drop the first column from the merge (Account Nbr in this case)
        data_df = data_df.drop(columns=cols[0])

    # Column renaming dictionary
    col_rename = {
        "Lockout Flag Cd": "Restriction",
        "Origination Dt": "New_Dt",
        "Closed Dt": "Closed_Dt",
        "Next Sched Pymt Dt": "NDD"
    }
    
    # Rename columns as per the dictionary
    data_df.rename(columns=col_rename, inplace=True)
    
    # Drop duplicate rows
    data_df = data_df.drop_duplicates()

    # Replace all NaN values in ndd_df with an empty string (for missing values)
    data_df = data_df.fillna("")

    # Return the cleaned data_df and ndd_df
    return data_df, lockouts_df, new_df, closed_df, ndd_df

