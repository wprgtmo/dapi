# app.py

from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Header, Response, status
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from os import getcwd, remove, path, stat

from pyi18n import PyI18n
from domino.config.config import settings
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from logging.config import dictConfig
from domino.config.db import SessionLocal
from fastapi.openapi.docs import (get_redoc_html, get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html)
from fastapi.staticfiles import StaticFiles
from typing import BinaryIO, Callable
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

from domino.routes.auth import auth_routes
from domino.routes.user import user_route
from domino.routes.country import country_route
from domino.routes.city import city_route
from domino.routes.package import packages_route
from domino.routes.status import status_route
from domino.routes.post import post_route
from domino.routes.comment import comment_route
from domino.routes.event import event_route
from domino.routes.tourney import tourney_route

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
app.include_router(packages_route, prefix="/api")
app.include_router(status_route, prefix="/api")
app.include_router(post_route, prefix="/api")
app.include_router(comment_route, prefix="/api")
app.include_router(event_route, prefix="/api")
app.include_router(tourney_route, prefix="/api")

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

@app.get("/{user_id}/{event_id}/{file_name}", summary="Mostrar imagen de un evento")
def getEventImage(user_id: str, event_id: str, file_name: str):
    return FileResponse(getcwd() + "/public/events/" + user_id + "/" + event_id + "/" + file_name)

@app.get("/{post_id}/{file_name}", response_class=FileResponse, summary="Mostrar imagen de un post")
def getPostFile(post_id: str, file_name: str):
    return FileResponse(getcwd() + "/public/post/" + post_id + "/" + file_name)

# @app.get("/{video_name}")
# def get_video(video_name: str):
#     file_name = getcwd()+"/public/post/316b0eeb-237a-4903-94d7-5686772468d5/"+video_name
#     with open(file_name, "rb") as myfile:
#         data = myfile.read(path.getsize(file_name))
#         return Response(content=data, status_code=206, media_type="video/mp4")


@app.delete("/delete/{name}")
def delevent(name: str):
    try:
        remove(getcwd() + "/public/events/" + name)
        return JSONResponse(content={"success": True, "message": "file deleted"}, status_code=200)
    except FileNotFoundError:
        return JSONResponse(content={"success": False}, status_code=404)

@app.get("/{user_id}/{name}")
def getprofile(user_id: str, file_name: str):
    return FileResponse(getcwd() + "/public/profile/" + user_id + "/" + file_name)

def send_bytes_range_requests(
    file_obj: BinaryIO, start: int, end: int, chunk_size: int = 10_000
):
    """Send a file in chunks using Range Requests specification RFC7233

    `start` and `end` parameters are inclusive due to specification
    """
    with file_obj as f:
        f.seek(start)
        while (pos := f.tell()) <= end:
            read_size = min(chunk_size, end + 1 - pos)
            yield f.read(read_size)
            
def _get_range_header(range_header: str, file_size: int) -> tuple[int, int]:
    def _invalid_range():
        return HTTPException(
            status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
            detail=f"Invalid request range (Range:{range_header!r})",
        )

    try:
        h = range_header.replace("bytes=", "").split("-")
        start = int(h[0]) if h[0] != "" else 0
        end = int(h[1]) if h[1] != "" else file_size - 1
    except ValueError:
        raise _invalid_range()

    if start > end or start < 0 or end > file_size - 1:
        raise _invalid_range()
    return start, end

def range_requests_response(
    request: Request, file_path: str, content_type: str
):
    """Returns StreamingResponse using Range Requests of a given file"""

    file_size = stat(file_path).st_size
    range_header = request.headers.get("range")

    headers = {
        "content-type": content_type,
        "accept-ranges": "bytes",
        "content-encoding": "identity",
        "content-length": str(file_size),
        "access-control-expose-headers": (
            "content-type, accept-ranges, content-length, "
            "content-range, content-encoding"
        ),
    }
    start = 0
    end = file_size - 1
    status_code = status.HTTP_200_OK

    if range_header is not None:
        start, end = _get_range_header(range_header, file_size)
        size = end - start + 1
        headers["content-length"] = str(size)
        headers["content-range"] = f"bytes {start}-{end}/{file_size}"
        status_code = status.HTTP_206_PARTIAL_CONTENT

    return StreamingResponse(
        send_bytes_range_requests(open(file_path, mode="rb"), start, end),
        headers=headers,
        status_code=status_code,
    )

@app.get("/{post_id}/{video_name}")
def get_video(request: Request, post_id: str, video_name: str):
    file_name = getcwd() + "/public/post/" + post_id + "/" + video_name
    return range_requests_response(
        request, file_path=file_name, content_type="video/mp4"
    )