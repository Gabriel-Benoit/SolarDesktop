from __future__ import annotations
from numbers import Real
from numpy import arccos, arctan, cos, pi, sin

# Utils funcs available for the foreign users of this pkg


def spheric_to_euclidean(radius: Real, phi: Real, theta: Real) -> tuple[Real, Real, Real]:
    """Converts 3D spheric coordinates into 3D euclidean coordinates

    Pre:
    ----
    radius >= 0

    Args:
    -----
        radius (float): the radius 
        phi (float): the phi angle
        theta (float): the theta angle

    Returns:
    --------
        tuple[float, float, float]: (x,y,z) euclidean coordinates
    """
    assert isinstance(radius, Real)
    assert isinstance(phi, Real)
    assert isinstance(theta, Real)
    assert radius >= 0
    x = radius * sin(theta) * cos(phi)
    y = radius * sin(theta) * sin(phi)
    z = radius * cos(theta)
    return x, y, z


def euclidean_to_spheric(x: Real, y: Real, z: Real) -> tuple[Real, Real, Real]:
    """Converts 3D euclidean coordinates into 3D spheric coordinates


    Args:
    -----
        x (float): 
        y (float): 
        z (float): 

    Returns:
    --------
        tuple[float, float, float]: (the radius, the phi angle, the theta angle)
    """
    assert isinstance(x, Real)
    assert isinstance(y, Real)
    assert isinstance(z, Real)
    r = (x**2 + y**2 + z**2)**(1/2)
    theta = arccos(z/r)

    if x > 0:
        phi = arctan(y/x)
    elif x < 0:
        phi = arctan(y/x) + pi
    else:
        phi = pi/2
    return r, phi, theta


if __name__ == '__main__':
    # test code
    pass
