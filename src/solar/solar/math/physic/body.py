from __future__ import annotations
from turtle import position
from typing import Iterable, Sequence, TypedDict

import numpy as np
from solar.math.tools.vector import Vector, Vector3D
import string
import random

from numbers import Real


class BodyLike(TypedDict):
    """A type allias reprensenting a dictionnary that
    contains all properties to build a Body instance from it.

    """
    name: str
    position: tuple[Real, Real, Real]
    velocity: tuple[Real, Real, Real]
    mass: float


class Body:
    """
    Record class representing an object evolving in a 3D Euclidean space

    Fields:
    -------
    - name: name of this object (readonly)(str)
    - mass: mass of this object (readonly)(float)
    - position: position of this object in the 3D Euclidean space (np.ndarray)
    - velocity: velocity of this object in the 3D Euclidean space (np.ndarray)
    """

    def __init__(self, mass: float, position: Sequence[Real], velocity: Sequence[Real], name: str = None) -> None:
        """Instantiate self, a new Body

        Args:
        -----
            mass (float): self's mass
            position (Sequence[Real]):  self's initial position in 3D
            velocity (Sequence[Real]):  self's initial velocity in 3D
            name (str, optional): self's name. Defaults to None.

        Raises:
        -------
            ValueError: if mass <= 0
            ValueError: if position or velocity is not in 3D
        """
        # Type checking
        assert isinstance(position, Sequence)
        assert isinstance(velocity, Sequence)
        assert isinstance(mass, Real)

        if mass <= 0:
            raise ValueError("Mass of a body must be strictly positive.")

        if len(position) != 3:
            raise ValueError("Position must be in 3D.")

        if len(velocity) != 3:
            raise ValueError("Velocity must be in 3D.")

        if isinstance(name, str):
            self.__name = name
        else:
            # random name
            self.__name = '@'
            for i in range(7):
                self.__name += random.choice(string.ascii_lowercase)
        self.__m: float = float(mass)
        self.__p = np.array(position, dtype=np.float_)
        self.__v = np.array(velocity, dtype=np.float_)

    def __repr__(self) -> str:
        mass = self.mass
        position = self.position
        velocity = self.velocity
        name = self.name
        return f'<Body: {name= }, {mass= }, {position= }, {velocity= }>'

    @property
    def mass(self) -> float:
        return self.__m

    @property
    def position(self) -> np.ndarray:
        return self.__p

    @position.setter
    def position(self, _v: Sequence[Real]) -> None:
        """Sets self.position to _v

            Args:
            -----
                _v (Sequence[Real]): the new postion
        """
        assert isinstance(_v, Sequence)
        if len(_v) != 3:
            raise ValueError("Position must be in 3D.")
        assert all(isinstance(p, Real) for p in _v)
        self.__p = np.array(_v, dtype=np.float_)

    @property
    def velocity(self) -> np.ndarray:
        return self.__v

    @velocity.setter
    def velocity(self, _v: Sequence[Real]) -> None:
        """Sets self.velocity to _v

        Args:
        -----
            _v (Sequence[Real]): the new velocity

        """
        assert isinstance(_v, Sequence)
        if len(_v) != 3:
            raise ValueError("Velocity must be in 3D.")
        assert all(isinstance(p, Real) for p in _v)

        self.__v = np.array(_v, dtype=np.float_)

    @property
    def name(self) -> str:
        return self.__name

    def flatten(self) -> tuple[float, float, float, float, float, float, float]:
        """Flattens self to a tuple: (m, px, py, pz, vx, xy, xz)
        where m is self's mass, (px, py, pz) self's position and (vx, xy, xz) self's velocity.

        Returns:
        -------
            tuple[float,...]: self flattened
        """
        return (self.__m,) + tuple(self.__p) + tuple(self.__v)

    def jsonify(self) -> BodyLike:
        """Convert self into a TypedDict (BodyLike) which can streamed in JSON format.

        Returns:
        --------
            BodyLike: a TypedDict which can streamed in JSON format.
        """
        return {
            "name": self.name,
            "position": tuple(self.__p),
            "velocity": tuple(self.__v),
            "mass": float(self.__m),
        }


def flatten(bodies: Iterable[Body], split_mass: bool = True) -> Vector | tuple[Vector, tuple[float, ...]]:
    """Converts bodies args to a Vector containing all bodies flattened or a tuple[Vector, tuple[float]]
    of which the first element is a Vector that contains all bodies flattened without their mass and the
    second one a tuple of the related masses.

    Args:
    -----
        bodies (Iterable[Body]): the bodies to flatten
        split_mass (bool, optionnal): whether the masses should be given aside or not. Defaults to True.

    Returns:
    --------
        Vector: a list of all bodies flattened in one vector if split_mass == False
        tuple[Vector, tuple[float]]: the list of flattened bodies without their mass and the list of their mass if split_mass == True
    """
    assert isinstance(split_mass, bool)
    assert isinstance(bodies, Iterable)
    params = ()
    masses = ()
    # Avoid too strong typing by counting by hand
    i = 0
    for body in bodies:
        assert isinstance(body, Body)
        flattened = body.flatten()
        assert len(flattened) == 7
        if split_mass:
            params += flattened[1:]
            masses += flattened[:1]
        else:
            params += flattened
        i += 1
    if split_mass:
        result = (Vector(*params), masses)
        assert len(result[0]) == i*6
        assert len(result[1]) == i
    else:
        result = Vector(*params)
        assert len(result) == i*7
    return result


if __name__ == "__main__":
    # test code
    pass
