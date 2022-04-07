from __future__ import annotations
from collections import abc
from typing import Collection, Iterable, Iterator
from functools import reduce
from numbers import Real

import numpy as np
from solar.types import VectorLike


class Vector(abc.Sequence[Real]):
    """
    Vector:
    -------

    A sequence (immutable) of floats of dimension N, N being the N elements given in Varargs of __init__()

    Fields:
    -------
        Vector_instance[i] : gives the i-th element of the vector (assignement isn't supported) (float)

    Note:
    -----
        This class support + and - operators ( they work the same way as algebric operations between vectors ).
        @ operator is also supported and computes the scalar product between 2 vectors.
        * operator scales self by the given Real.
    """

    def __init__(self, *args:  tuple[Real, ...]) -> None:
        """Instantiates self, a new Vector

        Args:
        -----
            Varargs : the elements to create the vector with (tuple[Real])

        """
        super().__init__()
        assert all(isinstance(arg, Real)
                   for arg in args), f'Expected Real type or sub-type'

        self._vect: tuple[float, ...] = args
        self.__len = len(args)

    def __iter__(self) -> Iterator[float]:
        return iter(self._vect)

    def __matmul__(self, v: Collection[Real]) -> float:
        """
        Computes the scalar product between self and a vector-like.

        Args:
        -----
            v (Collection[Real]):  a vector-like collection of Reals to compute the scalar product with

        Raises:
        -------
            ValueError: if len(self) != len(v)

        Returns:
        --------
            float: x such that x = sum of self[i] * v[i] with 0 <= i < len(self) if v is a Vector or a list


        """
        assert isinstance(v, Collection)
        assert all(isinstance(el, Real) for el in v)
        if len(v) == 0:
            return 0
        if self.__len != len(v):
            raise ValueError("v must have the same len than self.")
        return sum(v1 * v2 for v1, v2 in zip(self, v))

    def __mul__(self, number: Real) -> Vector:
        """Scales self by number arg and returns it. 

        Args:
        -----
            number (Real): the Real to scale self by

        Returns:
        --------
            Vector: self scaled by number arg
        """
        assert isinstance(number, Real)
        return self.__class__(*reduce(lambda acc, x: acc + [x*number], self, []))

    def __add__(self, v: Collection[Real]) -> Vector:
        """Adds v to self in a new Vector

        Args:
        -----
            v (Collection[Real]): The vector to add to self 

        Raises:
        -------
            ValueError: if len(self) != len(v)

        Returns:
        --------
            Vector: the result of self + v

        """
        assert isinstance(v, Collection)
        if len(v) == 0:
            return self
        if self.__len != len(v):
            raise ValueError("v must have the same len than self.")
        assert all(isinstance(el, Real) for el in v), 'type is not correct'
        return self.__class__(*[v1 + v2 for v1, v2 in zip(self, v)])

    def __sub__(self, v: Collection[Real]) -> Vector:
        """Substracts v from self in a new Vector

        Args:
        -----
            v (Collection[Real]): The vector-like to substract self to

        Raises:
        -------
            ValueError: if len(self) != len(v)

        Returns:
        --------
            Vector: the result of self - v

        """
        assert isinstance(v, Collection)
        if len(v) == 0:
            return self
        if self.__len != len(v):
            raise ValueError("v must have the same len than self.")
        assert all(isinstance(el, Real) for el in v), 'type is not correct'
        return self.__class__(*[v1 - v2 for v1, v2 in zip(self, v)])

    def __len__(self) -> int:
        """Returns the length of self

        Returns:
        --------
            int: the dimension of self
        """
        return self.__len

    def __eq__(self, __o: object) -> bool:
        """Checks whether self and __o are the same or not.

        Args:
        -----
            __o (object): the object to compare with self

        Returns:
        --------
            bool: whether self and __o are the same or not.
        """
        if isinstance(__o, Vector):
            return len(self) == len(__o) and all(self[i] == __o[i] for i in range(len(self)))
        return False

    def __getitem__(self, i: int | slice) -> float | Vector:
        """Lets the possibility to work with vectors as if they were lists 
        (and get items with brackets notation)

        Parameters:
        -----------
            i (int | slice) : the index or the slice of the element(s) wanted 


        Raises:
        -------
            ValueError: if i arg is outside of self's range


        Returns:
        --------
            float: the i-th element of self if i is an int
            Vector: the requested slice if i is a slice
        """
        assert isinstance(
            i, (int, slice)), f"Expected int or slice: received {type(i)}"
        if isinstance(i, int):
            if i >= self.__len:
                raise IndexError(
                    f"{i} outside of range [0 ... {self.__len - 1}]")
            return self._vect[i]
        else:
            if i.start is not None and i.start < 0:
                raise IndexError(
                    f"{i.start} outside of range [0 ... {self.__len - 1}]")

            if i.stop is not None and i.stop > self.__len:
                raise IndexError(
                    f"{i.stop} outside of range [0 ... {self.__len - 1}]")

            return self.__class__(*self._vect[i])

    def __repr__(self) -> str:
        return f"<Vector: {tuple(self._vect)!r}>"

    def __array__(self, *args, **kwargs) -> np.ndarray:
        """Function to convert self to ndarray

        Returns:
            np.ndarray: the 1-d array representing self
        """
        return np.array(self._vect, *args, **kwargs)

    @classmethod
    def concat(cls, *args: Iterable[VectorLike]) -> Vector:
        """Concatenates vectors together in a new Vector

        Args:
        -----
            Varargs: The vectors to concatenate (Iterable[Vector])

        Returns:
        --------
            Vector: a new vector containing all args concatenated
        """
        assert all(isinstance(el, (cls, Collection))
                   for el in args), f'All given args should be of type (or sub-type of) {type(cls)} or Collection[Real]'
        return cls(*reduce(lambda acc, x: acc+x, (list(v) for v in args), []))

    @staticmethod
    def sum(__iterable: Collection[Collection[Real]]) -> Vector:
        """Sums all vector-likes into one vector

        Args:
        -----
            __iterable (Collection[Collection[Real]]): the set of vector-like to sum up 

        Returns:
        --------
            Vector: a vector containing the sum of all vector-likes given 

        Note:
        -----
            The sum of an empty set of vectors (empty list for example) returns an empty vector (of dimension 0)
        """
        assert isinstance(__iterable, Collection)
        if len(__iterable) == 0:
            return EMPTY
        result: Collection[Real] = __iterable[0]
        size = len(result)

        def sum_core(acc, x):
            if len(x) != size:
                raise ValueError("All vectors must have the same size.")
            return acc + x

        return reduce(sum_core, __iterable[1:], result)


class Vector3D(Vector):
    """
    A Vector subclass with the number of dimensions fixed to 3

    Fields:
    -------
        x (Real): the first element of this vector 
        y (Real): the second element of this vector
        z (Real): the third element of this vector 

    See `Vector` for further information.
    """

    def __init__(self, x: Real, y: Real, z: Real) -> None:
        """Instatiate self a new Vector3D.

        Args:
            x (Real): the first element to give to self. 
            y (Real): the second element to give to self.
            z (Real): the third element to give to self. 
        """
        assert isinstance(x, Real), f'type given: {type(x)}'
        assert isinstance(y, Real), f'type given: {type(y)}'
        assert isinstance(z, Real), f'type given: {type(z)}'
        super().__init__(x, y, z)

    @property
    def x(self) -> float:
        return self[0]

    @property
    def y(self) -> float:
        return self[1]

    @property
    def z(self) -> float:
        return self[2]

    def __repr__(self) -> str:
        return super().__repr__().replace("Vector", "Vector3D")


EMPTY = Vector()

if __name__ == '__main__':
    # test code
    pass
