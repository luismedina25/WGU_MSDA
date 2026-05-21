#!/usr/bin/env python
# coding: utf-8

# import statements
from fastapi import FastAPI, HTTPException
import json
import numpy as np
import pickle
import datetime
from sklearn.preprocessing import PolynomialFeatures

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
# Load the model
with open('finalized_model.pkl', 'rb') as model_file    :
    model = pickle.load(model_file)

poly = PolynomialFeatures(degree=1)

# Initialize App
app = FastAPI(
    title='Flight Delay Prediction API',
    description='Predicts average departure delay for LAX flights.',
    version='1.0',
)

def time_to_seconds(time_str: str) -> int:
    # Convert a time string in HHMM format to seconds since midnight

    if not time_str.isdigit() or len(time_str) != 4:
        raise HTTPException(
            status_code=400,
            detail='Time must be a 4 digit string in HH:MM format.'
        )
    hour = int(time_str[:2])
    minute = int(time_str[2:])
    if hour > 23 or minute > 59:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid time '{time_str}'. Time must be in HH:MM format."
        )
    return hour * 3600 + minute * 60

# TODO:  write the API endpoints.  
# YOUR CODE GOES HERE
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Flight Delay Prediction API is working",
        "version": "1.0",
    }

@app.get("/predict/delays")
def predict_delays(
        arrival_airport: str,
        departure_time: str,
        arrival_time: str,
):

    # Validate arrival airport
    airport_code = arrival_airport.upper().strip()
    airport_encoding = create_airport_encoding(airport_code, airports)

    if airport_encoding is None:
        raise HTTPException(
            status_code=400,
            detail=f"Arrival airport code '{arrival_airport}' is invalid."
        )


    # Conver times to seconds since midnight
    dep_seconds = time_to_seconds(departure_time)
    arr_seconds = time_to_seconds(arrival_time)

    # Build a vector
    feature_vector = np.concatenate(
        [airport_encoding, [dep_seconds, arr_seconds]]
    ).reshape(1, -1)

    # Apply polynomial transform to match training
    feature_vector_poly = poly.fit_transform(feature_vector)

    # Make prediction
    prediction = model.predict(feature_vector_poly)[0]

    return {
        "arrival_airport": arrival_airport,
        "departure_time": departure_time,
        "arrival_time": arrival_time,
        "predicted_delay_minutes": round(float(prediction), 2)
    }