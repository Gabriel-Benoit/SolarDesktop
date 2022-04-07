from __future__ import annotations

import numpy as np
from solar.math.tools.vector import Vector
from numbers import Real
from typing import Collection
from collections import abc


class Matrix(abc.Sequence[Vector]):
    """Represents a matrix (the mathematical object). This class is concretely implementing 
    a sequence (immutable) of Vector each representing a line.

    Fields:
    -------
        lineNB (int): the number of lines of self 
        columnNB (int): the number of columns of self 
        self[i,j] (float | Vector | Matrix): supports the index notation with slices and/or int combination 

    Note:
    -----
        +,-,/ operations between self and an other Matrix are supported and implements the mathematics standards.
        @ implements the matrix multplication and * scales the Matrix by the given number.
    """

    def __init__(self, m: Collection[Collection[Real]]):
        """Instantiate self, a new Matrix.

        Args:
        -----
            m (Collection[Collection[Real]]): the matrix in a form of collection of vector-likes

        Raises:
        ------
            ValueError: if len(m) == 0 or len(m[-1]) == 0
            ValueError: all lines aren't the same size

        """
        assert isinstance(m, Collection)
        if len(m) == 0:
            raise ValueError("Can't create an empty matrix.")
        self.__col_nb = len(m[-1])
        self.__l_nb = len(m)
        if len(m) == 0 or self.__col_nb == 0:
            raise ValueError("Can't create an empty matrix.")
        assert all(isinstance(v, Collection) for v in m)
        for line in m:
            if len(line) != self.__col_nb:
                raise ValueError("All lines should be the same size")

        self.__m: tuple[Vector] = tuple(Vector(*i) for i in m)

    def __len__(self) -> int:
        """Returns the number of line the matrix has

        Returns:
        --------
            int: the number of line the matrix has
        """
        return self.__l_nb

    def __add__(self, m: Matrix) -> Matrix:
        """
        Primitive addition for matrices

        Args:
        -----
            m (Matrix): the matrix to add self to 

        Raises:
        -------
            ValueError:  if self.__l_nb != m.lineNB or self.__col_nb != m.columnsNB

        Returns:
        --------
            Matrix: the result of self + m 

        """
        assert isinstance(m, Matrix)
        if self.__l_nb != m.lines or self.__col_nb != m.columns:
            raise ValueError("Can't add matrice which aren't the same size.")
        return self.__class__([v1 + v2 for v1, v2 in zip(self, m)])

    def __mul__(self, number: Real) -> Matrix:
        """Scales self by number and returns the result

        Args:
        -----
            number (Real): the Real to scale self by 

        Returns:
        --------
            Matrix: a copy self with all elements multiplied by number arg.

        """
        assert isinstance(number, Real)
        return self.__class__([v1 * number for v1 in self])

    def __matmul__(self, m: Matrix) -> Matrix:
        """
        Primitive multiplication for matrices

        Args:
        -----
            m (Matrix): the matrix to multiply self by 

        Raises:
        -------
            ValueError: if m.lineNB != self.columnsNB

        Returns:
        --------
            Matrix: the matrix A result of self @ m such that 
                forall i; 0 <= i < self.lineNB; 
                    forall j; 0 <= j < m.columnNB; 
                        A[i,j] == (sum_{k=0}^{self.columnNB - 1} m[k, j] * self [i, k] )

        """
        assert isinstance(m, Matrix)
        if self.__col_nb != m.lines:
            raise ValueError(
                "matrix 1 has not the same number of columns than the number of lines of matrix 2.")

        result = [
            [
                m_line @ m[:, j]
                for j in range(m.columns)
            ]
            for m_line in self
        ]
        # asserting dim relation: ( Z x Y ) * ( Y x W ) = ( Z x W )
        assert len(result) == self.__l_nb
        assert len(result[0]) == m.columns
        return self.__class__(result)

    def __str__(self) -> str:
        """
        Prints self in a clean way
        """
        digit_nb = self.__get_max_chars()
        string = '\n'
        for lines in range(self.__l_nb):
            for column in range(self.__col_nb):
                nb = self.__m[lines][column]
                spaces = (digit_nb - len(str(nb)))*' '
                comma = ', ' if column < self.__col_nb and column > 0 else '['
                end = '' if column != self.__col_nb - 1 else ']'
                string += comma + spaces + str(nb) + end
            string += '\n'
        return string

    def __get_max_chars(self) -> int:
        """Gets the number needed to print in a pretty way self

        Returns:
        --------
            int: the maximum of length (number of chars) of all numbers in self
        """
        def max_f(x, y): return x if x > y else y

        max = 0
        for lines in range(self.__l_nb):
            for column in range(self.__col_nb):
                nb = str(self.__m[lines][column])
                max = max_f(max, len(nb))
        return max

    def __get_line_slice(self, query: slice) -> list[Vector]:
        """Gets a slice of self -> the rows between start and stop of the slice

        Args:
        -----
            query (slice): the slice of self to get 

        Raises:
        -------
            ValueError: if the index is out of range [0 ... self.lineNB]

        Returns:
        --------
            list[Vector]: the slice of self to get


        """
        assert isinstance(query, slice)
        stride = 1 if query.step is None else query.step
        start = 0 if query.start is None else query.start
        stop = self.__l_nb if query.start is None else query.stop
        if start >= stop or start < 0 or stop > self.__l_nb:
            raise ValueError("Index out of bounds.")
        return self.__m[start:stop:stride]

    def __getitem__(self, query: tuple[slice | int, slice | int] | slice | int) -> Vector | Matrix | float:
        """Gets an element, a column, a row or a sub-matrix of self depending the given args using index notation.

        Args:
        -----
            query (tuple[slice | int, slice | int] | slice | int): the 'index' given.


        Raises:
        -------
            ValueError: if query arg is a tuple and not of length 2.
            IndexError: if a given index is out of range.

        Returns:
        --------
            Matrix: a sub-matrix of self
            Vector: a column, a row of self
            float: an element of self


        """

        assert isinstance(query, (tuple, slice, int))
        if isinstance(query, tuple):
            if len(query) != 2:
                raise ValueError("Tuple arg should be of length 2.")

            assert isinstance(query[0], (slice, int))
            assert isinstance(query[1], (slice, int))

            if isinstance(query[0], slice):
                sub_ = self.__get_line_slice(query[0])
                if isinstance(query[1], int):
                    if query[1] >= self.__col_nb:
                        raise IndexError('Index out of bounds')
                    return Vector(*[i[query[1]] for i in sub_])
                else:
                    return self.__class__([Vector(*v[query[1]])
                                           for v in sub_])
            else:
                if query[0] >= self.__l_nb:
                    raise IndexError('Index out of bounds')
                sub_ = self.__m[query[0]]
                if isinstance(query[1], int) and (query[1] >= self.__col_nb):
                    raise IndexError('Index out of bounds')
                return sub_[query[1]]
        elif isinstance(query, slice):
            return self.__class__(self.__get_line_slice(query))
        else:
            if query >= self.__l_nb:
                raise IndexError('Index out of bounds')
            return self.__m[query]

    def T(self) -> Matrix:
        """Returns the transpose of self

        Returns:
        --------
            Matrix: the transpose of self
        """
        res = []
        for i in range(self.__col_nb):
            res.append(Vector(*[self[l, i] for l in range(self.__l_nb)]))
        return self.__class__(res)

    def __array__(self, ) -> np.ndarray:
        """Function to convert self to ndarray

        Returns:
            np.ndarray: the 2-d array representing self
        """
        return np.array(self.__m)

    @property
    def columns(self) -> int:
        return self.__col_nb

    @property
    def lines(self) -> int:
        return self.__l_nb

    @staticmethod
    def I(cls, dim: int) -> Matrix:
        """Returns the identity matrix of the given dimension

        Parameters:
        -----------
            dim (int): the Matrix's dimension

        Raises:
        -------
            ValueError: if the dim is not strictly positive.

        Returns:
        --------
            Matrix: the identity matrix 
                m such that m.columnsNB == m.lineNB == dim and diag(m) is a Vector of 1 and others elements are 0.
        """
        assert isinstance(dim, int)
        if dim <= 0:
            raise ValueError("dim can't be zero or negative")
        return cls([[0]*i + [1] + [0]*(dim-1-i) for i in range(dim)])

    @staticmethod
    def NULL(cls, dim: int) -> Matrix:
        """Returns the null matrix of the given dimension

        Args:
        -----
            dim (int): the dimension of the matrix

        Raises:
        -------
            ValueError: if dim <= 0.

        Returns:
        --------
            Matrix: the null squared matrix of dimension dim.

        """
        assert isinstance(dim, int)
        if dim <= 0:
            raise ValueError("dim must be strictly positive")
        return cls([[0]*dim for i in range(dim)])


if __name__ == '__main__':
    # test code
    m1 = Matrix([
        [1, 2, 3],
        [1, 2, 3]
    ])
    print(m1 * 2)
