from fastapi import HTTPException, Request

from __exceptions import AuthenticationError
from auth.main import user_dependency


async def check_user_dependency(request: Request, call_next):
    try:
        # Perform user_dependency check
        user = await user_dependency(request)
        print(user)
        if user is None:
            raise AuthenticationError(user)
        return await call_next(request)
    except HTTPException as exc:
        raise exc
    except Exception as err:
        raise HTTPException(status_code=500, detail="Internal server error")


# Middleware to perform user dependency check on the accounts routes only
async def middleware(request: Request, call_next):
    # Check if the request path starts with the prefix "/accounts"
    if request.url.path.startswith("/accounts"):
        # Call the user dependency check
        return await check_user_dependency(request, call_next)
    else:
        # Skip user dependency check for other endpoints
        return await call_next(request)
