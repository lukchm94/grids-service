import os
from datetime import datetime, timedelta
from typing import Annotated, Optional

from dotenv import load_dotenv
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from __app_configs import TokenTypes
from __exceptions import AuthenticationError, UserNotFoundError
from models.users import CurrentUser, User, UserWithToken

load_dotenv()
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token:
    user: User
    expire_minutes: int

    def __init__(
        self, user: User, expire_minutes: Optional[int] = ACCESS_TOKEN_EXPIRE_MINUTES
    ) -> None:
        self.user: User = user
        self.expire_minutes: int = expire_minutes

    def _get_delta(self) -> timedelta:
        return timedelta(minutes=self.expire_minutes)

    def _get_access_token(self) -> str:
        encode = {"sub": self.user.username, "role": self.user.role}
        expires = datetime.now() + self._get_delta()
        encode.update({"exp": expires})
        return jwt.encode(claims=encode, key=SECRET_KEY, algorithm=ALGORITHM)

    def generate_token(self) -> UserWithToken:
        token: str = self._get_access_token()
        user_with_token = UserWithToken(
            access_token=token, token_type=TokenTypes.bearer.value, user=self.user
        )
        return user_with_token


# Dependency to get the Logged User
async def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)]
) -> CurrentUser:
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_role: str = payload.get("role")
        if username is None:
            raise UserNotFoundError(username=username)
        return CurrentUser(username=username, role=user_role)

    except JWTError:
        raise AuthenticationError(username)


user_dependency = Annotated[dict, Depends(get_current_user)]
