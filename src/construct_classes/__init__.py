import dataclasses
import typing as t

import construct as c
from typing_extensions import dataclass_transform

# workaround for mypy self type bug
Self = t.TypeVar("Self", bound="Struct")


def subcon(cls: "t.Type[Struct]") -> t.Any:
    return dataclasses.field(metadata={"substruct": cls})


@dataclass_transform(field_descriptors=(subcon,))
class _StructMeta(type):
    def __new__(
        cls, name: str, bases: t.Tuple[type, ...], namespace: t.Dict[str, t.Any]
    ) -> type:
        new_cls = super().__new__(cls, name, bases, namespace)
        return dataclasses.dataclass()(new_cls)  # type: ignore # pyright is bad with metaclasses


class Struct(metaclass=_StructMeta):
    SUBCON: t.ClassVar["c.Construct[c.Container[t.Any], t.Dict[str, t.Any]]"]

    def build(self) -> bytes:
        return self.SUBCON.build(dataclasses.asdict(self))

    @staticmethod
    def _decontainerize(item: t.Any) -> t.Any:
        if isinstance(item, c.ListContainer):
            return [Struct._decontainerize(i) for i in item]
        return item

    @classmethod
    def from_parsed(cls: t.Type[Self], data: c.Container) -> Self:
        del data["_io"]
        for field in dataclasses.fields(cls):
            subcls = field.metadata.get("substruct")
            if subcls is None:
                continue

            field_data = data.get(field.name)
            if isinstance(field_data, c.ListContainer):
                data[field.name] = [subcls.from_parsed(d) for d in field_data]
            elif isinstance(field_data, c.Container):
                data[field.name] = subcls.from_parsed(field_data)
            elif field_data is None:
                continue
            else:
                raise ValueError(
                    f"Mismatched type for field {field.name}: expected a struct, found {type(field_data)}"
                )

        for key in data:
            data[key] = cls._decontainerize(data[key])
        return cls(**data)

    @classmethod
    def parse(cls: t.Type[Self], data: bytes) -> Self:
        result = cls.SUBCON.parse(data)
        return cls.from_parsed(result)
