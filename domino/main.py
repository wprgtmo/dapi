# main.py
from domino.config.config import settings

import uvicorn

if __name__ == "__main__":
    uvicorn.run("domino.app:app", host=settings.server_uri, port=int(settings.server_port), reload=True)