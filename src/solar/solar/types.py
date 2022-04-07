from __future__ import annotations
from numbers import Real
from typing import Collection, Sequence, TypeVar
from typing_extensions import Protocol
T = TypeVar('T')


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class VectorLike(Protocol, Collection[Real]):
    def __sub__(self, val: VectorLike) -> VectorLike:
        ...  # pragma: no cover

    def __add__(self, val: VectorLike) -> VectorLike:
        ...  # pragma: no cover

    def __mul__(self, val: VectorLike) -> VectorLike:
        ...  # pragma: no cover

    def __truediv__(self, val: VectorLike) -> VectorLike:
        ...  # pragma: no cover

    def __matmul__(self, val: VectorLike) -> Real:
        ...  # pragma: no cover


class MatrixLike(Protocol, Collection[VectorLike]):
    def __sub__(self, val: MatrixLike) -> MatrixLike:
        ...  # pragma: no cover

    def __add__(self, val: MatrixLike) -> MatrixLike:
        ...  # pragma: no cover

    def __mul__(self, val: MatrixLike) -> MatrixLike:
        ...  # pragma: no cover

    def __truediv__(self, val: MatrixLike) -> MatrixLike:
        ...  # pragma: no cover

    def __matmul__(self, val: MatrixLike) -> MatrixLike:
        ...  # pragma: no cover
