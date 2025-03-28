import streamlit as st
import pandas as pd
import io
from Module1 import clean_data  # Ensure these modules exist and are in the correct path
from Module2 import clean_and_process_data
from Module3 import merge_and_clean_data
from Module4 import summary_sheet

# Inject custom CSS to style the buttons
st.markdown(
    """
    <style>
    .stButton>button {
        background-color: #D8AF65;  /* Set button color to #D8AF65 */
        color: white;  /* Set button text color to white */
        border-radius: 5px;  /* Optional: Rounded corners */
        padding: 10px 20px;  /* Optional: Adjusts the padding */
        font-size: 16px;  /* Optional: Adjusts the font size */
    }
    .stButton>button:hover {
        background-color: #C89A5A;  /* Optional: Set hover effect color */
    }
    </style>
    """, unsafe_allow_html=True
)

# Add a title to your app
st.title("TAR Generator")

uploaded_files = st.file_uploader("Please upload all files pertinent to the report", accept_multiple_files=True)

# Variable to control when to display data
show_results = st.button("Process Data")

# Dictionary to store DataFrames by their filenames (to avoid overwriting)
df_dict = {}

# Check if any files have been uploaded
if uploaded_files and show_results:
    
    for file in uploaded_files:
        # Get the file name from the UploadedFile object
        file_name = file.name.lower().split('.csv')[0].split(' ')[0]  # Get the file name
        
        # Handle CSV files
        if 'analyze' in file_name:  # Checking if 'analyze' is in the file name
            file_content = file.read().decode("utf-8")
        
        # Handle other files (e.g., .lis or CSV without 'analyze')
        else:
            df = pd.read_csv(file)  # Read CSV file into a DataFrame

            # Store the DataFrame in the dictionary with the filename as the key
            df_dict[file_name] = df

    # Check if 'file_content' exists before passing it to clean_data function
    if 'file_content' in locals():
        module1_data = clean_data(file_content)
    
    # Ensure 'new_loans_(escrow)_[dmnd]' is available in the uploaded files
    if 'new_loans_(escrow)_[dmnd]' in df_dict and 'escrow_next_disbursement_[dmnd]' in df_dict:
        new_df, ndd_df, data_df = clean_and_process_data(
            df_dict['new_loans_(escrow)_[dmnd]'], 
            df_dict['escrow_next_disbursement_[dmnd]'], 
            module1_data
        )

        # Ensure 'escrow_restricted_lockouts_[dmnd]' and other required files exist
        if 'escrow_restricted_lockouts_[dmnd]' in df_dict and 'closed_loans_[dmnd]' in df_dict:
            data_df, lockouts_df, new_df, closed_df, ndd_df = merge_and_clean_data(
                data_df, df_dict['escrow_restricted_lockouts_[dmnd]'], 
                new_df, df_dict['closed_loans_[dmnd]'], 
                ndd_df
            )
            st.write(data_df)

            # Generate Excel file with multiple sheets in memory
            tar_name = st.text_input("Enter the desired file name for the report", "TAR_report")  # Default is 'TAR_report'
            sum_sheet = summary_sheet(data_df)

            # Create the Excel file in memory
            with io.BytesIO() as excel_file:
                with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                    # Write multiple sheets to the Excel file
                    sum_sheet.to_excel(writer, sheet_name='Summary', index = True)
                    data_df.to_excel(writer, sheet_name='Data', index=False)
                    lockouts_df.to_excel(writer, sheet_name='Lockouts', index=False)
                    new_df.to_excel(writer, sheet_name='New', index=False)
                    closed_df.to_excel(writer, sheet_name='Closed', index=False)
                    ndd_df.to_excel(writer, sheet_name='NDD', index=False)

                # Seek to the beginning of the in-memory file
                excel_file.seek(0)

                # Debugging: Check if the file is generated properly
                st.write("Excel file has been generated.")

                # Create a download button for the user
                st.download_button(
                    label="Download Report",  # Label for the button
                    data=excel_file,         # The in-memory binary data
                    file_name=f"{tar_name}.xlsx",  # Name of the file to be downloaded
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"  # MIME type for Excel files
                )
        else:
            st.write("Required files are missing for merging and cleaning.")
    else:
        st.write("File content for 'analyze' not found.")
else:
    # No files uploaded or "Process Data" button hasn't been clicked yet
    st.write("Upload your files and click the button to process them.")
