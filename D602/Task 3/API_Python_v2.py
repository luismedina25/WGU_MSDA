#!/usr/bin/env python
# coding: utf-8

# import statements
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import json
import numpy as np
import pickle
import datetime
import logging
from sklearn.preprocessing import PolynomialFeatures

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the airport encodings file
f = open('airport_encodings.json')
 
# returns JSON object as a dictionary
airports = json.load(f)
f.close()

def create_airport_encoding(airport: str, airports: dict) -> np.array:
    """
    create_airport_encoding is a function that creates an array the length of all arrival airports from the chosen
    departure aiport.  The array consists of all zeros except for the specified arrival airport, which is a 1.  

    Parameters
    ----------
    airport : str
        The specified arrival airport code as a string
    airports: dict
        A dictionary containing all of the arrival airport codes served from the chosen departure airport
        
    Returns
    -------
    np.array
        A NumPy array the length of the number of arrival airports.  All zeros except for a single 1 
        denoting the arrival airport.  Returns None if arrival airport is not found in the input list.
        This is a one-hot encoded airport array.

    """
    temp = np.zeros(len(airports))
    if airport in airports:
        temp[airports.get(airport)] = 1
        temp = temp.T
        return temp
    else:
        return None

# TODO:  write the back-end logic to provide a prediction given the inputs
# requires finalized_model.pkl to be loaded 
# the model must be passed a NumPy array consisting of the following:
# (polynomial order, encoded airport array, departure time as seconds since midnight, arrival time as seconds since midnight)
# the polynomial order is 1 unless you changed it during model training in Task 2
# YOUR CODE GOES HERE

# Load the trained Ridge regression model
try:
    with open('finalized_model.pkl', 'rb') as model_file:
        model = pickle.load(model_file)
    MODEL_LOADED = True
    logger.info("Model loaded successfully")
except Exception as e:
    model = None
    MODEL_LOADED = False
    MODEL_ERROR = str(e)
    logger.error(f"Failed to load model: {e}")

poly = PolynomialFeatures(degree=1)


# Initialize App
app = FastAPI(
    title="Flight Delay Prediction API",
    description="Predicts the average departure delay in minutes for LAX departures.",
    version="2.0"
)

class HealthResponse(BaseModel):
    status: str
    message: str
    version: str
    model_loaded: bool
    supported_airports: list

class PredictionResponse(BaseModel):
    arrival_airport: str
    departure_time: str
    arrival_time: str
    departure_seconds: int
    arrival_seconds: int
    predicted_departure_delay_minutes: float

def time_to_seconds(time_str: str, field_name: str) -> int:
    # This will convert HHMM string to seconds since midnight

    time_str = time_str.strip()
    if not time_str.isdigit() or len(time_str) != 4:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name} must be exactly four digits in HHMM forma. Received {time_str}. "
        )
    hour = int(time_str[:2])
    minute = int(time_str[2:])
    if hour > 23:
        raise HTTPException(
            status_code=400,
            detail=f"'{field_name}' has an invalid hour value ({hour}), must be between 0 and 23. "
        )
    if minute > 59:
        raise HTTPException(
            status_code=400,
            detail=f"'{field_name}' has an invalid minute value ({minute}), must be between 0 and 59."
        )
    return hour * 3600 + minute * 60

# TODO:  write the API endpoints.  
# YOUR CODE GOES HERE

@app.get("/", response_model=HealthResponse)
def root():

    return HealthResponse(
        status="ok",
        message="Flight Delay Prediction API is functional.",
        version="2.0",
        model_loaded=MODEL_LOADED,
        supported_airports=sorted(airports.keys())
    )

@app.get("/predict/delays", response_model=PredictionResponse)
def predict_delays(
        arrival_airport: str = Query(
            ...,
            description="Arrival airport code",
            example="SFO"
        ),
        departure_time: str = Query(
            ...,
            description="Scheduled local departure time in HHMM format.",
            example="0900"
        ),
        arrival_time: str = Query(
            ...,
            description="Scheduled local arrival time in HHMM format.",
            example="1100"
        ),

):

    # Load the model
    if not MODEL_LOADED:
        raise HTTPException(
            status_code=503,
            detail=f"Prediction model is unavailable: {MODEL_ERROR}"
        )

    # Validate airport
    airport_code = arrival_airport.upper().strip()
    airport_encoding = create_airport_encoding(airport_code, airports)

    if airport_encoding is None:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Arrival airport {airport_code} is not served from this departure airport."
                f"Supported airport: {sorted(airports.keys())}"
            )
        )


    # Convert times to seconds to midnight
    dep_seconds = time_to_seconds(departure_time, "departure_time")
    arr_seconds = time_to_seconds(arrival_time, "arrival_time")

    # Build a vector
    feature_vector = np.concatenate(
        [airport_encoding, [dep_seconds, arr_seconds]]
    ).reshape(1, -1)

    logger.info(f"Predicted delay for {airport_code}, dep={dep_seconds}, arr={arr_seconds}s")

    # Apply polynomial transform
    feature_vector_poly = poly.fit_transform(feature_vector)

    # Predict
    prediction = model.predict(feature_vector_poly)[0]

    logger.info(f"Predicted delay: {prediction:.2f} minutes")

    return PredictionResponse(
        arrival_airport=airport_code,
        departure_time=departure_time,
        arrival_time=arrival_time,
        departure_seconds=dep_seconds,
        arrival_seconds=arr_seconds,
        predicted_departure_delay_minutes=round(float(prediction), 2)
    )