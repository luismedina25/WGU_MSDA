# Import version 2 for the raw csv file
# Version 2 import with validation, missing columns, better logging

import pandas as pd
import logging
import sys

logging.basicConfig(
    filename= "import_datav2.log",
    filemode= "w",
    format= "[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt= "%H:%M:%S",
    level=logging.DEBUG
)
logging.getLogger('matplotlib.font_manager').disable = True
logging.info("Data Import Script Version 2")

# Remap the columns
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

# Numeric columns
int_cols = [
    'YEAR', 'MONTH', 'DAY', 'DAY_OF_WEEK',
    'SCHEDULED_DEPARTURE', 'DEPARTURE_TIME',
    'SCHEDULED_ARRIVAL', 'ARRIVAL_TIME'
]

# Create the import function
def import_data(input_file="T_ONTIME_REPORTING.csv", output_file="import_datav2.csv"):
    """

    Parameters
    ----------
    input_file: str
        Path to the raw CSV file
    output_file: str
        Path to the output CSV file

    Returns
    -------
    """

    # Load the file
    try:
        df = pd.read_csv(input_file, encoding='utf-8-sig', low_memory=False)
        logging.info(f"Loaded {len(df)} rows and {len(df.columns)} columns from {input_file}")
    except FileNotFoundError:
        logging.error(f"File not found: {input_file}")
        print(f"Error: Could not find {input_file}")
        sys.exit()

    # Check for missing columns
    missing = [col for col in rename_map.keys() if col not in df.columns]
    if missing:
        logging.warning(f"Missing expected columns: {missing}")
        print(f"Warning: Missing expected columns: {missing}")
    else:
        logging.info("All expected columns found in source file")


    # Rename the columns
    existing_map = {k: v for k, v in rename_map.items() if k in df.columns}
    df = df.rename(columns=existing_map)
    logging.info(f"Renamed {len(existing_map)} columns")

    # Keep only the columns needed
    target_cols = [v for v in rename_map.values() if v in df.columns]
    df = df[target_cols]
    logging.info(f"Kept {len(target_cols)} target columns")

    # Use numeric types
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    logging.info("Numeric type enforcement complete")

    for col in ['DEPARTURE_DELAY', 'ARRIVAL_DELAY']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Create the log summary
    logging.info(f"Final shape after formatting: {df.shape}")
    logging.info(f"Columns: {df.columns.tolist()}")
    logging.info(f"Null counts:\n{df.isnull().sum().to_string()}")

    # Save everything
    df.to_csv(output_file, index=False)
    logging.info(f"Saved formatted data to {output_file}")
    print(f"Import complete. {len(df)} rows saved to {output_file}")

    return df


if __name__ == "__main__":
    import_data()


logging.shutdown()



