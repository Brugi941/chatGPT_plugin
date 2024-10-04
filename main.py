from fastapi import FastAPI
import requests

{'userId': 1, 'id': 1, 'title': 'delectus aut autem', 'completed': False}
app = FastAPI()


@app.get("/gatti")
async def get_gatti():
    api_url = "https://freetestapi.com/api/v1/cats"
    response = requests.get(api_url)
    return response.json()