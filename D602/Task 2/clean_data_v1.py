# Clean data Version 1
# Version 1 of cleaning the data and filtering LAX as the only airport

import pandas as pd
import logging

logging.basicConfig(
    filename="clean_data_v1.log",
    filemode="w",
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt= "%H:%M:%S",
    level=logging.DEBUG
)

logging.getLogger('matplotlib.font_manager').disabled = True
logging.info("Data Cleaning Script Version 1")

airport = "LAX"
input_file = "import_datav2.csv"
output_file = "cleaned_datav1.csv"

# Load in the data
df = pd.read_csv(input_file)
logging.info(f"Loaded {len(df)} rows from {input_file}")
print(f"Loaded {len(df)} rows")


# Filter to only LAX departures
df =df[df['ORG_AIRPORT'] == airport]
logging.info(f"After {airport} filter: {len(df)} rows remaining")
print(f"After {airport} filter: {len(df)} rows")

# Save the cleaned data set
df.to_csv(output_file, index=False)
logging.info(f"Saved {len(df)} rows to {output_file}")
print(f"Done. Saved {len(df)} rows to {output_file}")

logging.shutdown()
