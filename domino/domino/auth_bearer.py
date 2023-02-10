# auth_bearer.py

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from domino.config.config import settings
from jwt import decode
import time
from domino.app import _

def decodeJWT(token: str) -> dict:
    try:       
        decoded_token = decode(jwt=token, key=settings.secret, algorithms=["HS256"])
        return decoded_token if decoded_token["exp"] >= time.time() else None    
    except Exception as e: 
        return {}
       
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        locale = request.headers["accept-language"].split(",")[0].split("-")[0];
        
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail=_(locale, "bearer.schema"))
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail=_(locale, "bearer.token"))
                         
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail=_(locale, "bearer.credential"))

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False
        try:
            payload = decodeJWT(jwtoken)
        except:
            payload = None

        if payload:
            isTokenValid = True

        return isTokenValid
