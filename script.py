import requests
import upwork
import json
import webbrowser
import urllib3
from bs4 import BeautifulSoup
import pandas as pd


def get_upwork_client():

    """This function sets up a client-server
    connection and keeps it for a day."""

    cred_file = open('credentials.json', 'r')
    cred_json = json.load(cred_file)
    cred_file.close()

    public_key = cred_json['public_key']
    secret_key = cred_json['secret_key']

    upwork_client = upwork.Client(public_key, secret_key)
    auth_url = upwork_client.auth.get_authorize_url()
    webbrowser.open(url=auth_url, autoraise=True, new=2)
    verifier = input(
        'Please enter the verification code you get '
        'following this link:\n{0}\n\n> '.format(auth_url))
    access_token, access_token_secret = \
        upwork_client.auth.get_access_token(verifier)
    upwork_client = upwork.Client(
        public_key, secret_key,
        oauth_access_token=access_token,
        oauth_access_token_secret=access_token_secret)
    return upwork_client


def get_user_id():

    """Get the ID of the currently logged in user"""

    user_info = get_upwork_client().hr.get_user_me(format=json)
    user_id = user_info["id"]
    return user_id


def get_rooms_org_id():

    """Get all the ID's of the org's that the rooms belongs to"""

    rooms_org_id = []
    rooms_info = get_upwork_client().messages.get_rooms(get_user_id())
    rooms_org_id.append([org["orgId"] for org in rooms_info["rooms"]])
    return rooms_org_id


def get_opened_jobs_urls():

    """Get the dictionary of 'Clients name':'Job URL' of all jobs
    the current user has `manage_recruiting` access to."""

    client_url_dict = {}
    for org in get_rooms_org_id():
        jobs_info = get_upwork_client().hr.get_jobs(org)
        client_url_dict.update(
            {
                job['created_by_name']: job['public_url']
                for job in jobs_info["jobs"]
             }
        )
    return client_url_dict


def get_job_postings_urls():

    """Get all URLs of the recently added job postings to the UpWork
    platform with the listed parameters. By default fetching URLs from
    the last 20 pages. Pass page_size as a parameter to search_jobs to
    set more or less pages to take"""

    """При запуске проверить данную функцию. На сайте пишут что обязательно 
    надо передавать параметры поиска, а внутри класса пишут что все параметры 
    опциональны"""

    jobs = get_upwork_client().provider_v2.search_jobs()
    job_postings_urls = [job['url'] for job in jobs]
    return job_postings_urls


def our_clients_identifier():

    """Gets one recent client's work like an identifier of the client.
    Response type: {'Job':'Name#1', 'Job':'Name#2', ...}"""

    our_client_jobs_dict = {}
    for names, urls in get_opened_jobs_urls().items():
        http = urllib3.PoolManager()
        url = urls
        response = http.request('GET', url)
        soup = BeautifulSoup(response.data, features="lxml")
        our_clients_recent_jobs = soup.select_one('img[title]')
        our_client_jobs_dict.update({our_clients_recent_jobs['title']: names})
    return our_client_jobs_dict


def random_clients_identifier():

    """Gets one recent client's work like an identifier of the client
    in all recently added offers on the platform.
    Response type: {'Job':'URL#1', 'Job':'URL#2', ...}"""

    random_url_jobs_dict = {}
    for urls in get_job_postings_urls():
        http = urllib3.PoolManager()
        url = urls
        response = http.request('GET', url)
        soup = BeautifulSoup(response.data, features="lxml")
        random_clients_recent_jobs = soup.select_one('img[title]')
        random_url_jobs_dict.update({random_clients_recent_jobs['title']: url})
    return random_url_jobs_dict


def compare_identifiers():

    """Compare identifiers of clients with whom we already talked to
    and hidden clients from all new job posts on upwork"""

    df1 = pd.Series(our_clients_identifier()).to_frame('df1')
    df2 = pd.Series(random_clients_identifier()).to_frame('df2')
    df3 = df1.join(df2).dropna().set_index('df1').to_dict()['df2']
    return df3


def send_slack_notifications():

    webhook_url = 'https://hooks.slack.com/services/' \
                  'T4C5C031A/B011AU4QNK0/ZVZyd2QjCE7bZDwp0xZCxMi4'
    messages = ['{}_{}'.format(name, job_url)
                for name, job_url in compare_identifiers().items()]
    for msg in messages:
        slack_msg = {'text': msg}
        requests.post(webhook_url, data=json.dumps(slack_msg))


send_slack_notifications()