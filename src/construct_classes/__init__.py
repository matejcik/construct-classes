import dataclasses
import typing as t

import construct as c

if t.TYPE_CHECKING:
    from typing_extensions import dataclass_transform
else:

    def dataclass_transform(**kwargs: t.Any) -> t.Any:
        def inner(cls: t.Any) -> t.Any:
            return cls

        return inner


# workaround for mypy self type bug
Self = t.TypeVar("Self", bound="Struct")


def subcon(
    cls: "t.Type[Struct]",
    *,
    metadata: t.Optional[t.Dict[str, t.Any]] = None,
    **kwargs: t.Any,
) -> t.Any:
    if metadata is None:
        metadata = {}
    metadata["substruct"] = cls
    return dataclasses.field(metadata=metadata, **kwargs)


@dataclass_transform(field_specifiers=(subcon,), kw_only_default=True)
class _StructMeta(type):
    def __new__(
        cls,
        name: str,
        bases: t.Tuple[type, ...],
        namespace: t.Dict[str, t.Any],
        *,
        kw_only: bool = True,
        **kwargs: t.Any,
    ) -> type:
        new_cls = super().__new__(cls, name, bases, namespace)
        if bases:
            assert bases[0].__name__ == "Struct"
            return dataclasses.dataclass(kw_only=kw_only, **kwargs)(new_cls)
        else:
            return new_cls


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
        args = {}
        for field in dataclasses.fields(cls):
            field_data = data.get(field.name)
            subcls = field.metadata.get("substruct")
            if subcls is None:
                args[field.name] = field_data
                continue

            if isinstance(field_data, c.ListContainer):
                args[field.name] = [subcls.from_parsed(d) for d in field_data]
            elif isinstance(field_data, c.Container):
                args[field.name] = subcls.from_parsed(field_data)
            elif field_data is None:
                continue
            else:
                raise ValueError(
                    f"Mismatched type for field {field.name}: expected a struct, found {type(field_data)}"
                )

        for key in args:
            args[key] = cls._decontainerize(args[key])
        return cls(**args)

    @classmethod
    def parse(cls: t.Type[Self], data: bytes) -> Self:
        result = cls.SUBCON.parse(data)
        return cls.from_parsed(result)
