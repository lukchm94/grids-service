from enum import Enum


class Paths(str, Enum):
    root = "/"
    grids = f"{root}grids"
    configs = f"{root}configs"
