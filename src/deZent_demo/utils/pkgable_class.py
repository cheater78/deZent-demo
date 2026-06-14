from abc import ABC, abstractmethod
from typing import Any, Type, TypeVar

PakageType = list
Package = PakageType[Any]

PkgableClassType = TypeVar("PkgableClassType", bound="PkgableClass")
class PkgableClass(ABC):

    @abstractmethod
    def to_package(self) -> Package:
        pass

    @classmethod
    @abstractmethod
    def from_package(cls: Type[PkgableClassType], pkg: Package) -> PkgableClassType:
        pass

__all__ = ["Package", "PakageType", "PkgableClass"]