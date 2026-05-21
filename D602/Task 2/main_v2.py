# Main version 2

import subprocess
import sys
import logging
import argparse
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename="main_pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def run_step(script_name, step_description, extra_args=None):
    # Run the pipeline as a subprocess and log the results

    logging.info(f"Starting {step_description}")
    print(f" {step_description}")

    cmd = [sys.executable, script_name]
    if extra_args:
        cmd.extend(extra_args)

    start = time.time()
    result = subprocess.run(cmd,capture_output=True, text=True)
    elapsed = round(time.time() - start, 2)

    if result.returncode == 0:
        logging.info(f"Completed in {elapsed} seconds: {step_description}")
        if result.stdout:
            logging.info(f"Output {result.stderr.strip()}")
        print(f" Status: Success ({elapsed}s)")
        if result.stdout:
            print(result.stdout.strip())

    else:
        logging.error(f"Failed after {elapsed} seconds: {step_description}")
        logging.error(f"STDERR: {result.stderr.strip()}")
        print(f" Status: Failure ({elapsed}s)")
        print(f" Error: {result.stderr.strip()}")
        sys.exit(1)

    return elapsed


def parse_args():
    parser = argparse.ArgumentParser(
        description="Flight Delay Prediction Pipeline"
    )
    parser.add_argument(
        "--num_alphas",
        type=int,
        default=20,
        help="Number of alpha values to test during model training (default: 20)"
    )
    parser.add_argument(
        "--order",
        type=int,
        default=1,
        help="Polynomial feature order for the regression model (default: 1)"
    )

    return parser.parse_args()

def main():
    args = parse_args()

    logging.info("Pipeline started")
    logging.info(f"Parameters: num_alphas={args.num_alphas}, order={args.order}")

    print(f"Flight Delay Prediction Pipeline")
    print(f" Start: {datetime.now()}")
    print(f" Parameters: num_alphas={args.num_alphas}, order={args.order}")

    timings = {}

    # import the data
    timings["Import"] = run_step(
        "import_data_v2.py",
        "Step 1: Data Import"
    )

    # Clean the data
    timings["Clean"] = run_step(
        "clean_data_v2.py",
        "Step 2: Data Cleaning"
    )

    # Train the model
    timings["Train"] = run_step(
        "poly_regresssor_Python_v2.py",
        "Step 3: Model Training",
        extra_args=["--num_alphas", str(args.num_alphas), "--order", str(args.order)]
    )

    # Create a summary
    total = round(sum(timings.values()), 2)
    logging.info(f"Pipeline completed. Total time: {total}")

    print(f" Pipeline completed successfully")
    print(f" End: {datetime.now()}")
    print(f"\n Step timings:")
    for step, t in timings.items():
        print(f" {step:<10} {t}s")
    print(f" {'Total':<10} {t}s")

if __name__ == "__main__":
    main()

