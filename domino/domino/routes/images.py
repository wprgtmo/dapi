from fastapi import APIRouter, Depends, Request, HTTPException
from domino.schemas.events import EventBase
from domino.schemas.tourney import TourneyCreated
from domino.schemas.result_object import ResultObject
from sqlalchemy.orm import Session
from domino.app import get_db
from typing import BinaryIO
from domino.services.event import get_all, new, get_one_by_id, delete, update, get_image_event
from starlette import status
from domino.auth_bearer import JWTBearer
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from os import getcwd, remove
  
image_route = APIRouter(
    tags=["Images"]   
)

@image_route.get("/image/{user_id}/{event_id}/{file_name}", summary="Mostrar imagen de un evento")
def getEventImage(user_id: str, event_id: str, file_name: str):
    return FileResponse(getcwd() + "/public/events/" + user_id + "/" + event_id + "/" + file_name)

@image_route.delete("/image/event/{event_id}", summary="Eliminar imagen de un evento")
def delevent(name: str):
    try:
        remove(getcwd() + "/public/events/" + name)
        return JSONResponse(content={"success": True, "message": "file deleted"}, status_code=200)
    except FileNotFoundError:
        return JSONResponse(content={"success": False}, status_code=404)
    
@image_route.get("/post/{post_id}/{file_name}", response_class=FileResponse, summary="Mostrar imagen de un post")
def getPostFile(post_id: str, file_name: str):
    return FileResponse(getcwd() + "/public/post/" + post_id + "/" + file_name)

@image_route.get("/video/post/{post_id}/{video_name}", summary="Mostrar un video de un Post")
def get_video(request: Request, post_id: str, video_name: str):
    file_name = getcwd() + "/public/post/" + post_id + "/" + video_name
    return range_requests_response(
        request, file_path=file_name, content_type="video/mp4"
    )
       
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
