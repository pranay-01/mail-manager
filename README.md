# mail-manager

## Step 1: Clone the project into your local

## Step 2: Navigate to the root of the project, and install python packages(make sure you have python3.8 or above installed in your local) and run this command:

- "pip install -r requirements.txt"


## Step 3: Authenticate and Access Gmail API

To authenticate and access the Gmail API in Python, you typically use OAuth 2.0 for authorization. Below are the general steps:

### 1. Create a Google Cloud Platform (GCP) Project

- Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project if you haven't already.
- Enable the Gmail API:
  - In the Google Cloud Console, navigate to **APIs & Services > Library**.
  - Search for "Gmail API" and enable it for your project.

### 2. Create OAuth 2.0 Credentials

- Go to **APIs & Services > Credentials**.
- Click on "Create Credentials" and select "OAuth client ID".
- Choose the application type (typically "Desktop app" or "Web application" for Python applications).
- Click "Create" to generate your OAuth 2.0 client ID and client secret.
- Download json credentials file and rename it to "creds.json" file and put it in the root of the project.


## Step 4: Verify the rules.json file

- Make sure to add your rules according to the emails you have in your inbox, to actually see the working results of the script.

## Step 5: Run the app.py

- "python/python3 app.py"
