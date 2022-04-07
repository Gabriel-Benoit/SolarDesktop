from __future__ import annotations
from collections.abc import Collection
from typing import Generator, Iterable
from solar.types import T, VectorLike
from numbers import Real
from solar.math.tools.vector import Vector


def exclude(__iterable: Iterable[T], obj: T) -> Generator[T, None, None]:
    """Returns a generator not containing the paramater obj

    Args:
    -----
        __iterable (Iterable[T]): the iterable to exclude obj from 
        obj (T): the object to exclude from __iterable 

    Returns:
    --------
        Generator[T, None, None]: x, a generator such that forall i; 0 <= i < n; x[i] != obj  with n = len(__iterable)

    """
    assert isinstance(__iterable, Iterable)
    return (d for d in __iterable if d != obj)


def get_magnitude(v1: VectorLike, v2: VectorLike) -> float:
    """Gets the distance between 2 points in an Euclidian space


    Args:
    -----
        v1 (VectorLike): the first vector-like 
        v2 (VectorLike): the vector-like to compute the magnitude with v1 

    Raises:
    -------
        ValueError: if len(v1) != len(v2)

    Returns:
    --------
        float: x such that x = (sum_{i=0}^{n} ( |v2[i] - v1[i]|^2 ))^( 1/2 ) with n = len(v1)
    """
    # Type checking
    assert isinstance(v1, Collection)
    assert isinstance(v2, Collection)
    assert all(isinstance(i, Real) for i in v1)
    assert all(isinstance(i, Real) for i in v2)

    if len(v1) != len(v2):
        raise ValueError("v1 and v2 aren't the same length.")
    return norm(v2 - v1, 2)


def norm(v: Collection[Real], deg: int) -> float:
    """Computes the norm of degree deg for a given vector

    Args:
    -----
        v  (Collection[Real]): the vector-like to compute the norm of
        deg (int): the degree of the norm 

    Raises:
    -------
        ValueError: if deg <= 0.

    Returns:
    --------
        float: x such that x = (sum_{i=0}^{n} ( |v[i]|^deg ))^( 1/deg ) with n = len(v)
    """
    # Type checking
    assert isinstance(v, Collection)
    assert isinstance(deg, int)
    assert all(isinstance(i, Real) for i in v)

    if deg <= 0:
        raise ValueError("deg must be strictly positive.")
    return sum(
        (abs(el)**deg) for el in v
    )**(1/deg)
