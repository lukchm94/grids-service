from logging import Logger

from __app_configs import Deliminator, LogMsg, Permissions, return_elements
from __exceptions import AuthenticationError, InvalidPermissionError, UserNotFoundError
from auth.main import encode_passwords, user_dependency
from database.main import db_dependency
from database.models import UsersTable
from models.users import User, UserReq, UserVerification


class Getter:
    logger: Logger
    db: db_dependency

    def __init__(self, logger: Logger, db: db_dependency) -> None:
        self.logger: Logger = logger
        self.db: db_dependency = db

    def user_by_username(self, username: str) -> dict:
        users: list[UsersTable] = (
            self.db.query(UsersTable).filter(UsersTable.username == username).all()
        )
        if len(users) == 0:
            raise UserNotFoundError(username)
        return return_elements([user.to_user() for user in users])

    def user(self, username: str, password: str) -> User:
        user = (
            self.db.query(UsersTable)
            .filter(UsersTable.username == username)
            .filter(UsersTable.deleted_at.is_(None))
            .first()
        )
        if user is None:
            raise UserNotFoundError(username)
        if user.hashed_password != encode_passwords(password):
            raise AuthenticationError(username)
        return user.to_user()


class Setter:
    logger: Logger
    db: db_dependency
    user_req: UserReq

    def __init__(self, logger: Logger, db: db_dependency, user_req: UserReq) -> None:
        self.logger: Logger = logger
        self.db: db_dependency = db
        self.user_req: UserReq = user_req

    def _permissions_to_str(self) -> str:
        return Deliminator.comma.value.join(
            permission for permission in self.user_req.permissions
        )

    def create_user(self) -> None:
        create_user_model: UsersTable = UsersTable(
            email=self.user_req.email,
            username=self.user_req.username,
            first_name=self.user_req.first_name,
            last_name=self.user_req.last_name,
            role=self.user_req.role,
            hashed_password=encode_passwords(self.user_req.password),
            permissions=self._permissions_to_str(),
            deleted_at=None,
        )
        self.db.add(create_user_model)
        self.db.commit()


class Update:
    logger: Logger
    db: db_dependency
    user: user_dependency

    def __init__(
        self, logger: Logger, db: db_dependency, user: user_dependency
    ) -> None:
        self.logger: Logger = logger
        self.db: db_dependency = db
        self.user: user_dependency = user

    def _get_user(self, username: str) -> UsersTable:
        user = (
            self.db.query(UsersTable)
            .filter(UsersTable.username == username)
            .filter(UsersTable.deleted_at.is_(None))
            .first()
        )
        if user is None:
            raise UserNotFoundError(self.user.username)
        return user

    def _to_str(self, permissions: list[str]) -> str:
        return Deliminator.comma.value.join(
            perm.replace(Deliminator.space.value, Deliminator.none.value)
            for perm in permissions
        )

    def _validate_permissions(self, permissions: list[str]) -> str:
        for perm in permissions:
            if perm not in Permissions.list():
                raise InvalidPermissionError(perm)
        return self._to_str(permissions)

    def change_password(self, user_ver: UserVerification) -> None:
        user: UsersTable = self._get_user(self.user.username)
        if user.hashed_password != encode_passwords(user_ver.password):
            raise AuthenticationError(user.username)
        user.hashed_password = encode_passwords(user_ver.new_password)
        self.db.add(user)
        self.db.commit()
        self.logger.info(LogMsg.changed_pass.value.format(username=self.user.username))

    def change_permissions(self, permissions: list[str], username: str) -> None:
        user: UsersTable = self._get_user(username)
        p = self._validate_permissions(permissions)
        print(self._to_str(permissions))
        print(p)
        print(permissions)
        user.permissions = self._validate_permissions(permissions)
        self.db.add(user)
        self.db.commit()
        self.logger.info(
            LogMsg.changed_perm.value.format(
                username=self.user.username, perm=permissions
            )
        )
