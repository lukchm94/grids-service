import os
from datetime import datetime, timedelta
from typing import Annotated, Optional

from dotenv import load_dotenv
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from __app_configs import TokenConfigs, TokenTypes
from __exceptions import AuthenticationError, ExpiredTokenError, UserNotFoundError
from models.users import CurrentUser, User, UserWithToken

load_dotenv()
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY")


class Token:
    user: User
    expire_minutes: int

    def __init__(
        self,
        user: User,
        expire_minutes: Optional[int] = TokenConfigs.default_expiration.value,
    ) -> None:
        self.user: User = user
        self.expire_minutes: int = expire_minutes

    def _get_delta(self) -> timedelta:
        return timedelta(minutes=self.expire_minutes)

    def _get_access_token(self) -> str:
        encode = {
            "sub": self.user.username,
            "role": self.user.role,
            "permissions": self.user.permissions,
        }
        expires = datetime.now() + self._get_delta()
        encode.update({"exp": expires})
        return jwt.encode(
            claims=encode, key=SECRET_KEY, algorithm=TokenConfigs.algorithm.value
        )

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
        payload = jwt.decode(
            token=token, key=SECRET_KEY, algorithms=[TokenConfigs.algorithm.value]
        )
        username: str = payload.get("sub")
        user_role: str = payload.get("role")
        permissions: str = payload.get("permissions")
        if username is None:
            raise UserNotFoundError(username=username)
        return CurrentUser(username=username, role=user_role, permissions=permissions)

    except ExpiredSignatureError:
        raise ExpiredTokenError()

    except JWTError:
        raise AuthenticationError(username)


user_dependency = Annotated[CurrentUser, Depends(get_current_user)]
