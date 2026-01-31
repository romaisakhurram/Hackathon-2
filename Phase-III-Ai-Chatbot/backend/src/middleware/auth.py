from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from ..config import settings
import time
import uuid


class BetterAuthJWTMiddleware:
    """
    Middleware to handle Better Auth JWT verification per FR-001
    """
    def __init__(self):
        self.secret = settings.better_auth_secret

    async def __call__(self, request: Request, call_next):
        # Extract authorization header
        auth_header = request.headers.get("authorization")

        if auth_header:
            try:
                # Extract token from "Bearer <token>" format
                if auth_header.startswith("Bearer "):
                    token = auth_header[7:]
                else:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Invalid authorization header format"}
                    )

                # Verify JWT token using Better Auth standards
                payload = jwt.decode(
                    token,
                    self.secret,
                    algorithms=["HS256"]
                )

                # Validate user_id exists in payload per Better Auth JWT format
                user_id = payload.get("user_id")
                if not user_id:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Invalid token: missing user_id (Better Auth integration)"}
                    )

                # Validate token expiration (NFR-003: 24-hour expiry)
                exp = payload.get("exp")
                if exp and time.time() > exp:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Better Auth token has expired"}
                    )

                # Additional Better Auth JWT validation (T052)
                # Check for required claims in Better Auth JWT format
                required_claims = ["user_id", "exp", "iat"]
                missing_claims = [claim for claim in required_claims if claim not in payload]

                if missing_claims:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": f"Better Auth token missing required claims: {missing_claims}"}
                    )

                # Validate issuer if present (Better Auth standard)
                issuer = payload.get("iss")
                if issuer and not issuer.endswith("better-auth"):
                    # Log warning but don't fail for flexibility
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Token issuer '{issuer}' may not be from Better Auth")

                # Add user info to request state
                request.state.user_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
                request.state.user_payload = payload

            except JWTError as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Better Auth JWT validation failed: {str(e)}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Could not validate Better Auth credentials"}
                )
            except ValueError as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Better Auth user ID validation failed: {str(e)}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid user ID format in Better Auth token"}
                )

        response = await call_next(request)
        return response