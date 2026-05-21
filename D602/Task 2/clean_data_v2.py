# Clean data Version 2
# Version 2 of cleaning, filter to LAX and other cleaning steps

import pandas as pd
import logging

# Configure Logger
logging.basicConfig(
    filename= "clean_data_v2.log",
    filemode= "w",
    format= "%(asctime)s %(levelname)s %(message)s",
    datefmt= "%H:%M:%S",
    level= logging.DEBUG
)

logging.getLogger('matplotlib.font_manager').disabled = True
logging.info("Data Cleaning Script Version 2")

airport = "LAX"
month = 1
input_file = "import_datav2.csv"
output_file = "cleaned_datav2.csv"

# Load the data
df = pd.read_csv(input_file)
logging.info(f"Loaded {len(df)} rows from {input_file}")
print(f"Loaded {len(df)} rows")

# First cleaning process
before = len(df)
df = df[df['ORG_AIRPORT'] == airport].copy()
logging.info(f"Step 1: {airport} filter: removed {before - len(df)} rows {len(df)} remaining")
print(f"After {airport} filter: {len(df)} rows")

# Filter the data to just January
before = len(df)
df = df[df['MONTH'] == month].copy()
logging.info(f"Step 2: Month filter (month={month}): removed {before - len(df)} rows, {len(df)} remaining")
print(f"After  month filter: {len(df)} rows")

# Remove any duplicate rows
before = len(df)
df = df.drop_duplicates()
logging.info(f"Step 3: Duplicates removed: {before - len(df)} rows, {len(df)} remaining")
print(f"After duplicates removed: {len(df)} rows")

# Remove rows where departure delay is null
before = len(df)
df = df.dropna(subset=['DEPARTURE_DELAY'])
logging.info(f"Step 4: Null values removed: {before - len(df)} rows, {len(df)} remaining")
print(f"After null values removed: {len(df)} rows")

# Remove rows where scheduled departures is null
before = len(df)
df = df.dropna(subset=['SCHEDULED_DEPARTURE'])
logging.info(f"Step 5: Null values removed: {before - len(df)} rows, {len(df)} remaining")
print(f"After null values removed: {len(df)} rows")

# Final report for logging
logging.info(f"Final cleaned dataset shape: {df.shape}")
logging.info(f"Null counts in final data:\n{df.isnull().sum().to_string()}")

# Save the new dataset
df.to_csv(output_file, index=False)
logging.info(f"Saved cleaned data to {output_file}")
print(f"\nDone. {len(df)} rows were saved to {output_file}")

logging.shutdown()