import os 
import logging
import requests  
import pandas as pd 

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(), logging.FileHandler("/opt/airflow/logs/file_logs.log")])


logging.info("ETL Pipeline Started ")

def extract():
    try:
        url = "https://uk-daily-fuel-prices.p.rapidapi.com/api/petrol-prices/fuel-type/E10"

        api_key = {
            "x-rapidapi-key": os.getenv("Api_key"),
            "x-rapidapi-host": "uk-daily-fuel-prices.p.rapidapi.com",
            "Content-Type": "application/json",
        }
        
        querystring = {"min": "130", "max": "140", "type": "E10", "limit": "50"}

        response = requests.get(url=url, headers=api_key, params=querystring)

        if response.status_code == 200:
            logging.info(f"api requests successfully with status code {response.status_code}")
            data = response.json()
        else:
            logging.info(f"api requests failed with status code {response.status_code}")
            return None

        records = []
        for key in data['data']:
            try:
                location = key.get("location") or []
                if location and isinstance(location, dict):
                    latitude = location.get("latitude")
                    longitude = location.get("longitude")
                else:
                    latitude = None
                    longitude = None

                price = key.get("prices") or {}

                if price and isinstance(price, dict):

                 B7_p = price.get("B7")
                 E5_p = price.get("E5")
                 E10_p = price.get("E10")
                 SDV_P = price.get("SDV")

                else:
                   B7_p = None
                   E5_p = None
                   E10_p= None
                   SDV_P = None

                records.append({
                    "site_id": key.get("site_id"),
                    "brand": key.get("brand"),
                    "address": key.get("address"),
                    "postcode": key.get("postcode"),
                    "latitude": latitude,
                    "longitude": longitude,
                    "standard_diesel_b7": B7_p,
                    "super_petrol_e5": E5_p,
                    "standard_petrol_e10": E10_p,
                    "super_diesel_sdv": SDV_P,
                    "last_updated": key.get("last_updated"),
                })
            except (KeyError, IndexError) as item_error:
                logging.warning(f"skipping a data record due to missing key: {item_error}")
                continue

        df = pd.DataFrame(records)
        logging.info(f"Len of data after extraction is {len(df)}")
        return df
    except Exception as e:
        logging.error(f"Extraction Failed with error {e}")
        return None

bronze = extract()
















        

        









        


