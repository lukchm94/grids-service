from __exceptions import AuthenticationError, PermEndpointError
from auth.main import user_dependency
from auth.permissions import Access
from database.main import db_dependency


def authorize(
    user: user_dependency, db: db_dependency, method: str, endpoint: str
) -> bool:
    if user is None:
        raise AuthenticationError(user)
    if not Access(
        db=db,
        user_perm=user.permissions,
        endpoint=endpoint,
        method=method,
    ).check():
        raise PermEndpointError(perm=user.permissions, endpoint=endpoint)
