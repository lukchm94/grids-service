from __app_configs import ValidationEnum


class HttpMethods(str, ValidationEnum):
    get = "get"
    post = "post"
    delete = "delete"
