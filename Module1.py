import re
import pandas as pd
from datetime import datetime


def clean_data(file_content, year):
    processed_data = []

    # Use splitlines() to split the string into lines
    lines = file_content.splitlines()

    for i, line in enumerate(lines):
        # Skip the first three lines
        if i < 3:
            continue
        
        # Process the line (strip whitespace and split by commas)
        data = re.split(r',\s*(?=(?:(?:[^"]*"){2})*[^"]*$)', line)

        data = [item.replace('=', '').strip().strip('"') for item in data]
        
        # Append the processed data to the list
        processed_data.append(data)

    for i in range(len(processed_data)):
        line = processed_data[i]

        # Loop over the line
        for j in range(len(line)):
            if j == 0:
                del line[0]  # Delete the first element
        # After the inner loop, update the processed_data with the modified line
        processed_data[i] = line

    # Convert processed data into a DataFrame
    data_df = pd.DataFrame(processed_data[1:], columns=processed_data[0])
    data_df.columns = data_df.columns.str.strip()

    # Drop unnecessary columns
    data_df = data_df.drop(["Run Date", "Job No", "Dup Bill Fee", "DQ"], axis=1)
    # Add 'Exclude' and 'Borrower Name' columns with appropriate replacements
    data_df["Exclude"] = ""

    # Initialize 'Net Tax' column
    data_df['Net Tax'] = ''
    
    # Fill 'Net Tax' column with 'Total Tax' values where 'Exclude' is empty
    for i in range(len(data_df['Exclude'])):
        if data_df['Exclude'][i] == '':
            data_df.loc[i, 'Net Tax'] = data_df.loc[i, 'Total Tax']

    # Remove any remaining quotation marks in the 'Borrower Name' column
    data_df["Borrower Name"] = data_df["Borrower Name"].replace('"', '', regex=True)

    data_df['Due Date'] = data_df['Due Date'].apply(lambda x: datetime.strptime(f"{year}-{x}", "%Y-%m/%d").date())

    # Ensure the 'Full Due Date' is in the MM/DD/YYYY format
    data_df['Due Date'] = pd.to_datetime(data_df['Due Date'], format='%m/%d/%Y').dt.date


    return data_df