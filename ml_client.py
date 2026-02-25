import requests

ML_SERVICE_URL = "https://appify-ml.onrender.com/score"


def call_ml_service(resume_json):

    try:
        response = requests.post(
            ML_SERVICE_URL,
            json=resume_json,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.Timeout:
        return {"error": "ML service timed out. It may be sleeping (Render free tier)."}

    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to ML service."}

    except Exception as e:
        return {"error": str(e)}