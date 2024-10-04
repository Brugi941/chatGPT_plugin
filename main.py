from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
import requests
import uvicorn

{'userId': 1, 'id': 1, 'title': 'delectus aut autem', 'completed': False}
app = FastAPI()

class gatto(BaseModel):
    id: int
    name: str
    origin: str
    temperament: str
    description: str

    def fromJson(jsonRow):
        return gatto(id=jsonRow["id"], name=jsonRow["name"], origin=jsonRow["origin"], temperament=jsonRow["temperament"], description=jsonRow["description"])

class ListaGatti(BaseModel):
    gatti : List[gatto]

@app.get("/gatti", response_model=ListaGatti)
async def get_gatti():
    api_url = "https://freetestapi.com/api/v1/cats"
    response = requests.get(api_url)
    gatti = []
    for record in response.json():

        gatti.append(gatto.fromJson(jsonRow=record))
    return ListaGatti(gatti=gatti)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)