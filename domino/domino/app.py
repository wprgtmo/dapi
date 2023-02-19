# app.py

from fastapi import FastAPI, Request
from pyi18n import PyI18n
from domino.config.config import settings
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from logging.config import dictConfig
from domino.config.db import SessionLocal
from fastapi.openapi.docs import (get_redoc_html, get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html)
from fastapi.staticfiles import StaticFiles
from typing import Callable


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

# @app.get("/hello/{name}")
# def hello_name(request: Request, name: str):
#     print(request.headers["accept-language"].split(",")[0].split("-")[0]);
#     locale = "en" #request.headers["accept-language"].split(",")[0].split("-")[0];
#     # locale: str = get_user_locale(name)
#     return {"greeting": _(locale, "greetings.hello_name", name=name)}

