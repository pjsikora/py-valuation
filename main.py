from typing import Union
from fastapi import FastAPI, Query, HTTPException
from internal.open_ai import valuate_item
from config import settings
from urllib.parse import urlparse

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])  # scheme = http/https, netloc = domain
    except ValueError:
        return False

app = FastAPI()

@app.get("/info")
async def info():
    return {
        "app_name": settings.app_name
    }

@app.get("/gpt")
def get_gpt_data(image_url: str = Query(..., description="Image URL")):
    if is_valid_url(image_url):
         return {
            "response": valuate_item(image_url)
        }
    else: 
       raise HTTPException(status_code=400, detail="No proper URL given")