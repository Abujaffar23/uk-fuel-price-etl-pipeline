
import logging 
import pandas as pd 


logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[ logging.StreamHandler(), logging.FileHandler("file_logs.log")])


def transform(df):

    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        logging.error("DataFrame is empty or not a valid DataFrame. Transformation cannot be performed.")
        return None

    try:
        logging.info("Starting data Transformation process...")

        df['last_updated'] = pd.to_datetime(df['last_updated'], errors='coerce')

        logging.info("datetime Transformation successful")

        df.drop_duplicates(subset=['site_id'], keep='first', inplace=True)

        logging.info(f"duplicate Transformation successful with {len(df)} records remaining")

        df.columns = df.columns.str.lower()

        #df.dropna(inplace=True)

        logging.info(f"rows length after Trasnsformation is {len(df)}")

        logging.info("Data Transformation completed successfully.")

        df.to_csv("/opt/airflow/output/transformed_uk_fuel_prices.csv", index=False)

        logging.info("Transformed data saved to 'transformed_uk_fuel_prices.csv'.")



    except Exception as e:
        logging.error(f"An error occurred during data transformation: {e}")
        return None

    return df


