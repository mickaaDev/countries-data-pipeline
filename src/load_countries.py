import os
import requests
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()


def get_database_connection():
    db_user = os.getenv('POSTGRES_USER')
    db_password = os.getenv('POSTGRES_PASSWORD')
    db_name = os.getenv('POSTGRES_DB')
    db_host = 'localhost'
    db_port = os.getenv('POSTGRES_PORT')
    
    connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    return create_engine(connection_string)



def fetch_countries_data():

    api_url = os.getenv('COUNTRIES_API_URL')
    response = requests.get(api_url)
    response.raise_for_status()
    return response.json()


def transform_data(data):

    df = pd.json_normalize(data)
    df = df[['name.common', 'name.official', 'capital', 'region', 'subregion', 'population', 'area', 'flags.png']]
    
    df.rename(columns={
        'name.common': 'country',
        'name.official': 'official_name', 
        'capital': 'capital',
        'region': 'region',
        'subregion': 'subregion',
        'population': 'population',
        'area': 'area',
        'flags.png': 'flag_url'
    }, inplace=True)
    
    df['capital'] = df['capital'].apply(lambda x: x[0] if isinstance(x, list) and x else 'Unknown')
    return df

def load_data_to_db(df, engine):
    df.to_sql('countries', engine, if_exists='replace', index=False, method='multi')



def main():
    
    try:
        data = fetch_countries_data()
        
        df = transform_data(data)
        
        engine = get_database_connection()
        
        load_data_to_db(df, engine)
        
        print(f"Successfully loaded {len(df)} countries to database!")
        
    except Exception as e:
        print(f"Error in pipeline: {e}")
        raise

if __name__ == "__main__":
    main()
