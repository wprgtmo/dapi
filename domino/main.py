# main.py
from domino.config.config import settings
import os
import uvicorn

if __name__ == "__main__":
    if settings.env=='production':
        settings.server_port = os.getenv('PORT')
        settings.server_uri = '0.0.0.0'
        
    uvicorn.run("domino.app:app", host=settings.server_uri, port=int(settings.server_port), reload=True)