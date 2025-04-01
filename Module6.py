import io
import zipfile
import pandas as pd
import streamlit as st

# Function to create the in-memory Excel file for each state
def create_excel_for_state(state_key, states_df, lockouts_df, new_df, closed_df, ndd_df, sum_sheet):
    # Create an in-memory file to store the Excel content
    excel_file = io.BytesIO()
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # Write the filtered state DataFrame for this key to the "Data" sheet
        if sum_sheet is not None:
            sum_sheet[state_key].to_excel(writer, sheet_name='Summary', index = True)
        
        states_df[state_key].to_excel(writer, sheet_name='Data', index=False)
        
        # Write other DataFrames to separate sheets if they exist
        if lockouts_df is not None:
            lockouts_df.to_excel(writer, sheet_name='Lockouts', index=False)
        
        if new_df is not None:
            new_df.to_excel(writer, sheet_name='New', index=False)
        
        if closed_df is not None:
            closed_df.to_excel(writer, sheet_name='Closed', index=False)
        
        if ndd_df is not None:
            ndd_df.to_excel(writer, sheet_name='NDD', index=False)
    
    
    # Seek to the beginning of the in-memory file to read or save it
    excel_file.seek(0)
    
    return excel_file

# Create a ZIP file to contain all Excel reports
def create_zip_file(states_df, lockouts_df, new_df, closed_df, ndd_df, summary_sheet):
    # Create an in-memory bytes buffer for the ZIP file
    zip_buffer = io.BytesIO()
    
    # Create a ZipFile object to write to the buffer
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for key in states_df:
            # Generate an Excel file for the state
            excel_file = create_excel_for_state(key, states_df, lockouts_df, new_df, closed_df, ndd_df, summary_sheet)
            
            # Dynamically create the filename based on the state key (e.g., state abbreviation)
            filename = f"{key}_tar.xlsx"
            
            # Write the Excel file to the ZIP file
            zip_file.writestr(filename, excel_file.read())
    
    # Seek to the beginning of the ZIP buffer before returning
    zip_buffer.seek(0)
    
    return zip_buffer
