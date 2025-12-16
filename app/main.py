from fastapi import FastAPI
from app.routers.items import router as item_router  

app = FastAPI()

app.include_router(
    item_router,
    prefix="/api/v1",  
    tags=["books"]    
)

@app.get("/")
def main_root():
    return {"message": "API de la bibliothèque démarrée !"}
