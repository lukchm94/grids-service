import base64
from logging import Logger

from __app_configs import return_elements
from database.main import db_dependency
from database.models import UsersTable
from models.users import UserReq


class Getter:
    logger: Logger
    db: db_dependency

    def __init__(self, logger: Logger, db: db_dependency) -> None:
        self.logger: Logger = logger
        self.db: db_dependency = db

    def get_all_users(self) -> dict:
        users: list[UsersTable] = self.db.query(UsersTable).all()
        print(users)
        if len(users) == 0:
            raise
        return return_elements([user.to_user() for user in users])


class Setter:
    logger: Logger
    db: db_dependency
    user_req: UserReq

    def __init__(self, logger: Logger, db: db_dependency, user_req: UserReq) -> None:
        self.logger: Logger = logger
        self.db: db_dependency = db
        self.user_req: UserReq = user_req

    def create_user(self) -> None:
        create_user_model: UsersTable = UsersTable(
            email=self.user_req.email,
            username=self.user_req.username,
            first_name=self.user_req.first_name,
            last_name=self.user_req.last_name,
            role=self.user_req.role,
            hashed_password=base64.b64encode(self.user_req.password.encode()).decode(),
            # hashed_password=self.user_req.password,
            deleted_at=None,
        )
        print(create_user_model.to_user())
        print(type(create_user_model))
        print(type(create_user_model.hashed_password))
        self.db.add(create_user_model)
        self.db.commit()
