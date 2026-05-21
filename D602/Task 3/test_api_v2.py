# Create the Unit test for version 2

import pytest
import numpy as np
from unittest.mock import patch, MagicMock, mock_open
from fastapi.testclient import TestClient
import json


#Fixtures

@pytest.fixture
def mock_airports():
    # Real airport codes matching the json file
    return {
        "ABQ": 0, "ATL": 1, "BOS": 2, "DEN": 3,
        "DFW": 4, "JFK": 5, "LAS": 6, "MIA": 7,
        "SFO": 8, "SLC": 9
    }


@pytest.fixture
def mock_model():
    # Ridge regression model that will return a fixed prediction
    model = MagicMock()
    model.predict.return_value = np.array([7.5])
    return model


@pytest.fixture
def mock_poly():

    poly = MagicMock()
    poly.transform.return_value = np.zeros((1, 90))
    return poly


@pytest.fixture
def client(mock_airports, mock_model, mock_poly):
    # Testclient with mocked model and airports
    import API_Python_v2
    import importlib

    with patch("API_Python_v2.open", create=True), \
            patch("API_Python_v2.json.load", return_value=mock_airports), \
            patch("API_Python_v2.pickle.load", return_value=mock_model):

        importlib.reload(API_Python_v2)

        API_Python_v2.airports = mock_airports
        API_Python_v2.model = mock_model
        API_Python_v2.poly = mock_poly
        API_Python_v2.MODEL_LOADED = True

        yield TestClient(API_Python_v2.app)

# Test Get and health check

def test_root_returns_200(client):
    # Get should return HTTP 200.
    response = client.get("/")
    assert response.status_code == 200

def test_root_returns_ok_status(client):
    # Get should return status ok
    response = client.get("/")
    assert response.json()["status"] == "ok"


def test_root_returns_message(client):
    # Get should return a message confirming the API is functional
    response = client.get("/")
    assert "functional" in response.json()["message"].lower()

def test_root_returns_model_loaded(client):
    # Get should indicate the model is loaded
    response = client.get("/")
    assert response.json()["model_loaded"] is True


def test_root_returns_supported_airports(client):
    # Get should return a list of supported airports
    response = client.get("/")
    data = response.json()
    assert "supported_airports" in data
    assert isinstance(data["supported_airports"], list)
    assert len(data["supported_airports"]) > 0


# Validate Prediction Test

def test_predict_valid_request_returns_200(client):
    # Get it will validate params and should return HTTP 200
    response = client.get(
        "/predict/delays",
        params={
            "arrival_airport": "SFO",
            "departure_time": "0830",
            "arrival_time": "1015"
        }
    )
    assert response.status_code == 200

def test_predict_valid_request_returns_delay(client):
    # Get should return the predicted delay value
    response = client.get(
        "/predict/delays",
        params={
            "arrival_airport": "SFO",
            "departure_time": "0830",
            "arrival_time": "1015"
        }
    )
    data = response.json()
    assert "predicted_departure_delay_minutes" in data
    assert isinstance(data["predicted_departure_delay_minutes"], float)

def test_predict_echoes_airport(client):
    # Get should echo back the airport code in uppercase
    response = client.get(
        "/predict/delays",
        params={
            "arrival_airport": "SFO",
            "departure_time": "1400",
            "arrival_time": "1730"
        }
    )
    data = response.json()
    assert "arrival_airport" in data

def test_predict_returns_seconds(client):
    # Get should return departure and arrival in seconds
    response = client.get(
        "/predict/delays",
        params={
            "arrival_airport": "SFO",
            "departure_time": "0100",
            "arrival_time": "0200"
        }
    )
    data = response.json()
    assert data["departure_seconds"] == 3600
    assert data["arrival_seconds"] == 7200

def test_predict_midnight_departure(client):
    # Get should handle midnight (0000) correctly
    response = client.get(
        "/predict/delays",
        params={
            "arrival_airport": "DEN",
            "departure_time": "0000",
            "arrival_time": "0300"
        }
    )
    assert response.status_code == 200
    assert response.json()["departure_seconds"] == 0

# Invalid test

def test_predict_invalid_airport_returns_400(client):
    # Get predict with n airport should return HTTP 400
    response = client.get(
        "/predict/delays",
        params={
            "arrival_airport": "ZZZ",
            "departure_time": "0830",
            "arrival_time": "1015"
        }
    )
    assert response.status_code == 400

def test_predict_invalid_time_format_400(client):
    # Get with wrong format not in HHMM should return HTTP 400
    response = client.get(
        "/predict/delays",
        params={
            "arrival_airport": "SFO",
            "departure_time": "830",
            "arrival_time": "1015"
        }
    )
    assert response.status_code == 400

def test_predict_invalid_hour_returns_400(client):
    # Get with hour > 23 should return HTTP 400
    response = client.get(
        "/predict/delays",
        params={
            "arrival_airport": "SFO",
            "departure_time": "2500",
            "arrival_time": "1015"
        }
    )
    assert response.status_code == 400

def test_predict_invalid_minute_returns_400(client):
    # Get with minutes > 59 should return HTTP 400
    response = client.get(
        "/predict/delays",
        params={
            "arrival_airport": "SFO",
            "departure_time": "0860",
            "arrival_time": "1015"
        }
    )
    assert response.status_code == 400

def test_predict_letters_in_time_returns_400(client):
    # Get with letters in time should return HTTP 400
    response = client.get(
        "/predict/delays",
        params={
            "arrival_airport": "SFO",
            "departure_time": "08ab",
            "arrival_time": "1015"
        }
    )
    assert response.status_code == 400

def test_predict_missing_params_returns_422(client):
    # Get with no params should return HTTP 422
    response = client.get("/predict/delays")
    assert response.status_code == 422


# Create helper functions

def test_create_airport_encoding_valid(mock_airports):
    # will create airport encoding and should return a one-hot array for a valid airport.
    from API_Python_v2 import create_airport_encoding
    result = create_airport_encoding("SFO", mock_airports)
    assert result is not None
    assert result[8] == 1.0
    assert np.sum(result) == 1.0

def test_create_airport_encoding_invalid(mock_airports):
    # will create airport encoding and should return None for an unknown airport
    from API_Python_v2 import create_airport_encoding
    result = create_airport_encoding("ZZZ", mock_airports)
    assert result is None

def test_create_airport_encoding_length(mock_airports):
    # will create airport encoding and should return an array the length of the airports dict
    from API_Python_v2 import create_airport_encoding
    result = create_airport_encoding("ATL", mock_airports)
    assert len(result) == len(mock_airports)












