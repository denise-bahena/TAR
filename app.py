import streamlit as st
import pandas as pd
import io
from Module1 import clean_data  # Ensure these modules exist and are in the correct path
from Module2 import clean_and_process_data
from Module3 import merge_and_clean_data
from Module4 import summary_sheet, generate_summary_sheet
from Module5 import filter_state_dfs
from Module6 import create_excel_for_state, create_zip_file

pages= {
    "Home Page" : "app.py",
    "Summary Sheet Generation Page" : "summary.py"
}

# Create a non-editable navigation options using radio buttons
page = st.sidebar.radio("Select a page", list(pages.keys()))

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

if page == "Home Page":
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

                states_df = filter_state_dfs(data_df)
                sum_sheets = generate_summary_sheet(states_df)
                
                # Debugging: Check if the file is generated properly
                st.write("Excel file(s) generating ...")

                # Create a download button for the user
                st.download_button(
                    label="Download Report(s)",  # Label for the button
                    data = create_zip_file(states_df, lockouts_df, new_df, closed_df, ndd_df, sum_sheets),         # The in-memory binary data
                    file_name = "TAR_reports.zip",  # Name of the file to be downloaded
                    mime="application/zip",
                    key = "download_all_reports"
                    )
            else:
                st.write("Required files are missing for merging and cleaning.")
        else:
            st.write("File content for 'analyze' not found.")
    else:
        # No files uploaded or "Process Data" button hasn't been clicked yet
        st.write("Upload your files and click the button to process them.")
elif page == "Summary Sheet Generation Page":
    # Code for the Summary Sheet Generation Page
    st.title("Summary Sheet Generation")
    uploaded_file = st.file_uploader("Please upload Data sheet", accept_multiple_files=False)
    # Variable to control when to display data
    show_results = st.button("Process Data")

    if uploaded_file and show_results:
        file_content = uploaded_file.read().decode("utf-8")
        
        # Use StringIO to convert the string into a file-like object
        data = io.StringIO(file_content)
        
        # Now, read the CSV from the StringIO object
        df = pd.read_csv(data)
        
        # Generate the summary sheet output
        output = summary_sheet(df)

        # Create an in-memory Excel file to save the summary sheet
        with io.BytesIO() as excel_file:
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                output.to_excel(writer, sheet_name='Summary', index=True)
            
            # Seek to the beginning of the in-memory file
            excel_file.seek(0)
            
            # Provide the user a download button
            st.download_button(
                label="Download Summary Sheet",  # Label for the button
                data=excel_file,  # The in-memory binary data
                file_name="Summary.xlsx",  # Name of the file to be downloaded
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"  # MIME type for Excel files
            )