# Main version 1

import subprocess
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename="main_pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def run_step(script_name, step_description):
    # Run the pipeline step and log the result.
    logging.info(f"Starting: {step_description}")
    print(f"Running: {step_description}")

    result = subprocess.run(
        [sys.executable, script_name],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        logging.info(f"Completed successfully: {step_description}")
        print(f"Success: {step_description}")
        if result.stdout:
            print(result.stdout)
    else:
        logging.error(f"Error: {step_description}")
        logging.error(result.stderr)
        print(f"ERROR: {step_description} failed.")
        print(result.stderr)
        sys.exit(1)


def main():
    logging.info("Starting Pipeline")
    print(f"Flight Delay Prediction Pipeline")
    print(f"Start time: {datetime.now()}")

    # Import the data
    run_step("import_data_v2.py", "Import Data and Format it.")

    # Clean the data
    run_step("clean_data_v2.py", "Clean the data.")

    # Train the model
    run_step("poly_regressor_Python_v2.py", "Train the model.")

    logging.info("Pipeline Completed")
    print(f"Pipeline Completed.")
    print(f"End time: {datetime.now()}")

if __name__ == "__main__":
    main()