# app.py

from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Header, Response, status, Depends
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from os import getcwd, remove, path, stat
import aiofiles

from pyi18n import PyI18n
from domino.config.config import settings
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from logging.config import dictConfig
from domino.config.db import SessionLocal
from fastapi.openapi.docs import (get_redoc_html, get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html)
from fastapi.staticfiles import StaticFiles
from typing import BinaryIO, Callable, List, Optional
import shutil

dictConfig(settings.log_config)

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    docs_url=None, redoc_url=None
)

i18n: PyI18n = PyI18n(('en', 'es'), load_path="/domino/domino/locales/")

_: Callable = i18n.gettext

app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.add_middleware(SessionMiddleware, secret_key=settings.secret)

from domino.routes.enterprise.auth import auth_routes
from domino.routes.enterprise.user import user_route
from domino.routes.resources.country import country_route
from domino.routes.resources.city import city_route
from domino.routes.resources.package import packages_route
from domino.routes.resources.status import status_route
from domino.routes.post.post import post_route
from domino.routes.post.comment import comment_route
from domino.routes.events.event import event_route
from domino.routes.events.tourney import tourney_route
from domino.routes.resources.images import image_route
from domino.routes.enterprise.profiletype import profiletype_route
from domino.routes.events.invitations import invitation_route
from domino.routes.events.player import player_route
from domino.routes.events.referee import referee_route
from domino.routes.enterprise.singleprofile import singleprofile_route
from domino.routes.enterprise.defaultprofile import defaultprofile_route
from domino.routes.enterprise.pairprofile import pairprofile_route
from domino.routes.enterprise.teamprofile import teamprofile_route
from domino.routes.enterprise.referee_profile import refereeprofile_route
from domino.routes.enterprise.request import request_route
from domino.routes.enterprise.followers import follower_route
from domino.routes.enterprise.eventadmon_profile import eventadmonprofile_route
from domino.routes.resources.ext_type import type_ext_route
from domino.routes.resources.exampledata import exampledata_route

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )

app.include_router(auth_routes, prefix="/api")
app.include_router(user_route, prefix="/api")
app.include_router(country_route, prefix="/api")
app.include_router(city_route, prefix="/api")
# app.include_router(packages_route, prefix="/api")
app.include_router(status_route, prefix="/api")
app.include_router(profiletype_route, prefix="/api")
app.include_router(post_route, prefix="/api")
app.include_router(comment_route, prefix="/api")
app.include_router(event_route, prefix="/api")
app.include_router(tourney_route, prefix="/api")
app.include_router(image_route, prefix="/api")
app.include_router(invitation_route, prefix="/api")
app.include_router(player_route, prefix="/api")
app.include_router(referee_route, prefix="/api")
app.include_router(singleprofile_route, prefix="/api")
app.include_router(defaultprofile_route, prefix="/api")
app.include_router(pairprofile_route, prefix="/api")
app.include_router(teamprofile_route, prefix="/api")
app.include_router(refereeprofile_route, prefix="/api")
app.include_router(request_route, prefix="/api")
app.include_router(eventadmonprofile_route, prefix="/api")
app.include_router(follower_route, prefix="/api")
app.include_router(type_ext_route, prefix="/api")
app.include_router(exampledata_route, prefix="/api")


@app.post("/file")
def upfile(file: UploadFile = File(...)):
    # print(request.headers["accept-language"].split(",")[0].split("-")[0]);
    # locale = "en" #request.headers["accept-language"].split(",")[0].split("-")[0];
    # # locale: str = get_user_locale(name)
    # return {"greeting": _(locale, "greetings.hello_name", name=name)}
    import os

    path = "public/events"
    if not os.path.isdir(path):
        print("crear............")
        os.mkdir(path)
                
    path = path + "/" + file.filename
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"file_name": file.filename}

from pydantic import BaseModel

class Properties(BaseModel):
    language: str = None
    author: str = None    

@app.post("/upload-files")
async def create_upload_files(post_id: str, properties: Properties, files: List[UploadFile] = File(...)):

    from fastapi.encoders import jsonable_encoder
    json_compatible_item_data = jsonable_encoder(properties)
    return(json_compatible_item_data)
   
    
    # for file in files:
    #     # destination_file_path = getcwd() + "/public/post/" + post_id + "/" + video_name
    #     destination_file_path = getcwd() + "/public/post/" + post_id + "/" +file.filename

    #     async with aiofiles.open(destination_file_path, 'wb') as out_file:
    #         while content := await file.read(1024):  # async read file chunk
    #             await out_file.write(content)  # async write file chunk
    # return {"Result": "OK", "filenames": [file.filename for file in files]}

class Base(BaseModel):
    name: str
    point: Optional[float] = None
    is_accepted: Optional[bool] = False
    tourney: List[Properties]

@app.post("/submit")
def submit(base: Base = Depends(), files: List[UploadFile] = File(...)):
    received_data= base.dict()
    return {"JSON Payload ": received_data, "Uploaded Filenames": [file.filename for file in files]}