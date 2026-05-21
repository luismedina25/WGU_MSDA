# Create the Unit test for version 1

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
    poly.fit_transform.return_value = np.zeros((1, 90))
    return poly


@pytest.fixture
def client(mock_airports, mock_model, mock_poly):
    # Testclient with mocked model and airports
    import API_Python_v1
    import importlib

    with patch("API_Python_v1.open", create=True), \
            patch("API_Python_v1.json.load", return_value=mock_airports), \
            patch("API_Python_v1.pickle.load", return_value=mock_model):

         importlib.reload(API_Python_v1)

         API_Python_v1.airports = mock_airports
         API_Python_v1.model = mock_model
         API_Python_v1.poly = mock_poly

         yield TestClient(API_Python_v1.app)

# Test Get

def test_root_returns_200(client):
    # Get should return HTTP 200.
    response = client.get("/")
    assert response.status_code == 200

def test_root_returns_ok_status(client):
    # Get should return status ok
    response = client.get("/")
    assert response.json()["status"] == "ok"


def test_root_returns_message(client):
    # Get should return a non-empty message
    response = client.get("/")
    assert "message" in response.json()

# Test Get predicted/delays

def test_predict_valid_request_returns_200(client):
    # A valid request should return HTTP 200
    response = client.get(
        "/predict/delays",
        params={
            "arrival_airport": "SFO",
            "departure_time":  "0830",
            "arrival_time":    "1015",
        }
    )
    assert response.status_code == 200


def test_predict_valid_request_returns_delay(client):
    # Should return the predicted delay value
    response = client.get(
        "/predict/delays",
        params={
            "arrival_airport": "SFO",
            "departure_time":  "0830",
            "arrival_time":    "1015",
        }
    )
    data = response.json()
    assert "predicted_delay_minutes" in data
    assert isinstance(data["predicted_delay_minutes"], float)


def test_predict_echoes_airport(client):
    # Get should echo back the airport code in uppercase
    response = client.get(
        "/predict/delays",
        params={
            "arrival_airport": "jfk",
            "departure_time": "1400",
            "arrival_time": "1730",
        }
    )
    assert response.json()["arrival_airport"].upper() == "JFK"


# Now to test invalid request tests

def test_predict_invalid_airport_returns_400(client):
    response = client.get(
        "/predict/delays",
        params={
            "arrival_airport": "ZZZ",
            "departure_time": "0830",
            "arrival_time": "1015",
        }
    )
    assert response.status_code == 400


def test_predict_invalid_time_format_returns_400(client):
    # Get predict delays with non-HHMM time and should return HTTP 400
    response = client.get(
        "/predict/delays",
        params={
            "arrival_airport": "SFO",
            "departure_time": "830",
            "arrival_time": "1015",
        }
    )
    assert response.status_code == 400

def test_predict_invalid_hour_return_400(client):
    # Get predict/delay with hour > 23 and should return HTTP 400
    response = client.get(
        "/predict/delays",
        params={
            "arrival_airport": "SFO",
            "departure_time": "2500",
            "arrival_time": "1015",
        }
    )
    assert response.status_code == 400

def test_predict_missing_params_returns_422(client):
    # Get predict/delay with no params should return HTTP 422
    response = client.get("/predict/delays")
    assert response.status_code == 422
