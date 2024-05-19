import os

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from constants import ACCESS_SCOPES


def init_auth() -> Credentials:
    """
    function to initiate google authentication to further use the google apis

    :return:
    creds
    """
    creds = None

    if os.path.exists("token.json"):
        return Credentials.from_authorized_user_file("token.json")

    if creds:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file("creds.json", ACCESS_SCOPES)
        creds = flow.run_local_server(port=0)

    with open("token.json", "w") as t:
        t.write(creds.to_json())

    return creds


Service = build("gmail", "v1", credentials=init_auth())
