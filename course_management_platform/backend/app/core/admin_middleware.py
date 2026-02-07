from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.jwt_handler import decode_access_token
from app.database import SessionLocal
from app.repositories.admin_audit_repo import log_admin_action


class AdminAuditMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        # ----------------------------------------------------
        # PROCESS REQUEST
        # ----------------------------------------------------

        response = await call_next(request)

        # ----------------------------------------------------
        # EXTRACT TOKEN
        # ----------------------------------------------------

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return response

        try:
            token = auth_header.split(" ")[1]
            payload = decode_access_token(token)
        except:
            return response

        if not payload:
            return response

        # ----------------------------------------------------
        # CHECK ADMIN
        # ----------------------------------------------------

        if payload.get("role") != "Administrator":
            return response

        # ----------------------------------------------------
        # LOG ACTION
        # ----------------------------------------------------

        db = SessionLocal()

        log_admin_action(
            db=db,
            admin_user_id=payload.get("user_id"),
            admin_level=payload.get("admin_level"),
            action=str(request.url.path),
            method=request.method,
            status_code=response.status_code
        )

        db.close()

        return response