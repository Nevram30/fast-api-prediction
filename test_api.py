import requests
import json

url = "http://localhost:8000/api/v1/predict"
payload = {
    "city": "Panabo",
    "dateFrom": "2024-01-01",
    "dateTo": "2024-01-31",
    "province": "Pampanga",
    "species": "tilapia"
}

response = requests.post(url, json=payload)
print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
