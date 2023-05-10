import os
import datetime
from google.oauth2 import service_account
from google.cloud import bigquery
from googleapiclient.discovery import build
import functions_framework
import settings

# Global variables
key_file = settings.key_file
site_url = os.environ.get("URL","Could not retreive url.")
search_types = ['web','image','video','news','googleNews','discover']

# Create dates list or return today's date
def set_date_range(payload):
    if ('start_date'in payload) and ('end_date' in payload):
        print('Creating date list...')
        start_date = datetime.date.fromisoformat(payload['start_date'])
        end_date = datetime.date.fromisoformat(payload['end_date'])
        dates_list = []
        current_date = start_date
        while current_date <= end_date:
            dates_list.append(current_date.isoformat())
            current_date += datetime.timedelta(days=1)
        print(f'Range of dates: {dates_list}.')
    else:
        print('Retrieving only recent date.')
        dates_list = []
        dates_list.append(datetime.date.today()-datetime.timedelta(days=2)).isoformat()
        print('Date is: {start_date}.')
    return dates_list

def connect_to_searchconsole():
    print('Generating credentials.')
    scope = ['https://www.googleapis.com/auth/webmasters']
    credentials = service_account.Credentials.from_service_account_file(key_file, scopes=scope)
    service = build("webmasters", "v3", credentials=credentials)
    return service

def fetch_api_data(site_url, search_type, start_date):
    # Adjust for different table types
    if search_type == 'discover':
        dimmensions = ["country","page"]
    elif search_type == 'googleNews':
        dimmensions = ["country","page","device"]
    else:
        dimmensions = ["country","page","device","query"]
    payload = {
        "startDate":start_date,
        "endDate":(datetime.date.fromisoformat(start_date)+datetime.timedelta(days=1)).isoformat(),
        "dimensions":dimmensions,
        "type":search_type,
        "rowLimit":int(os.environ.get("ROWS","Could not set row limit.")),
        "startRow":0
    }
    service = connect_to_searchconsole()
    print('Fetching data...')
    response = service.searchanalytics().query(siteUrl=site_url, body=payload).execute()
    print(f"{len(response['rows'])} lines of data retrieved.")
    return response['rows']

def add_metadata(fetched_data, type, start_date):
    for entry in fetched_data:
        if 'device' not in entry: entry['keys'].append('')
        if 'query' not in entry: entry['keys'].append('')
        if 'position' not in entry: entry['position'] = 0
        entry['type'] = type
        entry['date'] = start_date
    return fetched_data

def format_data(fetched_data):
    list = []
    for entry in fetched_data:
        formated = {
            'Country': entry['keys'][0],
            'URL': entry['keys'][1],
            'Device_Category': entry['keys'][2],
            'Query': entry['keys'][3],
            'Clicks': entry['clicks'],
            'Impressions': entry['impressions'],
            'Site_CTR': entry['ctr'],
            'Average_Position': entry['position'],
            'Search_Type': entry['type'],
            'Date': entry['date']
        }
        list.append(formated)
    return list

def insert_into_bigquery(fetched_data):
    client = bigquery.Client()
    datasetName = os.environ.get("DATASET", "Could not retreive dataset name.")
    dataset = client.dataset(datasetName)
    tableName = os.environ.get("TABLE", "Could not retreive table name.")
    table = dataset.table(tableName)
    table_nm = client.get_table(table)
    client.insert_rows(table_nm, fetched_data)

@functions_framework.http
def main(request):
    """
    Função de insert de dados do Search Console em tabelas do BigQuery.
    Payload recebe valores de start_date e end_date caso seja necessário trabalho em lotes.
    Ausência de valores resulta em uma atualização apenas dos dados recentes (últimos 2 dias).
    TO-DO: Escrever documentação técnica.
    """
    payload = request.get_json()
    dates_list = set_date_range(payload)
    
    for single_date in dates_list:
        print(f'Fetching data for date: {single_date}.')
        for type in search_types:
            print(f'Fetching type: {type}.')
            fetched_data = fetch_api_data(site_url, type, single_date)
            fetched_data = add_metadata(fetched_data, type, single_date)
            fetched_data = format_data(fetched_data)
            errors = insert_into_bigquery(fetched_data)
            if errors:
                print(errors)
    return "Done!"