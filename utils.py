import requests

def submit_transaction(data):
    """
    transaction submission
    API endpoint needed where localhost is
    """
    try:
        response = requests.post("http://localhost:5000/api/transactions", json=data)
        if response.status_code == 201:
            return True
        else:
            print("Error:", response.text)
            return False
    except Exception as e:
        print("Exception:", e)
        return False

def fetch_properties():
    """
    record fetching
    API endpoint needed where localhost is
    """
    try:
        response = requests.get("http://localhost:5000/api/properties")
        if response.status_code == 200:
            return response.json()
        else:
            print("Error:", response.text)
            return []
    except Exception as e:
        print("Exception:", e)
        return []