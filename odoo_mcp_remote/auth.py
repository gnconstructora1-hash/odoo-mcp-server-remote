"""Bearer token authentication middleware."""

from starlette.requests import Request
from starlette.responses import JSONResponse


class BearerAuthMiddleware:
    """ASGI middleware that validates Bearer tokens against a static API key."""

    def __init__(self, app, api_key: str):
        self.app = app
        self.api_key = api_key

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope)
            auth_header = request.headers.get("authorization", "")
            if not auth_header.startswith("Bearer "):
                response = JSONResponse(
                    {"error": "Missing or invalid Authorization header"},
                    status_code=401,
                    headers={"WWW-Authenticate": "Bearer"},
                )
                await response(scope, receive, send)
                return
            token = auth_header[7:]
            if token != self.api_key:
                response = JSONResponse(
                    {"error": "Invalid API key"},
                    status_code=403,
                )
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)
