from __future__ import annotations
from abc import ABC
from functools import reduce
from typing import Any, Callable, Collection, Generator
from solar.math.tools.vector import Vector
from numbers import Real
from solar.types import MatrixLike, VectorLike
import numpy as np


class ARK(ABC):
    """Abstract base class for Runge-Kutta explicit approximation methods.

    Static fields:
    --------------
    The subclass(es) must provide 3 static fields which represents the butcher tableau related to the desired method of resolution:
    - A (Matrix): a matrix of coefficients
    - b (Collection[Real]): a vector-like of coefficients
    - c (Collection[Real]): a vector-like of coefficients such that forall i; 0 <= i < n; c[i] = sum_{j=0}^{n} (A[i,j])

    For further information go check out https://en.wikipedia.org/wiki/List_of_Runge%E2%80%93Kutta_methods#Explicit_methods
    """

    def __init__(self, f: Callable[[float, VectorLike, Any], VectorLike], y0: VectorLike, t0: Real, tn: Real, n: int) -> None:
        """Instatiate self, an abstact base for Runge-Kutta explicit approximation methods.

        Args:
        -----
            f (Callable[[float, VectorLike, Any], VectorLike]): the function that will be integrated.
            y0 (VectorLike): the vector-like to start integration with
            t0 (Real): the time t to start with
            tn (Real): the last time of the interval to integrate
            n (int): the number of steps between t0 and tn. The greater is n, the better is accuracy and the slower is integration.

        Raises:
        -------
            ValueError: n is not strictly positive
            ValueError: if t0 equals tn
        """
        # Type checking
        assert isinstance(f, Callable), "f should be a callable."
        assert isinstance(y0, Collection), "y0 must be a vector-like."
        assert all(isinstance(y0_i, Real)
                   for y0_i in y0), "y0 must be a vector-like."
        assert isinstance(t0, Real), "t0 must be a float."
        assert isinstance(tn, Real), "tn must be a float."
        assert isinstance(n, int), "n must be a int."

        if (t0 - tn) == 0:
            raise ValueError("Can't have a null domain to integrate")
        if n <= 0:
            raise ValueError("Should at least have 1 step.")

        self.__func = f
        self.__y0 = y0
        self.__h = (tn - t0)/n
        self.__n = n
        self.__current_t = t0
        self.__f_kwargs = {}

    # Butcher tableau representation
    A: MatrixLike = NotImplemented
    b: VectorLike = NotImplemented
    c: VectorLike = NotImplemented

    def set_func_kwargs(self, **kwargs):
        """Sets the kwargs to pass to f, the function to integrate.

        Args:
        -----
            kwargs (dict[str:Any]): the key words args to pass to f 
        """
        self.__f_kwargs = kwargs

    def run_simulation(self) -> Generator[Vector]:
        """Runs the simulation for the given n steps + 1. The result will be returned as a generator of solutions

        Raises:
        -------
            ValueError: the format of static fields is wrong
            ValueError: self.A is not a matrix-line (all lines are not the same size)

        Yields:
        -------
            Generator[Vector]: the solutions for each step
        """
        assert isinstance(
            self.b, Collection), "self's b static attribute should be a VectorLike."
        assert isinstance(
            self.c, Collection), "self's c static attribute should be a VectorLike."
        if len(self.A) != len(self.c) or len(self.c) != len(self.b) or len(self.A) != len(self.b):
            raise ValueError(
                "self's A, b, c statics attributes aren't the right format.")

        for i, line in enumerate(self.A):
            if len(line) != len(self.A[i - 1]):
                raise ValueError("self.A must be a Matrix-like.")

        for i in range(self.__n+1):

            k_list: list[VectorLike] = []
            # Stable: k_{ni} = f(t_n + c_i*h, y_n + sum_{j=1}^{i-1} (a_ij * k_nj), **kwargs)*h
            # Unstable: k_{ni} = f(t_n + c_i*h, y_n + h*sum_{j=1}^{i-1} (a_ij * k_nj), **kwargs)
            for i, c_i in enumerate(self.c):
                k_list.append(self.__func(self.__current_t + c_i*self.__h,
                                          self.__y0 +
                                          (self.__sum([
                                              k_i * self.A[i, j] for j, k_i in enumerate(k_list)
                                          ])), **self.__f_kwargs)*self.__h)
            # Stable: y_{n+1} = y_n + sum_{i=1}^{s}(b_i*k_ni)
            # Unstable: y_{n+1} = y_n + sum_{i=1}^{s}(b_i*k_ni)*h
            self.__y0 += self.__sum([k_ni*b_i for b_i,
                                    k_ni in zip(self.b, k_list)])
            self.__current_t += self.__h
            yield self.__y0

    @staticmethod
    def __sum(vectors: Collection[VectorLike]):

        if vectors == []:
            return []
        return reduce(lambda acc, x: acc + x, vectors, np.array(len(vectors[-1]) * [0]))


class ERK4(ARK):
    """Explicit Runge Kutta method of order 4"""
    A = np.array([
        [0,   0,   0,   0],
        [1/2, 0,   0,   0],
        [0,   1/2, 0,   0],
        [0,   0,   1,   0],
    ])

    b = np.array(Vector(1/6, 1/3, 1/3, 1/6))
    c = np.array(Vector(0, 1/2, 1/2, 1))


if __name__ == '__main__':
    # test code
    pass
