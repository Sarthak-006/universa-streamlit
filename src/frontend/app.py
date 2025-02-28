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
    page_title="Universa - UniPriv",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for improved styling
def load_css():
    st.markdown("""
    <style>
        /* Main theme colors */
        :root {
            --primary-color: #4361ee;
            --primary-light: #6c8cff;
            --primary-dark: #1939c6;
            --secondary-color: #3a0ca3;
            --accent-color: #f72585;
            --background-color: #f8f9fa;
            --card-bg: #ffffff;
            --text-color: #212529;
            --text-light: #6c757d;
            --success-color: #4cc9a0;
            --warning-color: #ffd166;
            --error-color: #ef476f;
        }
        
        /* Global styles */
        .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-weight: 600;
            letter-spacing: -0.02em;
        }
        
        /* Sidebar styling */
        .css-1d391kg, .css-12oz5g7 {
            background-color: #f2f6ff;
        }
        
        /* Cards */
        .profile-card, .group-card {
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            margin-bottom: 20px;
            border: 1px solid rgba(0,0,0,0.05);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .profile-card:hover, .group-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 25px rgba(0,0,0,0.08);
        }
        
        /* Metric cards */
        .metric-card {
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            text-align: center;
            border: 1px solid rgba(0,0,0,0.05);
            height: 100%;
        }
        
        .metric-card h3 {
            font-size: 16px;
            margin-top: 0;
            color: var(--text-light);
            font-weight: 500;
        }
        
        .metric-card p {
            font-size: 32px;
            font-weight: 700;
            color: var(--primary-color);
            margin: 10px 0;
        }
        
        /* Feature cards */
        .feature-card {
            background-color: var(--card-bg);
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            margin-bottom: 20px;
            border: 1px solid rgba(0,0,0,0.05);
            transition: transform 0.2s ease;
            height: 100%;
        }
        
        .feature-card:hover {
            transform: translateY(-3px);
        }
        
        .feature-card h4 {
            margin-top: 0;
            color: var(--primary-color);
            font-size: 18px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .feature-card p {
            color: var(--text-light);
            line-height: 1.6;
        }
        
        /* Match score badge */
        .match-score {
            display: inline-block;
            background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
            color: white;
            border-radius: 20px;
            padding: 6px 14px;
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 12px;
            box-shadow: 0 2px 10px rgba(67, 97, 238, 0.3);
        }
        
        /* Buttons */
        .stButton button {
            border-radius: 8px;
            font-weight: 500;
            box-shadow: 0 2px 5px rgba(0,0,0,0.08);
            transition: all 0.2s ease;
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        
        /* Primary button */
        .primary-button button {
            background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
            color: white;
            border: none;
        }
        
        /* Header styling */
        .app-header {
            display: flex;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid rgba(0,0,0,0.05);
        }
        
        .app-logo {
            font-size: 2.5rem;
            background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-right: 1rem;
        }
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 8px 16px;
            background-color: #f2f6ff;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: var(--primary-color) !important;
            color: white !important;
        }
        
        /* Data tables */
        .dataframe {
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid rgba(0,0,0,0.05);
        }
        
        .dataframe th {
            background-color: #f2f6ff;
            font-weight: 600;
            padding: 12px 16px !important;
        }
        
        .dataframe td {
            padding: 12px 16px !important;
        }
        
        /* Form inputs */
        .stTextInput input, .stTextArea textarea, .stSelectbox, .stMultiselect {
            border-radius: 8px;
            border: 1px solid rgba(0,0,0,0.1);
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            font-weight: 500;
            color: var(--primary-color);
            background-color: #f2f6ff;
            border-radius: 8px;
        }
        
        /* Progress bars */
        .stProgress > div > div {
            background-color: var(--primary-color);
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    if "private_key" not in st.session_state:
        st.session_state.private_key = ""
    if "public_key" not in st.session_state:
        st.session_state.public_key = ""
    if "active_profile_id" not in st.session_state:
        st.session_state.active_profile_id = None
    if "active_group_id" not in st.session_state:
        st.session_state.active_group_id = None
    # Add any other session state variables that need initialization

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
    st.markdown('<div class="app-header">', unsafe_allow_html=True)
    st.markdown('<span class="app-logo">🌐</span>', unsafe_allow_html=True)
    st.markdown('<div><h1 style="margin:0">Universa - UniPriv</h1><p style="margin:0;color:var(--text-light)">Advanced Decentralized Matching Engine</p></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Welcome section with a modern hero area
    st.markdown("""
    <div style="background:linear-gradient(135deg, #f2f6ff, #e6f0ff);border-radius:16px;padding:32px;margin-bottom:32px;border:1px solid rgba(67,97,238,0.1);">
        <h2 style="margin-top:0;margin-bottom:16px;color:var(--primary-dark);">Welcome to Universa - UniPriv</h2>
        <p style="font-size:18px;line-height:1.6;max-width:800px;margin-bottom:24px;">
            This privacy-focused system helps connect individuals and groups based on shared interests and preferences 
            while maintaining data security and anonymity.
        </p>
        <div style="display:inline-block;background:linear-gradient(135deg, var(--primary-color), var(--primary-dark));color:white;padding:10px 20px;border-radius:8px;font-weight:500;box-shadow:0 4px 12px rgba(67,97,238,0.2);">
            Get Started →
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics in a row
    st.subheader("System Overview")
    
    metrics_cols = st.columns(4)
    with metrics_cols[0]:
        st.markdown("""
        <div class="metric-card">
            <h3>Active Profiles</h3>
            <p>1,248</p>
        </div>
        """, unsafe_allow_html=True)
    
    with metrics_cols[1]:
        st.markdown("""
        <div class="metric-card">
            <h3>Active Groups</h3>
            <p>86</p>
        </div>
        """, unsafe_allow_html=True)
    
    with metrics_cols[2]:
        st.markdown("""
        <div class="metric-card">
            <h3>Matches Made</h3>
            <p>3,542</p>
        </div>
        """, unsafe_allow_html=True)
    
    with metrics_cols[3]:
        st.markdown("""
        <div class="metric-card">
            <h3>Privacy Score</h3>
            <p>98%</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Features section with improved cards
    st.markdown("<h2 style='margin-top:40px;margin-bottom:24px;'>Key Features</h2>", unsafe_allow_html=True)
    
    feature_cols = st.columns(3)
    
    with feature_cols[0]:
        st.markdown("""
        <div class="feature-card">
            <h4>🔒 Privacy-Preserving</h4>
            <p>Your sensitive data remains encrypted throughout the matching process, ensuring your information stays private and secure.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_cols[1]:
        st.markdown("""
        <div class="feature-card">
            <h4>🔍 Advanced Matching</h4>
            <p>Our sophisticated algorithms find optimal matches based on complex preference criteria while respecting privacy constraints.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_cols[2]:
        st.markdown("""
        <div class="feature-card">
            <h4>🌐 Decentralized Architecture</h4>
            <p>Built on decentralized principles to ensure no single entity controls your data or the matching process.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Second row of features
    feature_cols2 = st.columns(3)
    
    with feature_cols2[0]:
        st.markdown("""
        <div class="feature-card">
            <h4>👥 Group Formation</h4>
            <p>Create and manage groups with shared preferences for collective matching opportunities.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_cols2[1]:
        st.markdown("""
        <div class="feature-card">
            <h4>📊 Transparent Scoring</h4>
            <p>Understand exactly how matches are scored with detailed breakdowns of compatibility factors.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_cols2[2]:
        st.markdown("""
        <div class="feature-card">
            <h4>🛡️ Data Control</h4>
            <p>Maintain full control over your data with tools to manage, export, or delete your information at any time.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent activity section
    st.markdown("<h2 style='margin-top:40px;margin-bottom:24px;'>Recent Activity</h2>", unsafe_allow_html=True)
    
    # Create tabs for different activity types
    tabs = st.tabs(["Recent Matches", "System Updates", "Community Highlights"])
    
    with tabs[0]:
        # First activity item
        col1, col2 = st.columns([1, 5])
        with col1:
            st.markdown("""
            <div style="background-color:#f2f6ff;border-radius:50%;width:40px;height:40px;display:flex;align-items:center;justify-content:center;">
                <span style="font-size:20px;">👤</span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='font-weight:500;'>Profile #1234 matched with Group #42</div>", unsafe_allow_html=True)
            st.markdown("<div style='color:var(--text-light);font-size:14px;'>2 hours ago • 92% match score</div>", unsafe_allow_html=True)
        
        st.markdown("<hr style='margin:16px 0;border:none;border-bottom:1px solid rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
        
        # Second activity item
        col1, col2 = st.columns([1, 5])
        with col1:
            st.markdown("""
            <div style="background-color:#f2f6ff;border-radius:50%;width:40px;height:40px;display:flex;align-items:center;justify-content:center;">
                <span style="font-size:20px;">👥</span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='font-weight:500;'>Group #56 matched with Group #78</div>", unsafe_allow_html=True)
            st.markdown("<div style='color:var(--text-light);font-size:14px;'>5 hours ago • 88% match score</div>", unsafe_allow_html=True)
        
        st.markdown("<hr style='margin:16px 0;border:none;border-bottom:1px solid rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
        
        # Third activity item
        col1, col2 = st.columns([1, 5])
        with col1:
            st.markdown("""
            <div style="background-color:#f2f6ff;border-radius:50%;width:40px;height:40px;display:flex;align-items:center;justify-content:center;">
                <span style="font-size:20px;">👤</span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='font-weight:500;'>Profile #5678 matched with Profile #9012</div>", unsafe_allow_html=True)
            st.markdown("<div style='color:var(--text-light);font-size:14px;'>Yesterday • 95% match score</div>", unsafe_allow_html=True)
    
    with tabs[1]:
        # First update item
        col1, col2 = st.columns([1, 5])
        with col1:
            st.markdown("""
            <div style="background-color:#f2f6ff;border-radius:50%;width:40px;height:40px;display:flex;align-items:center;justify-content:center;">
                <span style="font-size:20px;">🚀</span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='font-weight:500;'>Matching algorithm v2.4 deployed</div>", unsafe_allow_html=True)
            st.markdown("<div style='color:var(--text-light);font-size:14px;'>1 day ago • 15% performance improvement</div>", unsafe_allow_html=True)
        
        st.markdown("<hr style='margin:16px 0;border:none;border-bottom:1px solid rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
        
        # Second update item
        col1, col2 = st.columns([1, 5])
        with col1:
            st.markdown("""
            <div style="background-color:#f2f6ff;border-radius:50%;width:40px;height:40px;display:flex;align-items:center;justify-content:center;">
                <span style="font-size:20px;">🔒</span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='font-weight:500;'>Privacy protocol updated to v3.1</div>", unsafe_allow_html=True)
            st.markdown("<div style='color:var(--text-light);font-size:14px;'>3 days ago • Enhanced encryption standards</div>", unsafe_allow_html=True)
        
        st.markdown("<hr style='margin:16px 0;border:none;border-bottom:1px solid rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
        
        # Third update item
        col1, col2 = st.columns([1, 5])
        with col1:
            st.markdown("""
            <div style="background-color:#f2f6ff;border-radius:50%;width:40px;height:40px;display:flex;align-items:center;justify-content:center;">
                <span style="font-size:20px;">📱</span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='font-weight:500;'>Mobile interface improvements</div>", unsafe_allow_html=True)
            st.markdown("<div style='color:var(--text-light);font-size:14px;'>1 week ago • Better responsive design</div>", unsafe_allow_html=True)
    
    with tabs[2]:
        # First highlight item
        col1, col2 = st.columns([1, 5])
        with col1:
            st.markdown("""
            <div style="background-color:#f2f6ff;border-radius:50%;width:40px;height:40px;display:flex;align-items:center;justify-content:center;">
                <span style="font-size:20px;">🏆</span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='font-weight:500;'>Group #42 reached 100 successful matches</div>", unsafe_allow_html=True)
            st.markdown("<div style='color:var(--text-light);font-size:14px;'>This week • Community milestone</div>", unsafe_allow_html=True)
        
        st.markdown("<hr style='margin:16px 0;border:none;border-bottom:1px solid rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
        
        # Second highlight item
        col1, col2 = st.columns([1, 5])
        with col1:
            st.markdown("""
            <div style="background-color:#f2f6ff;border-radius:50%;width:40px;height:40px;display:flex;align-items:center;justify-content:center;">
                <span style="font-size:20px;">👏</span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='font-weight:500;'>New community guide published</div>", unsafe_allow_html=True)
            st.markdown("<div style='color:var(--text-light);font-size:14px;'>2 weeks ago • Best practices for matching</div>", unsafe_allow_html=True)
        
        st.markdown("<hr style='margin:16px 0;border:none;border-bottom:1px solid rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
        
        # Third highlight item
        col1, col2 = st.columns([1, 5])
        with col1:
            st.markdown("""
            <div style="background-color:#f2f6ff;border-radius:50%;width:40px;height:40px;display:flex;align-items:center;justify-content:center;">
                <span style="font-size:20px;">🌟</span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='font-weight:500;'>Profile #7890 recognized for privacy advocacy</div>", unsafe_allow_html=True)
            st.markdown("<div style='color:var(--text-light);font-size:14px;'>Last month • Community contribution</div>", unsafe_allow_html=True)
    
    # Call-to-action section at the bottom
    st.markdown("""
    <div style="background:linear-gradient(135deg, var(--primary-color), var(--primary-dark));border-radius:16px;padding:32px;margin-top:40px;color:white;text-align:center;">
        <h2 style="margin-top:0;color:white;margin-bottom:16px;">Ready to get started?</h2>
        <p style="font-size:18px;max-width:600px;margin:0 auto 24px auto;opacity:0.9;">
            Create your profile now and experience the power of privacy-preserving matching.
        </p>
        <div style="display:inline-block;background:white;color:var(--primary-color);padding:12px 24px;border-radius:8px;font-weight:600;box-shadow:0 4px 12px rgba(0,0,0,0.2);">
            Create Profile
        </div>
    </div>
    """, unsafe_allow_html=True)

def profiles_page() -> None:
    """Profiles page for managing user profiles."""
    # Load custom CSS
    load_css()
    
    # Page header with modern styling
    st.markdown('<div class="app-header">', unsafe_allow_html=True)
    st.markdown('<span class="app-logo">👤</span>', unsafe_allow_html=True)
    st.markdown('<div><h1 style="margin:0">Profiles</h1><p style="margin:0;color:var(--text-light)">Create and manage your personal profiles</p></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Create tabs for different profile actions
    tabs = st.tabs(["My Profiles", "Create Profile", "Import/Export"])
    
    with tabs[0]:
        st.markdown("<h3>Your Profiles</h3>", unsafe_allow_html=True)
        
        # Fetch profiles
        profiles_response = make_api_request("/profiles/")
        
        if "error" in profiles_response:
            st.error(f"Failed to load profiles: {profiles_response['error']}")
        elif not profiles_response:
            st.markdown("""
            <div style="background-color:#f8f9fa;border-radius:12px;padding:24px;text-align:center;margin:20px 0;">
                <div style="font-size:48px;margin-bottom:16px;">👤</div>
                <h3 style="margin-top:0;margin-bottom:8px;">No Profiles Yet</h3>
                <p style="color:var(--text-light);margin-bottom:20px;">Create your first profile to get started with matching.</p>
                <div style="display:inline-block;background:linear-gradient(135deg, var(--primary-color), var(--primary-dark));color:white;padding:10px 20px;border-radius:8px;font-weight:500;box-shadow:0 4px 12px rgba(67,97,238,0.2);">
                    Create Profile
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Display profiles in a grid
            profile_cols = st.columns(3)
            
            for i, profile in enumerate(profiles_response):
                with profile_cols[i % 3]:
                    # Create a profile card with modern styling
                    st.markdown(f"""
                    <div class="profile-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                            <h3 style="margin:0;font-size:18px;">{profile.get('name', 'Unnamed Profile')}</h3>
                            <div style="background-color:#f2f6ff;border-radius:50%;width:40px;height:40px;display:flex;align-items:center;justify-content:center;">
                                <span style="font-size:20px;">👤</span>
                            </div>
                        </div>
                        <p style="color:var(--text-light);margin-bottom:16px;font-size:14px;">ID: {profile.get('id', 'Unknown')}</p>
                        <p style="margin-bottom:20px;">{profile.get('description', 'No description')}</p>
                        <div style="display:flex;gap:8px;">
                            <div class="primary-button">
                                <button style="width:100%;">Select</button>
                            </div>
                            <button style="width:100%;">Edit</button>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Add functional buttons below the card
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Select", key=f"select_{profile['id']}"):
                            st.session_state.active_profile_id = profile['id']
                            st.success(f"Selected profile: {profile.get('name', 'Unnamed Profile')}")
                            st.experimental_rerun()
                    with col2:
                        if st.button(f"Delete", key=f"delete_{profile['id']}"):
                            delete_response = make_api_request(f"/profiles/{profile['id']}", method="DELETE")
                            if "error" in delete_response:
                                st.error(f"Failed to delete profile: {delete_response['error']}")
                            else:
                                if st.session_state.active_profile_id == profile['id']:
                                    st.session_state.active_profile_id = None
                                st.success("Profile deleted successfully!")
                                st.experimental_rerun()
            
            # Display active profile indicator
            if st.session_state.active_profile_id:
                active_profile = next((p for p in profiles_response if p['id'] == st.session_state.active_profile_id), None)
                if active_profile:
                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg, #e6f0ff, #f2f6ff);border-radius:12px;padding:16px;margin-top:24px;border:1px solid rgba(67,97,238,0.1);">
                        <div style="display:flex;align-items:center;gap:12px;">
                            <div style="background-color:var(--primary-color);border-radius:50%;width:32px;height:32px;display:flex;align-items:center;justify-content:center;color:white;">
                                <span style="font-size:16px;">✓</span>
                            </div>
                            <div>
                                <p style="margin:0;font-weight:500;">Active Profile: {active_profile.get('name', 'Unnamed Profile')}</p>
                                <p style="margin:0;color:var(--text-light);font-size:14px;">ID: {active_profile.get('id', 'Unknown')}</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    with tabs[1]:
        st.markdown("<h3>Create New Profile</h3>", unsafe_allow_html=True)
        
        # Create a form with modern styling
        with st.form("create_profile_form"):
            st.markdown("""
            <div style="margin-bottom:20px;">
                <p style="color:var(--text-light);">Fill out the form below to create a new profile. Your profile will be used for matching with other users and groups.</p>
            </div>
            """, unsafe_allow_html=True)
            
            name = st.text_input("Profile Name", placeholder="Enter a name for your profile")
            description = st.text_area("Description", placeholder="Describe yourself or the purpose of this profile")
            
            # Preferences section with collapsible UI
            with st.expander("Preferences (Optional)", expanded=False):
                st.markdown("""
                <div style="margin-bottom:16px;">
                    <p style="color:var(--text-light);font-size:14px;">
                        Preferences help the matching engine find better matches for you. 
                        All preference data is encrypted and protected.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                interests = st.multiselect(
                    "Interests",
                    options=["Technology", "Science", "Art", "Music", "Sports", "Travel", "Food", "Literature", "Movies", "Gaming"],
                    default=[]
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    age = st.slider("Age", min_value=18, max_value=100, value=25)
                with col2:
                    location = st.text_input("Location", placeholder="City, Country")
                
                experience_level = st.select_slider(
                    "Experience Level",
                    options=["Beginner", "Intermediate", "Advanced", "Expert"]
                )
                
                availability = st.multiselect(
                    "Availability",
                    options=["Weekdays", "Weekends", "Mornings", "Afternoons", "Evenings"],
                    default=[]
                )
            
            # Privacy settings
            with st.expander("Privacy Settings", expanded=False):
                st.markdown("""
                <div style="margin-bottom:16px;">
                    <p style="color:var(--text-light);font-size:14px;">
                        Control how your profile data is shared and used in the matching process.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                share_contact_info = st.checkbox("Share contact information with matches", value=False)
                visible_to_groups = st.checkbox("Visible to groups", value=True)
                visible_to_individuals = st.checkbox("Visible to individuals", value=True)
                
                anonymity_level = st.select_slider(
                    "Anonymity Level",
                    options=["Low", "Medium", "High", "Maximum"],
                    value="Medium"
                )
            
            # Submit button with modern styling
            st.markdown('<div class="primary-button">', unsafe_allow_html=True)
            submit_button = st.form_submit_button("Create Profile")
            st.markdown('</div>', unsafe_allow_html=True)
            
            if submit_button:
                if not name:
                    st.error("Profile name is required")
                else:
                    # Prepare preferences
                    preferences = {
                        "interests": interests,
                        "age": age,
                        "location": location,
                        "experience_level": experience_level,
                        "availability": availability,
                        "privacy": {
                            "share_contact_info": share_contact_info,
                            "visible_to_groups": visible_to_groups,
                            "visible_to_individuals": visible_to_individuals,
                            "anonymity_level": anonymity_level
                        }
                    }
                    
                    # Create profile
                    profile_data = {
                        "name": name,
                        "description": description,
                        "preferences": preferences
                    }
                    
                    response = make_api_request("/profiles/", method="POST", data=profile_data)
                    
                    if "error" in response:
                        st.error(f"Failed to create profile: {response['error']}")
                    else:
                        st.success("Profile created successfully!")
                        # Set as active profile
                        st.session_state.active_profile_id = response["id"]
                        st.experimental_rerun()
    
    with tabs[2]:
        st.markdown("<h3>Import/Export Profiles</h3>", unsafe_allow_html=True)
        
        # Create columns for import and export
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <h4>📤 Export Profile</h4>
                <p>Export your profile data as a JSON file for backup or transfer to another system.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Profile selection for export
            profiles_response = make_api_request("/profiles/")
            if "error" not in profiles_response and profiles_response:
                profile_options = {p["id"]: p["name"] for p in profiles_response}
                selected_profile_id = st.selectbox(
                    "Select profile to export",
                    options=list(profile_options.keys()),
                    format_func=lambda x: profile_options.get(x, "Unknown")
                )
                
                if st.button("Export Profile", key="export_profile"):
                    profile_data = make_api_request(f"/profiles/{selected_profile_id}")
                    if "error" in profile_data:
                        st.error(f"Failed to export profile: {profile_data['error']}")
                    else:
                        # Convert to JSON and create download link
                        profile_json = json.dumps(profile_data, indent=2)
                        b64 = base64.b64encode(profile_json.encode()).decode()
                        filename = f"profile_{selected_profile_id}_{datetime.now().strftime('%Y%m%d')}.json"
                        href = f'<a href="data:application/json;base64,{b64}" download="{filename}" class="download-button">Download Profile JSON</a>'
                        st.markdown(f"""
                        <div style="margin-top:16px;text-align:center;">
                            {href}
                        </div>
                        <style>
                            .download-button {{
                                display: inline-block;
                                background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
                                color: white;
                                padding: 10px 20px;
                                border-radius: 8px;
                                text-decoration: none;
                                font-weight: 500;
                                box-shadow: 0 4px 12px rgba(67,97,238,0.2);
                                transition: all 0.2s ease;
                            }}
                            .download-button:hover {{
                                transform: translateY(-2px);
                                box-shadow: 0 6px 16px rgba(67,97,238,0.3);
                            }}
                        </style>
                        """, unsafe_allow_html=True)
            else:
                st.info("No profiles available for export")
        
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h4>📥 Import Profile</h4>
                <p>Import a profile from a JSON file to restore from backup or transfer from another system.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # File uploader for import
            uploaded_file = st.file_uploader("Upload profile JSON file", type=["json"])
            
            if uploaded_file is not None:
                try:
                    profile_data = json.load(uploaded_file)
                    # Remove ID to create a new profile
                    if "id" in profile_data:
                        del profile_data["id"]
                    
                    # Add "Imported" to the name
                    if "name" in profile_data:
                        profile_data["name"] = f"{profile_data['name']} (Imported)"
                    
                    if st.button("Import Profile", key="import_profile"):
                        response = make_api_request("/profiles/", method="POST", data=profile_data)
                        
                        if "error" in response:
                            st.error(f"Failed to import profile: {response['error']}")
                        else:
                            st.success("Profile imported successfully!")
                            st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error parsing profile data: {str(e)}")
                    
    # Help section at the bottom
    st.markdown("""
    <div style="background-color:#f8f9fa;border-radius:12px;padding:20px;margin-top:40px;border:1px solid rgba(0,0,0,0.05);">
        <h4 style="margin-top:0;">💡 Profile Tips</h4>
        <ul style="margin-bottom:0;">
            <li>Create multiple profiles for different purposes or contexts</li>
            <li>Add detailed preferences to improve your matching results</li>
            <li>Export your profiles regularly for backup</li>
            <li>Use the privacy settings to control how your data is shared</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

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
    # Initialize session state at the beginning of main
    initialize_session_state()
    
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
        st.title("Universa - UniPriv")
        st.caption("Decentralized Matching Engine")
        
        if USE_MOCK_API:
            st.warning("⚠️ DEMO MODE: Using mock data")
        
        st.markdown("---")
        
        # Navigation
        st.subheader("Navigation")
        selection = st.radio("Select Page", PAGES, label_visibility="collapsed")
        
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
        st.markdown("""<div style="position: fixed; bottom: 0; width: 100%; text-align: center; padding: 1rem; opacity: 0.7; font-size: 0.8rem;">Universa - UniPriv © 2023</div>""", unsafe_allow_html=True)
    
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