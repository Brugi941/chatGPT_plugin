from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
import requests
import uvicorn
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

{'userId': 1, 'id': 1, 'title': 'delectus aut autem', 'completed': False}
app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/gatti", response_model=List[gatto])
async def get_gatti():
    api_url = "https://freetestapi.com/api/v1/cats"
    response = requests.get(api_url)
    gatti = []
    for record in response.json():
        gatti.append(gatto.fromJson(jsonRow=record))
    gatti.append(gatto(id=123,name="Anna", origin="Mestre", temperament="arrabbiotto", description="Il gatto più arrabbiotto"))
    return gatti
    #return ListaGatti(gatti=gatti)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Cats API",
        version="1.0.0",
        summary="Access cats data",
        description="Access cats data, especially temperament",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)