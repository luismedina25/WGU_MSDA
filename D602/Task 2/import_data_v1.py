# Import for the raw csv
# Basic import and save file

import pandas as pd
import logging

#Configure logger
logging.basicConfig(
    filename='imported_data.log',
    filemode='w',
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG
)
logging.getLogger('matplotlib.font_manager').disabled = True
logging.info("Data Import Script Version 1")

#Load in the file
input_file = "T_ONTIME_REPORTING.csv"

df = pd.read_csv(input_file)
logging.info(f"Loaded {len(df)} rows from {input_file}")
print(f"Loaded {len(df)} rows")
print("Columns found: ", df.columns.tolist())

# Remap the columns to match the ones in the file
rename_map = {
    'YEAR': 'YEAR',
    'MONTH': 'MONTH',
    'DAY_OF_MONTH': 'DAY',
    'DAY_OF_WEEK': 'DAY_OF_WEEK',
    'ORIGIN': 'ORG_AIRPORT',
    'DEST': 'DEST_AIRPORT',
    'CRS_DEP_TIME': 'SCHEDULED_DEPARTURE',
    'DEP_TIME': 'DEPARTURE_TIME',
    'DEP_DELAY': 'DEPARTURE_DELAY',
    'CRS_ARR_TIME': 'SCHEDULED_ARRIVAL',
    'ARR_TIME': 'ARRIVAL_TIME',
    'ARR_DELAY': 'ARRIVAL_DELAY'
}

df = df.rename(columns=rename_map)
df = df[list(rename_map.values())]

# Save the formatted data
output_file = "imported_data.csv"
df.to_csv(output_file, index=False)
logging.info(f"Saved {len(df)} rows to {output_file}")
print(f"Done. Saved {len(df)} rows to {output_file}")

logging.shutdown()

