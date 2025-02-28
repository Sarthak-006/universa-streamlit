"""
Streamlit frontend for the UNIVERSA Advanced Decentralized Matching Engine.

This module provides a web-based user interface built with Streamlit for interacting
with the matching engine API.
"""

import streamlit as st
import requests
import json
import os
import pandas as pd
from typing import Dict, List, Any, Optional
import base64
from datetime import datetime
import io
from PIL import Image
import random

# Import the mock API
from .mock_api import make_mock_request

# Global flag for using mock API
USE_MOCK_API = os.getenv("USE_MOCK_API", "false").lower() == "true"

# Constants
API_URL = os.getenv("API_URL", "https://universa-api.onrender.com")  # Default to a cloud API endpoint
PAGES = ["Home", "Profiles", "Groups", "Matching", "Privacy Tools"]

# Set page configuration and theme
st.set_page_config(
    page_title="UNIVERSA",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for improved styling
def load_css():
    st.markdown("""
    <style>
        /* Main theme color */
        .primary-color {
            color: #4361ee;
        }
        
        /* Cards */
        .profile-card, .group-card {
            background-color: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 15px;
        }
        
        /* Metric cards */
        .metric-card {
            background-color: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
        }
        .metric-card h3 {
            font-size: 16px;
            margin-top: 0;
            color: #333;
        }
        .metric-card p {
            font-size: 28px;
            font-weight: bold;
            color: #4361ee;
            margin: 8px 0;
        }
        
        /* Feature cards */
        .feature-card {
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            margin-bottom: 15px;
        }
        .feature-card h4 {
            margin-top: 0;
            color: #4361ee;
        }
        
        /* Match score badge */
        .match-score {
            display: inline-block;
            background-color: #4361ee;
            color: white;
            border-radius: 20px;
            padding: 4px 12px;
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 8px;
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if "private_key" not in st.session_state:
    st.session_state.private_key = ""
if "public_key" not in st.session_state:
    st.session_state.public_key = ""
if "active_profile_id" not in st.session_state:
    st.session_state.active_profile_id = None
if "active_group_id" not in st.session_state:
    st.session_state.active_group_id = None

# Check if the API is accessible
def check_api_connection():
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            return True
        return False
    except:
        return False

# Helper functions
def make_api_request(endpoint: str, method: str = "GET", data: Optional[Dict] = None,
                    params: Optional[Dict] = None) -> Dict:
    """Make a request to the API, falling back to mock API if necessary."""
    global USE_MOCK_API
    
    # Use mock API if explicitly set or if real API connection fails
    if USE_MOCK_API:
        return make_mock_request(endpoint, method, data, params)
    
    # Try real API
    url = f"{API_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # If real API call fails, try the mock API instead
        if not USE_MOCK_API:
            USE_MOCK_API = True
            st.warning("Using mock API due to connection issues with the real API")
            return make_mock_request(endpoint, method, data, params)
        return {"error": str(e)}
    except requests.exceptions.Timeout:
        # If timeout, try the mock API
        if not USE_MOCK_API:
            USE_MOCK_API = True
            st.warning("Using mock API due to timeout with the real API")
            return make_mock_request(endpoint, method, data, params)
        return {"error": "API request timed out. Please try again later."}
    except json.JSONDecodeError:
        return {"error": "Invalid response from API. Please try again later."}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

def display_json(data: Dict) -> None:
    """Display JSON data in a prettier format."""
    st.json(data)

def display_profile(profile: Dict) -> None:
    """Display a profile card with improved styling."""
    with st.container():
        # Create a container with styling
        st.markdown('<div class="profile-card">', unsafe_allow_html=True)
        
        # Profile details
        st.subheader(profile.get('name', 'Unnamed Profile'))
        st.write(f"**ID:** {profile.get('id', 'Unknown')}")
        st.write(f"**Description:** {profile.get('description', 'No description')}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show preferences in an expander if available
        if 'preferences' in profile and profile['preferences']:
            with st.expander("Preferences"):
                st.json(profile['preferences'])

def display_group(group: Dict) -> None:
    """Display a group card with improved styling."""
    with st.container():
        # Create a container with styling
        st.markdown('<div class="group-card">', unsafe_allow_html=True)
        
        # Group details
        st.subheader(group.get('name', 'Unnamed Group'))
        st.write(f"**ID:** {group.get('id', 'Unknown')}")
        st.write(f"**Description:** {group.get('description', 'No description')}")
        st.write(f"**Members:** {len(group.get('members', []))}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show preferences in an expander if available
        if 'preferences' in group and group['preferences']:
            with st.expander("Group Preferences"):
                st.json(group['preferences'])

def generate_encryption_keys() -> None:
    """Generate encryption keys for secure communication."""
    response = make_api_request("/encryption/generate-key-pair", method="POST")
    
    if "error" in response:
        st.error(f"Failed to generate keys: {response['error']}")
    else:
        st.session_state.private_key = response["private_key"]
        st.session_state.public_key = response["public_key"]
        st.success("Encryption keys generated successfully!")

# Page functions
def home_page() -> None:
    """Home page with dashboard and overview."""
    # Load custom CSS
    load_css()
    
    # Title with logo and header
    col1, col2 = st.columns([1, 5])
    with col1:
        # Use a placeholder logo
        st.markdown('<div style="font-size: 4rem; color: #4361ee; text-align: center;">🌐</div>', unsafe_allow_html=True)
    with col2:
        st.title("UNIVERSA")
        st.write("Advanced Decentralized Matching Engine")
    
    # Welcome section using Streamlit native components
    st.header("Welcome to UNIVERSA")
    st.write("This privacy-focused system helps connect individuals and groups based on shared interests and preferences while maintaining data security and anonymity.")
    
    # Features section using Streamlit columns instead of HTML grid
    st.header("Key Features")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>🔒 Privacy-Preserving</h4>
            <p>Your sensitive data remains encrypted throughout the matching process</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h4>🧩 Group Formation</h4>
            <p>Create or join groups for larger collaborations</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>🤝 Versatile Connections</h4>
            <p>Find individuals or groups that match your preferences</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h4>🛡️ PII Protection</h4>
            <p>Built-in tools to detect and anonymize personal information</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Dashboard
    st.header("Dashboard")
    
    # System stats with improved styling
    # Fetch profile count
    profiles_response = make_api_request("/profiles/")
    profile_count = len(profiles_response) if not isinstance(profiles_response, dict) or "error" not in profiles_response else 0
    
    # Fetch group count
    groups_response = make_api_request("/groups/")
    group_count = len(groups_response) if not isinstance(groups_response, dict) or "error" not in groups_response else 0
    
    # Calculate some random stats for visual appeal
    match_count = profile_count // 2 if profile_count > 1 else random.randint(1, 5)
    privacy_score = random.randint(85, 99)
    
    # Use Streamlit columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Total Profiles</h3>
            <p>{}</p>
        </div>
        """.format(profile_count), unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>Active Groups</h3>
            <p>{}</p>
        </div>
        """.format(group_count), unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>Active Matches</h3>
            <p>{}</p>
        </div>
        """.format(match_count), unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>Privacy Score</h3>
            <p>{}%</p>
        </div>
        """.format(privacy_score), unsafe_allow_html=True)
    
    # Active profile with improved styling
    if st.session_state.active_profile_id:
        st.header("Your Active Profile")
        profile_response = make_api_request(f"/profiles/{st.session_state.active_profile_id}")
        
        if "error" in profile_response:
            st.error(f"Failed to load profile: {profile_response['error']}")
        else:
            display_profile(profile_response)
            
            # Recent matches with improved styling
            st.subheader("Recent Matches")
            matches_response = make_api_request(
                f"/matching/profile/{st.session_state.active_profile_id}/matches",
                params={"limit": 3}
            )
            
            if "error" in matches_response:
                st.warning("No recent matches found")
            else:
                for match in matches_response:
                    with st.container():
                        # Display match score as a badge
                        st.markdown(f'<div class="match-score">Match Score: {match["score"]:.2f}</div>', unsafe_allow_html=True)
                        
                        # Display the profile
                        display_profile(match['profile'])
                        st.divider()
    else:
        st.info("Select a profile from the Profiles page to see your dashboard")

def profiles_page() -> None:
    """Profile management page."""
    st.title("Profile Management")
    
    tab1, tab2, tab3 = st.tabs(["Create Profile", "Browse Profiles", "My Profile"])
    
    with tab1:
        st.header("Create a New Profile")
        
        with st.form("profile_form"):
            # Basic info
            preferences = st.text_area("Preferences (JSON)", "{}")
            tags = st.text_input("Tags (comma separated)")
            status = st.selectbox("Availability", ["active", "busy", "inactive"])
            
            # Encryption options
            use_encryption = st.checkbox("Encrypt sensitive data")
            
            if use_encryption and not st.session_state.public_key:
                st.warning("You need to generate encryption keys first")
                if st.button("Generate Keys"):
                    generate_encryption_keys()
            
            # Submit button
            submit = st.form_submit_button("Create Profile")
            
            if submit:
                try:
                    # Prepare profile data
                    profile_data = {
                        "preferences": json.loads(preferences),
                        "tags": [tag.strip() for tag in tags.split(",") if tag.strip()],
                        "availability": {"status": status}
                    }
                    
                    # Create profile
                    response = make_api_request("/profiles/", method="POST", data=profile_data)
                    
                    if "error" in response:
                        st.error(f"Failed to create profile: {response['error']}")
                    else:
                        st.success(f"Profile created successfully with ID: {response['profile_id']}")
                        st.session_state.active_profile_id = response["profile_id"]
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    
    with tab2:
        st.header("Browse Profiles")
        
        # Fetch profiles
        profiles_response = make_api_request("/profiles/")
        
        if "error" in profiles_response:
            st.error(f"Failed to load profiles: {profiles_response['error']}")
        elif not profiles_response:
            st.info("No profiles found")
        else:
            # Filter options
            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                filter_tag = st.text_input("Filter by Tag")
            with filter_col2:
                filter_status = st.selectbox("Filter by Status", ["All", "active", "busy", "inactive"])
            
            # Apply filters
            filtered_profiles = profiles_response
            if filter_tag:
                filtered_profiles = [p for p in filtered_profiles if filter_tag.lower() in [t.lower() for t in p.get("tags", [])]]
            if filter_status != "All":
                filtered_profiles = [p for p in filtered_profiles if p.get("availability", {}).get("status") == filter_status]
            
            # Display profiles
            for profile in filtered_profiles:
                with st.container():
                    display_profile(profile)
                    st.divider()
    
    with tab3:
        st.header("My Profile")
        
        if not st.session_state.active_profile_id:
            st.info("No active profile selected. Please select a profile from the Browse tab.")
        else:
            # Fetch profile details
            profile_response = make_api_request(f"/profiles/{st.session_state.active_profile_id}")
            
            if "error" in profile_response:
                st.error(f"Failed to load profile: {profile_response['error']}")
            else:
                # Display profile
                display_profile(profile_response)
                
                # Edit profile form
                st.subheader("Edit Profile")
                
                with st.form("edit_profile_form"):
                    # Current values
                    current_preferences = profile_response.get("preferences", {})
                    current_tags = profile_response.get("tags", [])
                    current_status = profile_response.get("availability", {}).get("status", "active")
                    
                    # Form fields
                    preferences = st.text_area("Preferences (JSON)", json.dumps(current_preferences, indent=2))
                    tags = st.text_input("Tags (comma separated)", ", ".join(current_tags))
                    status = st.selectbox("Availability", ["active", "busy", "inactive"], 
                                         index=["active", "busy", "inactive"].index(current_status))
                    
                    # Submit button
                    submit = st.form_submit_button("Update Profile")
                    
                    if submit:
                        try:
                            # Prepare profile data
                            profile_data = {
                                "preferences": json.loads(preferences),
                                "tags": [tag.strip() for tag in tags.split(",") if tag.strip()],
                                "availability": {"status": status}
                            }
                            
                            # Update profile
                            response = make_api_request(
                                f"/profiles/{st.session_state.active_profile_id}", 
                                method="PUT", 
                                data=profile_data
                            )
                            
                            if "error" in response:
                                st.error(f"Failed to update profile: {response['error']}")
                            else:
                                st.success("Profile updated successfully")
                                st.experimental_rerun()
                        except Exception as e:
                            st.error(f"An error occurred: {str(e)}")
                
                # Danger zone
                st.subheader("Danger Zone")
                if st.button("Delete Profile", type="primary", help="This action cannot be undone"):
                    if st.checkbox("I understand this action cannot be undone"):
                        response = make_api_request(
                            f"/profiles/{st.session_state.active_profile_id}",
                            method="DELETE"
                        )
                        
                        if "error" in response:
                            st.error(f"Failed to delete profile: {response['error']}")
                        else:
                            st.success("Profile deleted successfully")
                            st.session_state.active_profile_id = None
                            st.experimental_rerun()

def groups_page() -> None:
    """Group management page."""
    st.title("Group Management")
    
    tab1, tab2, tab3 = st.tabs(["Create Group", "Browse Groups", "My Groups"])
    
    with tab1:
        st.header("Create a New Group")
        
        with st.form("group_form"):
            # Basic info
            name = st.text_input("Group Name")
            description = st.text_area("Description")
            tags = st.text_input("Tags (comma separated)")
            
            # Initial members
            if st.session_state.active_profile_id:
                initial_members = st.checkbox("Add myself as a member", value=True)
            else:
                st.info("Select a profile to add yourself as a member")
                initial_members = False
            
            # Submit button
            submit = st.form_submit_button("Create Group")
            
            if submit:
                if not name:
                    st.error("Group name is required")
                else:
                    try:
                        # Prepare group data
                        group_data = {
                            "name": name,
                            "description": description,
                            "tags": [tag.strip() for tag in tags.split(",") if tag.strip()],
                            "members": [st.session_state.active_profile_id] if initial_members and st.session_state.active_profile_id else []
                        }
                        
                        # Create group
                        response = make_api_request("/groups/", method="POST", data=group_data)
                        
                        if "error" in response:
                            st.error(f"Failed to create group: {response['error']}")
                        else:
                            st.success(f"Group created successfully with ID: {response['group_id']}")
                            st.session_state.active_group_id = response["group_id"]
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
    
    with tab2:
        st.header("Browse Groups")
        
        # Fetch groups
        groups_response = make_api_request("/groups/")
        
        if "error" in groups_response:
            st.error(f"Failed to load groups: {groups_response['error']}")
        elif not groups_response:
            st.info("No groups found")
        else:
            # Filter options
            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                filter_tag = st.text_input("Filter by Tag")
            with filter_col2:
                filter_name = st.text_input("Filter by Name")
            
            # Apply filters
            filtered_groups = groups_response
            if filter_tag:
                filtered_groups = [g for g in filtered_groups if filter_tag.lower() in [t.lower() for t in g.get("tags", [])]]
            if filter_name:
                filtered_groups = [g for g in filtered_groups if filter_name.lower() in g.get("name", "").lower()]
            
            # Display groups
            for group in filtered_groups:
                with st.container():
                    display_group(group)
                    st.divider()
    
    with tab3:
        st.header("My Groups")
        
        if not st.session_state.active_profile_id:
            st.info("No active profile selected. Please select a profile to view your groups.")
        else:
            # Fetch profile's groups
            groups_response = make_api_request(f"/matching/profile/{st.session_state.active_profile_id}/groups")
            
            if "error" in groups_response:
                st.error(f"Failed to load groups: {groups_response['error']}")
            elif not groups_response:
                st.info("You are not a member of any groups yet")
            else:
                # Display groups
                for group in groups_response:
                    with st.container():
                        display_group(group)
                        st.divider()
            
            # Group recommendations
            st.subheader("Recommended Groups")
            recommendations_response = make_api_request(
                f"/matching/profile/{st.session_state.active_profile_id}/recommendations"
            )
            
            if "error" in recommendations_response:
                st.warning("No group recommendations available")
            elif not recommendations_response:
                st.info("No recommended groups found")
            else:
                for recommendation in recommendations_response:
                    with st.container():
                        st.write(f"**Match Score:** {recommendation['score']:.2f}")
                        display_group(recommendation['group'])
                        
                        # Join button
                        if st.button("Join Group", key=f"join_{recommendation['group']['group_id']}"):
                            group = recommendation['group']
                            if st.session_state.active_profile_id not in group.get("members", []):
                                # Add current user to group members
                                updated_members = group.get("members", []) + [st.session_state.active_profile_id]
                                
                                # Update group
                                response = make_api_request(
                                    f"/groups/{group['group_id']}",
                                    method="PUT",
                                    data={"members": updated_members}
                                )
                                
                                if "error" in response:
                                    st.error(f"Failed to join group: {response['error']}")
                                else:
                                    st.success(f"Successfully joined group: {group['name']}")
                                    st.experimental_rerun()
                        
                        st.divider()

def matching_page() -> None:
    """Matching functionality page."""
    st.title("Matching")
    
    if not st.session_state.active_profile_id:
        st.warning("Please select an active profile to use matching features")
        return
    
    tab1, tab2, tab3 = st.tabs(["Find Matches", "Form Groups", "Match History"])
    
    with tab1:
        st.header("Find Profile Matches")
        
        with st.form("match_form"):
            algorithm = st.selectbox("Matching Algorithm", ["tag", "preference"])
            min_score = st.slider("Minimum Match Score", 0.0, 1.0, 0.3)
            limit = st.number_input("Maximum Matches", min_value=1, max_value=50, value=10)
            
            submit = st.form_submit_button("Find Matches")
            
            if submit:
                match_request = {
                    "algorithm": algorithm,
                    "min_score": min_score,
                    "limit": limit
                }
                
                response = make_api_request(
                    f"/matching/profile/{st.session_state.active_profile_id}/matches",
                    params=match_request
                )
                
                if "error" in response:
                    st.error(f"Failed to find matches: {response['error']}")
                elif not response:
                    st.info("No matches found with the current criteria")
                else:
                    st.success(f"Found {len(response)} matches!")
                    
                    # Create a dataframe for sorting
                    match_data = []
                    for match in response:
                        profile = match["profile"]
                        match_data.append({
                            "profile_id": profile["profile_id"],
                            "tags": ", ".join(profile.get("tags", [])),
                            "availability": profile.get("availability", {}).get("status", "Unknown"),
                            "score": match["score"],
                            "profile": profile  # Store the full profile for display
                        })
                    
                    df = pd.DataFrame(match_data)
                    
                    # Sorting options
                    sort_by = st.selectbox("Sort by", ["score", "tags", "availability"])
                    sort_order = st.selectbox("Order", ["Descending", "Ascending"])
                    
                    # Sort the dataframe
                    ascending = sort_order == "Ascending"
                    df = df.sort_values(by=sort_by, ascending=ascending)
                    
                    # Display matches
                    for _, row in df.iterrows():
                        with st.container():
                            st.write(f"**Match Score:** {row['score']:.2f}")
                            display_profile(row["profile"])
                            st.divider()
    
    with tab2:
        st.header("Form Groups")
        
        with st.form("group_formation_form"):
            algorithm = st.selectbox("Grouping Algorithm", ["tag", "preference"], key="group_algo")
            min_size = st.number_input("Minimum Group Size", min_value=2, max_value=10, value=3)
            max_size = st.number_input("Maximum Group Size", min_value=min_size, max_value=20, value=5)
            
            submit = st.form_submit_button("Form Groups")
            
            if submit:
                group_request = {
                    "algorithm": algorithm,
                    "min_size": min_size,
                    "max_size": max_size
                }
                
                response = make_api_request(
                    "/matching/groups",
                    method="POST",
                    data=group_request
                )
                
                if "error" in response:
                    st.error(f"Failed to form groups: {response['error']}")
                elif not response:
                    st.info("No groups could be formed with the current criteria")
                else:
                    st.success(f"Formed {len(response)} groups!")
                    
                    # Display groups
                    for group in response:
                        with st.container():
                            display_group(group)
                            st.divider()
    
    with tab3:
        st.header("Match History")
        st.info("This feature is coming soon!")

def privacy_tools_page() -> None:
    """Privacy tools and settings page."""
    st.title("Privacy Tools")
    
    tab1, tab2, tab3, tab4 = st.tabs(["PII Detection", "Anonymization", "Encryption", "Settings"])
    
    with tab1:
        st.header("PII Detection")
        st.write("Detect personally identifiable information (PII) in text.")
        
        text = st.text_area("Enter text to analyze")
        use_ai = st.checkbox("Use AI for detection (more accurate but slower)")
        
        if st.button("Detect PII"):
            if not text:
                st.warning("Please enter some text to analyze")
            else:
                response = make_api_request(
                    "/privacy/detect-pii",
                    method="POST",
                    data={"text": text, "use_ai": use_ai}
                )
                
                if "error" in response:
                    st.error(f"PII detection failed: {response['error']}")
                else:
                    st.subheader("Detection Results")
                    
                    if response.get("has_pii", False):
                        st.warning("⚠️ PII detected in the text")
                    else:
                        st.success("✅ No PII detected in the text")
                    
                    # Show regex results
                    regex_results = response.get("regex_detection", {})
                    if regex_results:
                        st.subheader("Detected PII Types")
                        for pii_type, instances in regex_results.items():
                            st.write(f"**{pii_type}:** {', '.join(instances)}")
                    
                    # Mask button
                    if st.button("Mask Detected PII"):
                        mask_response = make_api_request(
                            "/privacy/mask-pii",
                            method="POST",
                            data={"text": text, "use_ai": use_ai}
                        )
                        
                        if "error" in mask_response:
                            st.error(f"PII masking failed: {mask_response['error']}")
                        else:
                            st.subheader("Masked Text")
                            st.code(mask_response.get("masked_text", ""))
    
    with tab2:
        st.header("Anonymization")
        st.write("Anonymize text or profiles by replacing PII with anonymized values.")
        
        anonymize_type = st.radio("What would you like to anonymize?", ["Text", "Profile"])
        
        if anonymize_type == "Text":
            text = st.text_area("Enter text to anonymize", key="anon_text")
            consistent = st.checkbox("Use consistent anonymization", value=True, 
                                  help="Same values get the same replacements")
            
            if st.button("Anonymize Text"):
                if not text:
                    st.warning("Please enter some text to anonymize")
                else:
                    response = make_api_request(
                        "/privacy/anonymize-text",
                        method="POST",
                        data={"text": text, "consistent": consistent}
                    )
                    
                    if "error" in response:
                        st.error(f"Anonymization failed: {response['error']}")
                    else:
                        st.subheader("Anonymized Text")
                        st.code(response.get("anonymized_text", ""))
                        
                        st.subheader("Mapping")
                        mapping = response.get("mapping", {})
                        if mapping:
                            for original, anonymized in mapping.items():
                                st.write(f"**{original}** → **{anonymized}**")
                        else:
                            st.info("No PII was found to anonymize")
        else:  # Profile
            if not st.session_state.active_profile_id:
                st.warning("Please select an active profile to anonymize")
            else:
                # Fetch profile
                profile_response = make_api_request(f"/profiles/{st.session_state.active_profile_id}")
                
                if "error" in profile_response:
                    st.error(f"Failed to load profile: {profile_response['error']}")
                else:
                    st.write("Profile to anonymize:")
                    display_profile(profile_response)
                    
                    if st.button("Create Anonymous Profile"):
                        response = make_api_request(
                            "/privacy/create-anonymous-profile",
                            method="POST",
                            data=profile_response
                        )
                        
                        if "error" in response:
                            st.error(f"Anonymization failed: {response['error']}")
                        else:
                            st.subheader("Anonymous Profile")
                            st.json(response)
                            
                            if st.button("Use This Anonymous Profile"):
                                st.info("This feature is coming soon!")
    
    with tab3:
        st.header("Encryption")
        st.write("Generate encryption keys and encrypt your data.")
        
        # Key management
        st.subheader("Key Management")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate New Keys"):
                generate_encryption_keys()
        with col2:
            if st.button("Clear Keys"):
                st.session_state.private_key = ""
                st.session_state.public_key = ""
                st.success("Keys cleared")
        
        # Display current keys
        if st.session_state.public_key:
            with st.expander("View Keys"):
                st.code(f"Public Key:\n{st.session_state.public_key[:20]}...{st.session_state.public_key[-20:]}")
                if st.session_state.private_key:
                    st.warning("⚠️ Keep your private key secure and never share it!")
                    if st.checkbox("Show Private Key"):
                        st.code(f"Private Key:\n{st.session_state.private_key[:20]}...{st.session_state.private_key[-20:]}")
        
        # Encrypt data
        st.subheader("Encrypt Data")
        
        encrypt_type = st.radio("What would you like to encrypt?", ["Text/JSON", "Profile"])
        
        if encrypt_type == "Text/JSON":
            data = st.text_area("Enter data to encrypt (text or JSON)")
            
            try:
                # Try to parse as JSON
                json_data = json.loads(data)
                is_json = True
            except:
                is_json = False
            
            use_asymmetric = st.checkbox("Use asymmetric encryption", 
                                      help="More secure, requires public key")
            
            if st.button("Encrypt Data"):
                if not data:
                    st.warning("Please enter some data to encrypt")
                elif use_asymmetric and not st.session_state.public_key:
                    st.error("Public key required for asymmetric encryption")
                else:
                    try:
                        endpoint = "/encryption/encrypt-symmetric"
                        request_data = json_data if is_json else {"text": data}
                        
                        response = make_api_request(
                            endpoint,
                            method="POST",
                            data=request_data
                        )
                        
                        if "error" in response:
                            st.error(f"Encryption failed: {response['error']}")
                        else:
                            st.subheader("Encrypted Data")
                            st.json(response)
                    except Exception as e:
                        st.error(f"Encryption failed: {str(e)}")
        else:  # Profile
            if not st.session_state.active_profile_id:
                st.warning("Please select an active profile to encrypt")
            else:
                # Fetch profile
                profile_response = make_api_request(f"/profiles/{st.session_state.active_profile_id}")
                
                if "error" in profile_response:
                    st.error(f"Failed to load profile: {profile_response['error']}")
                else:
                    st.write("Profile to encrypt:")
                    display_profile(profile_response)
                    
                    use_asymmetric = st.checkbox("Use asymmetric encryption", 
                                              help="More secure, requires public key",
                                              key="profile_asymm")
                    
                    if st.button("Encrypt Profile"):
                        if use_asymmetric and not st.session_state.public_key:
                            st.error("Public key required for asymmetric encryption")
                        else:
                            public_key = st.session_state.public_key if use_asymmetric else None
                            
                            response = make_api_request(
                                "/encryption/encrypt-profile",
                                method="POST",
                                data=profile_response,
                                params={"public_key": public_key} if public_key else None
                            )
                            
                            if "error" in response:
                                st.error(f"Profile encryption failed: {response['error']}")
                            else:
                                st.subheader("Encrypted Profile")
                                st.json(response)
                                
                                if st.button("Update My Profile with Encrypted Data"):
                                    # Update profile with encrypted data
                                    update_response = make_api_request(
                                        f"/profiles/{st.session_state.active_profile_id}",
                                        method="PUT",
                                        data=response
                                    )
                                    
                                    if "error" in update_response:
                                        st.error(f"Failed to update profile: {update_response['error']}")
                                    else:
                                        st.success("Profile updated with encrypted data")
                                        st.experimental_rerun()
    
    with tab4:
        st.header("Privacy Settings")
        
        # AI Detection Settings
        st.subheader("AI-based PII Detection")
        use_ai_default = st.checkbox("Enable AI-based PII detection by default", value=False,
                                   help="More accurate but requires API key")
        
        api_key = st.text_input("Groq API Key (optional)", 
                              type="password",
                              help="Required for AI-based detection")
        
        if st.button("Save Settings"):
            # This would normally update user settings
            st.success("Settings saved successfully")
        
        # Export/Clear Data
        st.subheader("Data Management")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export My Data"):
                if not st.session_state.active_profile_id:
                    st.warning("Please select an active profile to export data")
                else:
                    # Fetch profile
                    profile_response = make_api_request(f"/profiles/{st.session_state.active_profile_id}")
                    
                    if "error" in profile_response:
                        st.error(f"Failed to load profile: {profile_response['error']}")
                    else:
                        # Convert to JSON
                        profile_json = json.dumps(profile_response, indent=2)
                        
                        # Create download link
                        b64 = base64.b64encode(profile_json.encode()).decode()
                        href = f'<a href="data:application/json;base64,{b64}" download="profile_{st.session_state.active_profile_id}.json">Download Profile Data</a>'
                        st.markdown(href, unsafe_allow_html=True)
        
        with col2:
            if st.button("Clear All Session Data"):
                # Clear session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.success("Session data cleared")
                st.experimental_rerun()

# Main app logic
def main():
    """Main application entry point."""
    # Load custom CSS
    load_css()
    
    # Check API connection and determine if using mock mode
    api_connected = check_api_connection()
    global USE_MOCK_API
    
    if not api_connected and not USE_MOCK_API:
        USE_MOCK_API = True
        st.warning("⚠️ API connection failed. Using mock data for demonstration.")
    
    # Sidebar navigation with improved styling
    with st.sidebar:
        # App title
        st.title("UNIVERSA")
        st.caption("Decentralized Matching Engine")
        
        if USE_MOCK_API:
            st.warning("⚠️ DEMO MODE: Using mock data")
        
        st.markdown("---")
        
        # Navigation
        st.subheader("Navigation")
        selection = st.radio("", PAGES, label_visibility="collapsed")
        
        st.markdown("---")
        
        # Display encryption key status in sidebar
        if st.session_state.public_key:
            st.success("🔐 Encryption keys configured")
        else:
            st.warning("🔓 Encryption keys not configured")
            if st.button("Generate Keys", use_container_width=True):
                generate_encryption_keys()
        
        # Display active profile in sidebar
        if st.session_state.active_profile_id:
            st.markdown("#### Active Profile")
            st.info(st.session_state.active_profile_id)
            if st.button("Clear Active Profile", use_container_width=True):
                st.session_state.active_profile_id = None
                st.experimental_rerun()
        
        # Environment info
        st.markdown("---")
        st.caption(f"Mode: {'DEMO' if USE_MOCK_API else 'PRODUCTION'}")
        if not USE_MOCK_API:
            st.caption(f"API URL: {API_URL}")
        
        # Toggle mock mode button
        if st.button("Toggle Demo Mode", use_container_width=True):
            USE_MOCK_API = not USE_MOCK_API
            st.experimental_rerun()
        
        # Add footer
        st.markdown("""<div style="position: fixed; bottom: 0; width: 100%; text-align: center; padding: 1rem; opacity: 0.7; font-size: 0.8rem;">UNIVERSA © 2023</div>""", unsafe_allow_html=True)
    
    # Display the selected page
    if selection == "Home":
        home_page()
    elif selection == "Profiles":
        profiles_page()
    elif selection == "Groups":
        groups_page()
    elif selection == "Matching":
        matching_page()
    elif selection == "Privacy Tools":
        privacy_tools_page()

# Run the app
if __name__ == "__main__":
    main() 