# pyright: reportMissingTypeStubs=false
import cbor2
from typing import Any, TypeVar, cast

from deZent_demo.utils.pkgable_class import PakageType, Package, PkgableClass

CodecType=bytes

def encode(obj: PkgableClass) -> CodecType:
    packaged_obj: Package = obj.to_package()
    cbor_encoded_obj: CodecType = cbor2.dumps(packaged_obj)
    return cbor_encoded_obj

PkgableClassType = TypeVar("PkgableClassType", bound=PkgableClass)
def decode(cls: type[PkgableClassType], encoded_message: CodecType) -> PkgableClassType:
    raw_message: Any = cbor2.loads(encoded_message)
    if not isinstance(raw_message, PakageType):
        raise TypeError(f"Raw decoded Message was not of PakageType({PakageType.__name__})!")
    packaged_message: Package = cast(Package, raw_message)
    return cls.from_package(packaged_message)

__all__ = [
    "CodecType",
    "encode",
    "decode",
]