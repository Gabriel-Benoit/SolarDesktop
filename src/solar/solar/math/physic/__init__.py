from __future__ import annotations
from typing import Collection, Iterable, Sequence
from numbers import Real
from solar.math.physic.body import Body
from solar import exclude, get_magnitude, norm
from solar.math.tools.vector import Vector, Vector3D
import numpy as np

__G = 6.6743015e-11


def n_body(t: float, current_state: Sequence[Real], masses: Sequence[Real]) -> Vector:
    """
    Computes coordinates of particules from an initial state according to newton's second law, in a n-body system situation

    Pre:
    ----
    forall i; 0 <= i < len(masses); masse > 0

    Args:
    -----
        t (float): the time to calculate state for (here useless but the params should match integrator patterns)
        current_state (Sequence[Real]): the current state vector-like containing position and velocity for each particle in the system 
        masses (Sequence[Real]): the vector-like containing mass of each particle 

    Raises:
    -------
        ValueError: if 6*len(masses) != len(current_state)

    Returns:
    --------
        Vector: the next state vector containing position and velocity for each particle in the system

    """
    # Type checking
    assert isinstance(current_state, Sequence)
    assert isinstance(masses, Sequence)
    assert all(isinstance(el, Real) for el in current_state)
    # Pre + type checking
    assert all(isinstance(mass, Real) and mass > 0 for mass in masses)

    if 6*len(masses) != len(current_state):
        raise ValueError("masses and current_state are out of sync")
    body_list = [Body(mass, current_state[i:i+3], current_state[i+3:i+6])
                 for (i, mass) in zip(range(0, len(current_state), 6), masses)]
    # Iterate over each body
    next_state = []
    for planet in body_list:
        next_state.append(planet.velocity)
        next_state.append(get_acceleration(
            list(exclude(body_list, planet)), planet))
    result = Vector.concat(*next_state)
    assert len(result) == len(current_state)
    return result


def hamiltonian(particles: Sequence[Body]) -> np.longfloat:
    """Computes the Hamiltonian (H) of an n-body system.
    In this case the definition of H = T + U where 
    T = ``get_kinetic_energy_gen`` and U = ``get_gravitational_energy``

    Args:
    -----
        particles (Sequence[Body]): the body sequence of the n-body system 

    Returns:
    --------
        longfloat: the result H (= T + U), the hamiltonian of the given n-body system

    """
    assert isinstance(particles, Sequence)
    assert all(isinstance(particle, Body) for particle in particles)

    return get_gravitational_energy(particles) + get_kinetic_energy_gen(
        (b.mass, b.velocity) for b in particles
    )


def get_gravitational_energy(particles: Sequence[Body]) -> np.longfloat:
    """Computes the total gravitional energy of a n-body system.

    Args:
    -----
        particles (Sequence[Body]): the body sequence of the n-body system 

    Returns:
    --------
        longfloat: the sum of the force between each body of the given n-body system
    """
    assert isinstance(particles, Sequence)
    u = np.longfloat(0.0)
    for i, p in enumerate(particles):
        u += sum(
            (__G * p.mass * particles[j].mass) /
            get_magnitude(p.position, particles[j].position)
            for j in range(i+1, len(particles))
        )

    return -u


def get_kinetic_energy_gen(particles: Iterable[tuple[float, Vector3D]]) -> float:
    """Computes the total kinetic energy of a n-body system.

    Args:
    -----
        particles (Iterable[Body]): the body list of the n-body system 

    Returns:
    --------
        longfloat: the sum of the kinectic energy for each body of the given n-body system
    """
    assert isinstance(particles, Iterable)
    # Sum_i (p_i^2 / 2m_i) with p_i the momentum for particle i
    return sum((norm(velocity * mass, 2)**2)/(2*mass) for mass, velocity in particles)


def get_acceleration(others: Collection[Body], particle: Body) -> Vector3D:
    """Computes the acceleration for one particle in a n-body system

    Args:
    -----
        others (Collection[Body]): the other particles to determine the acceleration from 
        particle (Body): the particle to determine the acceleration for 

    Returns:
    --------
        Vector3D : the acceleration in 3D space

    """
    assert isinstance(particle, Body)
    assert isinstance(others, Collection)
    assert all(isinstance(other, Body) for other in others)
    acceleration = Vector3D(0, 0, 0)
    for other_body in others:
        # Distance between 2 bodies
        r = get_magnitude(particle.position, other_body.position)
        # Direction determined by the difference between their positions
        dir: Vector3D = other_body.position - particle.position
        # Updating acceleration of this particle
        acceleration += dir * ((__G *
                               other_body.mass)/(r**3))
    return acceleration


if __name__ == '__main__':
    # test code
    pass
