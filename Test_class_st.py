import streamlit as st
import seaborn as sns
import pandas as pd
import pyodbc

# Header section
st.header("Class")
st.text("Test context")

server = '172.28.8.127'
database = 'TEMP_SAP_DAILY'
username = 'oe_user'
password = 'OE@93979'

connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
connection = pyodbc.connect(connection_string)
cursor = connection.cursor()

# make containers
dataset = st.container()

# Create a container for the dataset
with dataset:
    # Cache the SQL query result for 10 minutes (ttl=600)
    @st.cache_data(ttl=600)
    def load_data():
        df_class = pd.read_sql('SELECT * FROM [Master_OE].[dbo].[CLASS]', connection)
        df_class.columns = df_class.columns.str.strip()  # Remove trailing spaces from columns
        return df_class

    # Load the data
    df_class = load_data()

    df_class['Material'] = df_class['Material'].astype('str')

    # Sort the unique values in ascending order for the selectbox
    sorted_class_options = sorted(df_class['classQty'].unique())

    # Use session state to manage the selected class and search query
    if 'selected_class' not in st.session_state:
        st.session_state.selected_class = 'All'
    
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""

    # Create a combined list of options with "All" at the beginning
    options = ["All"] + sorted_class_options

    # Selectbox to filter class types, now including "All"
    st.session_state.selected_class = st.selectbox(
        "Select a class type to filter",
        options=options,
        index=options.index(st.session_state.selected_class)  # Get the index of the current selection
    )

    # Add a text input for the search box to filter data based on all columns
    st.session_state.search_query = st.text_input("Search data across all columns", value=st.session_state.search_query)

    # Add a "Clear Filter" button
    clear_filter = st.button("Clear Filter")

    if clear_filter:
        # Reset the session state variables to clear filters
        st.session_state.selected_class = 'All'
        st.session_state.search_query = ""

    # Filter the dataframe based on selectbox or search input
    filtered_data = df_class

    if st.session_state.selected_class != "All":
        # Apply class filter from the selectbox
        filtered_data = df_class[df_class['classQty'] == st.session_state.selected_class]

    if st.session_state.search_query:
        # Apply the search query across all columns
        filtered_data = filtered_data[
            filtered_data.apply(lambda row: row.astype(str).str.contains(st.session_state.search_query, case=False).any(), axis=1)
        ]

    # Show filtered data
    st.write(f"Data filtered for class type: {st.session_state.selected_class} and search query: {st.session_state.search_query}")
    st.write(filtered_data)

    # Count occurrences of each unique value in 'classQty'
    df_class_counts = filtered_data['classQty'].value_counts().reset_index()
    df_class_counts.columns = ['classQty', 'Count']

    # Create the bar chart dynamically
    st.bar_chart(df_class_counts.set_index('classQty')['Count'])