# Smartcar Backend Coding Challenge

API that calls GM and other third-party APIs and returns information according to the Smartcar API spec. Written in Python using FastAPI and the Requests library.

Recommended to use Python 3.8 or above

## Installation

### Linux

After cloning the repository,
use the package manager [pip](https://pip.pypa.io/en/stable/) to install dependencies.

```bash
pip install -r requirements.txt
```

To launch the API, it is suggested to use [Uvicorn](https://www.uvicorn.org/).

```bash
uvicorn app.main:app --port 8000
```

### Docker

```
docker build -t smartcar-challenge .
docker run -dp 8000:80 --name smartcar-challenge smartcar-challenge
```

## Usage

```bash
curl http://localhost:8000/vehicles/1234
    -X GET
    -H 'Content-Type: application/json'
```

You can see a full list of routes and responses by accessing the OpenAPI page at http://localhost:8000/docs
