"""The Lost and Found Desk's API: the app, its routers, the migrations it runs at startup, and
the error handlers that give every error one shape. Ready to use.

Run it with:  fastapi dev main.py
Then open http://127.0.0.1:8000/docs to try every route. Stop it with Ctrl+C.

Every error answer has the API's one shape, modeled on RFC 9457's problem details:

  {"status": 404, "title": "Not Found", "detail": "There's no item 99."}

  status    the status code, the same as the answer's own
  title     the status code's name: HTTPStatus(status).phrase, such as "Not Found"
  detail    a sentence about what went wrong this time
  problems  only on a 422: one {"field": ..., "message": ...} for each error FastAPI found
"""

from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from database import DATABASE_PATH, migrate, open_db
from routers import claims, items


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Runs once when the app starts: brings the database file up to date."""
    conn = open_db(DATABASE_PATH)
    migrate(conn)
    conn.close()
    yield


app = FastAPI(title="Lost and Found Desk", lifespan=lifespan)
app.include_router(items.router)
app.include_router(claims.router)


def problem(
    status: int,
    detail: str,
    problems: list[dict] | None = None,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    body: dict = {"status": status, "title": HTTPStatus(status).phrase, "detail": detail}
    if problems is not None:
        body["problems"] = problems
    return JSONResponse(status_code=status, content=body, headers=headers)


@app.exception_handler(RequestValidationError)
def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    problems = []
    for error in exc.errors():
        problems.append({"field": error["loc"][-1], "message": error["msg"]})
    return problem(422, "The request isn't valid.", problems)


@app.exception_handler(StarletteHTTPException)
def http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return problem(exc.status_code, exc.detail, headers=exc.headers)


@app.exception_handler(Exception)
def server_error(request: Request, exc: Exception) -> JSONResponse:
    return problem(500, "Something went wrong on our side.")
