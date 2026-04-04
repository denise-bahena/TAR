import streamlit as st
import pandas as pd
import datetime
import re
from abemodule import clean_corelogic_df
from Module2 import clean_and_process_data
from Module3 import merge_and_clean_data
from Module4 import summary_sheet, generate_summary_sheet
from Module5 import filter_state_dfs
from Module6 import create_excel_for_state, create_zip_file

# -------------------------------
# User input: report year
# -------------------------------
due_year = st.number_input(
    "Enter the year your report is due:",
    min_value=datetime.datetime.now().year,
    max_value=2100,
    step=1
)

# -------------------------------
# Upload multiple files
# -------------------------------
uploaded_files = st.file_uploader(
    "Please upload all files pertinent to the report",
    accept_multiple_files=True
)

# -------------------------------
# Mapping: filename keyword → internal variable name
# -------------------------------
filename_to_var = {
    'new_loans': 'new_loans_df',
    'escrow_next_disbursement': 'ndd_df',
    'escrow_restricted_lockouts': 'lockouts_df',
    'closed_loans': 'closed_loans_df',
    'corelogic': 'corelogic_df'
}

# -------------------------------
# Helper: normalize filenames
# -------------------------------
def normalize_name(name):
    """
    Lowercase, replace spaces/hyphens with underscores,
    remove (number) suffixes and [DMND] brackets, strip whitespace
    """
    name = name.lower()
    name = re.sub(r"\s*\(\d+\)", "", name)   # remove (1), (24), etc.
    name = re.sub(r"\[.*?\]", "", name)      # remove [DMND] or other brackets
    name = name.replace(" ", "_").replace("-", "_")
    return name.strip()

# -------------------------------
# Initialize storage
# -------------------------------
df_dict = {}
abemodule_data = None

# -------------------------------
# Process uploaded files
# -------------------------------
if uploaded_files:
    for file in uploaded_files:
        normalized_file_name = normalize_name(file.name)
        matched = False

        for keyword, var_name in filename_to_var.items():
            if keyword in normalized_file_name:
                try:
                    if keyword == 'corelogic':
                        try:
                            cl_df = pd.read_csv(file, skiprows=3)
                        except:
                            cl_df = pd.read_csv(file, skiprows=3, engine='python')
                        abemodule_data = clean_corelogic_df(cl_df, due_year)
                    else:
                        df_dict[var_name] = pd.read_csv(file)
                    matched = True
                    break
                except Exception as e:
                    st.error(f"Failed to read file {file.name}: {e}")
                    matched = True
                    break

        if not matched:
            st.warning(f"Unrecognized file uploaded: {file.name}")

    # -------------------------------
    # Check for missing required files
    # -------------------------------
    required_vars = [v for k, v in filename_to_var.items() if k != 'corelogic']
    missing_files = [v for v in required_vars if v not in df_dict]
    if abemodule_data is None:
        missing_files.append('corelogic_df')

    if missing_files:
        st.error(f"Missing required files: {missing_files}")
    else:
        st.success("All required files uploaded successfully!")

        # -------------------------------
        # Downstream processing
        # -------------------------------
        try:
            # Clean and process
            new_df, ndd_df, data_df = clean_and_process_data(
                df_dict['new_loans_df'],
                df_dict['ndd_df'],
                abemodule_data
            )

            # Merge & clean
            data_df, lockouts_df, new_df, closed_df, ndd_df = merge_and_clean_data(
                data_df, df_dict['lockouts_df'], 
                new_df, df_dict['closed_loans_df'], 
                ndd_df
            )

            # Filter by state and generate summary
            states_df = filter_state_dfs(data_df)
            sum_sheets = generate_summary_sheet(states_df)

            st.write("Excel file(s) generating...")

            st.download_button(
                label="Download Report(s)",
                data=create_zip_file(states_df, lockouts_df, new_df, closed_df, ndd_df, sum_sheets),
                file_name="TAR_reports.zip",
                mime="application/zip",
                key="download_all_reports"
            )

        except Exception as e:
            st.error(f"Error during processing: {e}")

else:
    st.info("Upload required files to start processing.")