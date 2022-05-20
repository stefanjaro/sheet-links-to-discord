# import libraries
import os
import datetime
from zoneinfo import ZoneInfo
import json
import pygsheets
import pandas as pd
from dotenv import load_dotenv

# load environment variables

# load from dotenv file -- comment out in production
load_dotenv()

def create_google_sheets_api_key():
    """
    Loads individual environment variables to form the google sheets API key
    """
    # get google sheets api key components
    gsak_type = os.getenv("gsak_type")
    gsak_project_id = os.getenv("gsak_project_id")
    gsak_private_key_id = os.getenv("gsak_private_key_id")
    gsak_private_key = os.getenv("gsak_private_key")
    gsak_client_email = os.getenv("gsak_client_email")
    gsak_client_id = os.getenv("gsak_client_id")
    gsak_auth_uri = os.getenv("gsak_auth_uri")
    gsak_token_uri = os.getenv("gsak_token_uri")
    gsak_auth_provider_x509_cert_url = os.getenv("gsak_auth_provider_x509_cert_url")
    gsak_client_x509_cert_url = os.getenv("gsak_client_x509_cert_url")

    # create google sheets service account key
    GOOGLE_SHEETS_API_KEY = json.dumps({
        "type": gsak_type,
        "project_id": gsak_project_id,
        "private_key_id": gsak_private_key_id,
        "private_key": gsak_private_key,
        "client_email": gsak_client_email,
        "client_id": gsak_client_id,
        "auth_uri": gsak_auth_uri,
        "token_uri": gsak_token_uri,
        "auth_provider_x509_cert_url": gsak_auth_provider_x509_cert_url,
        "client_x509_cert_url": gsak_client_x509_cert_url
    })

    return GOOGLE_SHEETS_API_KEY

# set environment variable
os.environ["GOOGLE_SHEETS_API_KEY"] = create_google_sheets_api_key()

def load_google_sheet(serv_acc_env_var, file_name, tab_name):
    """
    Creates and authorizes a connection to the Google API
    Must ensure the Google Sheets and Drive APIs have been enabled for the service account
    Then loads a table within a Google Sheet and returns a pygsheets object
    """
    # authorize a connection to the Google API
    conn = pygsheets.authorize(service_account_env_var=serv_acc_env_var)

    # open the google spreadsheet and the relevant tab within it
    # before running this, it's important to share the sheet with the service account email
    gsheet = conn.open(file_name).worksheet_by_title(tab_name)

    return gsheet

def write_to_google_sheet(gsheet, df):
    """
    Completely overwrites a Google Sheet with a Pandas dataframe
    """
    gsheet.set_dataframe(df, (1,1))
    return None

def convert_to_pandas_df(gsheet):
    """
    Converts our Google Sheet object of links into a Pandas dataframe
    Sets the right data types
    """
    # convert to pandas df
    links_df = gsheet.get_as_df()

    # adjusts all data types
    links_df["id"] = links_df["id"].astype(int)
    links_df["to_publish_date_lka"] = pd.to_datetime(links_df["to_publish_date_lka"])
    links_df["to_publish_time_lka"] = links_df["to_publish_time_lka"].astype(int)
    links_df["posted_indicator"] = links_df["posted_indicator"].astype(int)

    return links_df

def get_link_to_post(links_df):
    """
    Get the link that we need to post on Discord based on the date and time
    it needs to be posted and make sure it hasn't already been posted
    """
    # get the current date and time in colombo, sri lanka
    current_datetime = datetime.datetime.now(tz=ZoneInfo("Asia/Colombo"))

    # split into date and hour
    current_date = current_datetime.date()
    current_hour = current_datetime.hour

    # sort links_df by date and time
    links_df = links_df.sort_values(["to_publish_date_lka", "to_publish_time_lka"], ascending=True)

    # get the links that have been assigned for the current date
    # and have a publish time before or during the current hour
    # and haven't already been published yet
    # if there's multiple return only the first record (edge case handling)
    rel_link = links_df[
        (links_df["to_publish_date_lka"] == pd.to_datetime(current_date)) &
        (links_df["to_publish_time_lka"] <= current_hour) &
        (links_df["posted_indicator"] == 0)
    ].head(1)
            
    return rel_link

def update_posted_indicator(gsheet, links_df, rel_link):
    """
    After the link has been shared, update the posted_indicator
    of the link on the Google Sheet
    """
    # update the posted_indicator of the link we posted
    links_df.loc[links_df["id"] == rel_link["id"].item(), "posted_indicator"] = 1

    # write this to the google sheet
    write_to_google_sheet(gsheet, links_df)

if __name__ == "__main__":
    # load a google sheet
    gsheet = load_google_sheet("GOOGLE_SHEETS_API_KEY", "Resources to Share with SLDE Discord", "Original")

    # turn it into a pandas dataframe and set the right datatypes
    links_df = convert_to_pandas_df(gsheet)

    # get the link that needs to be posted
    rel_link = get_link_to_post(links_df)