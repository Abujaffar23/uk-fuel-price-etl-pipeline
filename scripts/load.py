import os
import logging
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(), logging.FileHandler("/opt/airflow/logs/file_logs.log")])


database_url = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{quote_plus(os.getenv('DB_PASSWORD'))}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(database_url)


def load(df):

    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        logging.error("DataFrame is empty or not a valid DataFrame. Load operation cannot be performed.")
        return None

    logging.info("starting data load process ...")

    with engine.begin() as connection:

        try:
            fuel_price = df[["site_id", "brand", "standard_diesel_b7", "super_petrol_e5", "standard_petrol_e10", "super_diesel_sdv"]].copy()

            fuel_price.to_sql("temp_price", con=connection, if_exists="replace", index=False)
            upsert_price = text("""
                            INSERT INTO fuel_price (site_id, brand, standard_diesel_b7, super_petrol_e5, standard_petrol_e10, super_diesel_sdv)
                            SELECT site_id, brand, standard_diesel_b7, super_petrol_e5, standard_petrol_e10, super_diesel_sdv
                            FROM temp_price
                            ON CONFLICT (site_id)
                            DO UPDATE SET
                                brand = EXCLUDED.brand,
                                standard_diesel_b7 = EXCLUDED.standard_diesel_b7,
                                super_petrol_e5 = EXCLUDED.super_petrol_e5,
                                standard_petrol_e10 = EXCLUDED.standard_petrol_e10,
                                super_diesel_sdv = EXCLUDED.super_diesel_sdv; """)
            connection.execute(upsert_price)
            connection.execute(text("DROP TABLE IF EXISTS temp_price;"))
            logging.info("Successfully loaded into fuel_price")

            fuel_location = df[["site_id", "address", "postcode", "latitude", "longitude"]]

            fuel_location.to_sql("temp_location", con=connection, if_exists="replace", index=False)
            insert_location = text("""
                            INSERT INTO fuel_location (site_id, postcode, latitude, longitude, address)
                            SELECT site_id, postcode, latitude, longitude, address
                            FROM temp_location
                            ON CONFLICT (site_id) DO NOTHING;
                        """)
            connection.execute(insert_location)
            connection.execute(text("DROP TABLE IF EXISTS temp_location;"))
            logging.info("Successfully loaded into fuel_location")

            logging.info("All data successfully synced into the database.")
            return True

        except Exception as e:
            logging.exception(f"Data Loading failed: {e}")
            raise



        

