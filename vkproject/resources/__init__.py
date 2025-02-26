import abc
import os.path
from abc import abstractmethod
from typing import Any, Type


class ResourceLoader(abc.ABC):
    @abstractmethod
    def load_resource(self, resource_path, resource_id):
        pass

    @abstractmethod
    def accepts_resource(self, resource_path, resource_id) -> bool:
        pass

class Resources:
    _loaders: list[ResourceLoader] = []

    @staticmethod
    def register_loader(loader):
        Resources._loaders.append(loader)

    @staticmethod
    def get_loader[T](loader_type: Type[T]) -> T | None:
        for loader in Resources._loaders:
            if isinstance(loader, loader_type):
                return loader

        return None

    @staticmethod
    def load():
        Resources._load_dir("res")

    @staticmethod
    def _load_file(directory: str, file: str):
        path = f"{directory}/{file}"
        resource_id = os.path.splitext((directory + "/" + file).removeprefix("res/"))[0]
        for loader in Resources._loaders:
            if loader.accepts_resource(path, resource_id):
                loader.load_resource(path, resource_id)


    @staticmethod
    def _load_dir(directory: str):
        tree = os.walk(directory)
        is_root = True
        for root, dirs, files in tree:
            if is_root:
                is_root = False
                continue

            for file in files:
                Resources._load_file(root, file)
            for sub_dir in dirs:
                Resources._load_dir(directory + "/" + sub_dir)
