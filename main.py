import streamlit as st
import pandas as pd
from pymongo import MongoClient
import time

# Set page configuration for a professional look
st.set_page_config(
    page_title="Part Number Search",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background-color: #f8fafc;
        padding: 20px;
        border-radius: 10px;
    }
    
    /* Title styling */
    .stTitle {
        color: #1e3a8a;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
    }
    
    /* Search bar styling */
    .stTextInput > div > div > input {
        border: 2px solid #3b82f6;
        border-radius: 8px;
        padding: 10px;
        font-size: 16px;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #3b82f6;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: 500;
        border: none;
        transition: background-color 0.3s;
    }
    .stButton > button:hover {
        background-color: #1e40af;
    }
    
    /* DataFrame styling */
    .stDataFrame {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        overflow: hidden;
    }
    .stDataFrame table {
        width: 100%;
        border-collapse: collapse;
    }
    .stDataFrame th {
        background-color: #1e3a8a;
        color: white;
        padding: 12px;
        font-weight: 600;
    }
    .stDataFrame td {
        padding: 12px;
        border-bottom: 1px solid #e2e8f0;
    }
    .stDataFrame tr:nth-child(even) {
        background-color: #f1f5f9;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1e3a8a;
        color: white;
    }
    .css-1d391kg .stSelectbox label {
        color: white;
        font-weight: 500;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        color: #64748b;
        font-size: 14px;
        margin-top: 20px;
        padding: 10px;
        border-top: 1px solid #e2e8f0;
    }
    </style>
""", unsafe_allow_html=True)

# Cache the database connection for performance
@st.cache_resource
def get_db():
    client = MongoClient("mongodb+srv://maheshkumar17032k3:hjtdIOubWFm6ckN0@materialsearch.fm0igam.mongodb.net/?retryWrites=true&w=majority&appName=materialsearch")
    return client["materialsearch"]

# Connect to the database
db = get_db()
collections = ["parts", "ground_floor_parts", "rack_and_imboj_parts"]

# Sidebar for filters and settings
with st.sidebar:
    st.header("🔧 Search Settings")
    st.markdown("Customize your search preferences.")
    
    # Collection filter
    selected_collections = st.multiselect(
        "Select Data Sources",
        options=collections,
        default=collections,
        format_func=lambda x: x.replace("_", " ").title()
    )
    
    # Case sensitivity toggle
    case_sensitive = st.checkbox("Case Sensitive Search", value=False)
    
    st.markdown("---")
    st.markdown("**About**")
    st.markdown("This app searches for part numbers across multiple inventory datasets. Contact support for assistance.")

# Main content
st.markdown('<div class="main">', unsafe_allow_html=True)

# Header with branding
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://via.placeholder.com/100", caption="Logo")  # Replace with actual logo URL if available
with col2:
    st.title("🔍 Part Number Search")
    st.markdown("Search for part numbers to find their locations and quantities across all inventory datasets.")

# Search input and button
with st.form(key="search_form"):
    search_term = st.text_input(
        "Enter Part Code",
        placeholder="e.g., s938c55903 or 5903",
        help="Enter full or partial part codes to search."
    )
    submit_button = st.form_submit_button("Search", type="primary")
    
# Perform search when the button is submitted
if submit_button and search_term:
    with st.spinner("🔄 Searching..."):
        results = []
        
        # Adjust regex query based on case sensitivity
        regex_options = "" if case_sensitive else "i"
        query = {"part_code": {"$regex": str(search_term), "$options": regex_options}}
        
        # Search in selected collections
        for collection_name in selected_collections:
            collection = db[collection_name]
            docs = collection.find(query)
            
            # Collect results
            for doc in docs:
                results.append({
                    "Source": collection_name.replace("_", " ").title(),
                    "Location": doc["location"],
                    "Part Code": doc["part_code"],
                    "Quantity": doc["quantity"]
                })
        
        # Display results
        if results:
            df_results = pd.DataFrame(results)
            st.markdown(f"**Found {len(results)} results**")
            # Fixed: Include use_container_width inside st.dataframe call
            st.dataframe(
                df_results[["Source", "Location", "Part Code", "Quantity"]],
                use_container_width=True
            )
        else:
            st.warning("No matching parts found for the given search term.")
else:
    if submit_button:
        st.error("Please enter a part code to search.")

# Footer
st.markdown('<div class="footer">Powered By Data Analytics Team | © 2025 | Version 1.0</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)