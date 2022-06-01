from google.oauth2 import service_account
from googleapiclient.discovery import build
import requests
import json
import pandas as pd

key = 'gglobo-dados-hdg-dev-2b110ae20235.json'
site_url = "sc-domain:ge.globo.com"
payload = {
    "startDate":"2022-01-01",
    "endDate":"2022-05-24",
    "dimensions":["page","device","query"],
    "rowLimit":10,
    "startRow":0
}

def connect(key):
    scope = ['https://www.googleapis.com/auth/webmasters']
    credentials = service_account.Credentials.from_service_account_file(key, scopes=scope)
    service = build(
        "webmasters",
        "v3",
        credentials=credentials
    )
    return service

service = connect(key)
def query(service, site_url, payload):
    response = service.searchanalytics().query(siteUrl=site_url, body=payload).execute()
    return response

print(query(service,site_url,payload))
