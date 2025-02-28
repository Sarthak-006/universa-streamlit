# UNIVERSA Streamlit App Deployment Guide

This guide explains how to deploy the UNIVERSA Decentralized Matching Engine on Streamlit Cloud using GitHub.

## Prerequisites

- A GitHub account
- Your UNIVERSA codebase pushed to a GitHub repository

## Deployment Steps

### 1. Push Your Code to GitHub

Make sure your repository has the following structure:
```
repository-root/
├── streamlit_app.py       # Main entry point for Streamlit Cloud
├── requirements.txt       # All required dependencies
├── README.md              # Project documentation
└── src/                   # Source code folder
    └── frontend/
        └── app.py         # Your main Streamlit application logic
```

### 2. Deploy to Streamlit Cloud

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository, branch, and set the main file path to `streamlit_app.py`
5. (Optional) Add any secrets or environment variables:
   - `API_URL`: Your backend API URL (if not using the default)

### 3. Advanced Configuration

#### Environment Variables

If you need to set environment variables, you can add them in the Streamlit Cloud dashboard:
1. Go to your app settings
2. Add the secrets in TOML format, for example:
   ```toml
   [env]
   API_URL = "https://your-api-url.com"
   ```

#### Custom Domain

If you want to use a custom domain:
1. Go to your app settings in Streamlit Cloud
2. Navigate to the "Custom domain" section
3. Follow the instructions to set up DNS records for your domain

## Troubleshooting

If your app doesn't deploy correctly:

1. Check the app logs in the Streamlit Cloud dashboard
2. Ensure all dependencies are correctly listed in `requirements.txt`
3. Verify that `streamlit_app.py` is correctly importing from `src.frontend.app`
4. Make sure the API endpoint is accessible from Streamlit Cloud

## Local Development

To run the app locally before deploying:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

## Updating Your Deployment

When you push changes to your GitHub repository, Streamlit Cloud will automatically rebuild and redeploy your app. 