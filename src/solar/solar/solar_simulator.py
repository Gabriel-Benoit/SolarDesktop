from __future__ import annotations
from functools import reduce
import logging
from math import log
from numbers import Real
import matplotlib.pyplot as plt
from matplotlib import animation as am
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3D
from solar.exceptions import BodyError
from solar.math.integrator.rungekutta import ERK4
from solar.math.physic import hamiltonian, n_body
from matplotlib.figure import Figure
from typing import Any, Callable, Sequence
from solar.math.physic.body import Body, flatten
from solar.logger import Logger
from inspect import Parameter, Signature
import inspect


class SOLARSimulator:
    def __init__(self, data: Sequence[Body], duration: int, step: int, log_level: int = logging.INFO) -> None:
        """Instatiate self, new SOLAR simulation

        Args:
        -----
            data (Sequence[Body]): the N-body system
            duration (int): duration of the simulation in hours
            step (int): step of time (in hours) between each integration (determines the precision of the simulation)
            log_level (int): the level of logging according to python logging std lib

        Raises:
        -------
            ValueError: if duration <= 0
            ValueError: if step <= 0 or step > duration
        """
        Logger.setLevel(log_level)
        # Type checking
        assert isinstance(data, (Sequence))
        assert all(isinstance(body, Body)
                   for body in data), f"Excpected a list of Body... Received {list(type(body) for body in data)}"
        assert isinstance(duration, int)

        def check_pos(acc: bool, x: Body) -> bool:
            # Avoid going through every body if it is already broken
            if not acc:
                return acc

            for b in data:
                if (x is not b and all(cx == bx for (cx, bx) in zip(x.position, b.position))):
                    return False
            return True

        if len(set(data)) != len(data) or not reduce(check_pos, data, True):
            Logger.critical(
                "Solar: Please make sure all bodies have different coordinates...")
            raise BodyError(
                "Please make sure all bodies have different coordinates...")

        if duration <= 0:
            Logger.critical("Solar: Negative simulation duration.")
            raise ValueError("Can't have a negative duration.")
        if step <= 0 or step > duration:
            Logger.critical(
                "Solar: Step of simulation not in the range ]0, duration].")
            raise ValueError("Step must be in the range ]0, duration].")
        self.__data = data
        self.__duration = duration
        self.__step = step
        self.__error = {}
        self.__statedict = {}

    def run_simulation(self, loop_callBack: Callable[[int, Any], None], after_callBack: Callable[[Any], None], loop_callback_args=(), after_callback_args=()) -> None:
        """Runs the simulation and generates all points for each t between given start and stop.

        Args:
        -----
            loop_callBack (Callable[[int, Any], None]): callBack that will be called for each iteration of the simulation
            after_callBack (Callable[[int, Any], None]): callBack that will be called after the last iteration
            loop_callback_args (tuple[Any,...]): args to pass to loop_callBack. Defaults to ().
            after_callback_args (tuple[Any,...]): args to pass to after_callBack. Defaults to ().
        """
        assert isinstance(loop_callBack, Callable)
        assert isinstance(after_callBack, Callable)
        # Init
        start = 0.0
        stop = self.__duration * 3600
        step = self.__step * 3600
        flattened, masses = flatten(self.__data)
        self.__statedict = {i: {'x': [], 'y': [], 'z': [], 'name': self.__data[i].name}
                            for i in range(len(self.__data))}
        h = hamiltonian(self.__data)
        self.__error: dict[str, list] = {
            'x': [0], 'y': [h], 'dy': [0]}

        # Setup RK4
        rk4 = ERK4(n_body, flattened, start,
                   stop, int((stop - start)/step))
        rk4.set_func_kwargs(masses=masses)

        # Running simulation and encoding results
        Logger.info("Solar: Starting simulation...")
        for t, t_state in enumerate(rk4.run_simulation()):
            for j in range(0, len(t_state), 6):
                self.__statedict[j // 6]['x'].append(t_state[j])
                self.__statedict[j // 6]['y'].append(t_state[j + 1])
                self.__statedict[j // 6]['z'].append(t_state[j + 2])
            h = hamiltonian([Body(mass,
                                  t_state[index:index + 3],
                                  t_state[index + 3:index + 6]
                                  )
                             for index, mass in zip(range(0, len(t_state), 6), masses)])
            self.__error["x"].append(t*self.__step)
            self.__error["dy"].append(h - self.__error['y'][-1])
            self.__error["y"].append(h)
            loop_callBack(t, *loop_callback_args)
            Logger.info(
                f"Solar: Simulation: {100*t*step/stop: .2f} %")  # pragma: no cover
        after_callBack(*after_callback_args)  # pragma: no cover
        Logger.info("Solar: Simulation is done.")  # pragma: no cover

    def __scale(self) -> None:  # pragma: no cover
        """Scales correctly the graphs
        """
        Logger.info("Solar: Scaling graphs...")
        x = [max(v["x"]) for v in self.__statedict.values()]
        y = [max(v["y"]) for v in self.__statedict.values()]
        z = [max(v["z"]) for v in self.__statedict.values()]
        Logger.debug(f"Solar: Scaling: {x, y, z= }")
        final_length = max(x + y + z)
        Logger.debug(f"Solar: Scaling: {final_length= }")
        self.__axis.set_xbound(- final_length, final_length)
        self.__axis.set_ybound(- final_length, final_length)
        self.__axis.set_zbound(- final_length, final_length)

    def show_results(self) -> None:
        """Opens a windows that shows the results of the simulation.
        """
        if self.__error == {} or self.__statedict == {}:
            Logger.critical(
                "Solar: Please make sure to call the run_simulation method before this method: show_results")
            raise RuntimeError(
                "Please make sure to call the run_simulation method before this method: show_results")
        Logger.info("Solar: Plotting results.")
        self.__fig = plt.figure(1)
        self.__axis: Axes3D = self.__fig.add_subplot(
            1, 1, 1, projection="3d")
        self.__axis.autoscale(enable=False, axis='both')
        self.__scale()
        self.__lines_main: list[Line3D] = []
        for planet_dict in self.__statedict.values():
            line, = self.__axis.plot(
                xs=planet_dict['x'], ys=planet_dict['y'], zs=planet_dict['z'])
            self.__lines_main.append(line)
        self.__axis.legend([b.name for b in self.__data])

        # symlog(H_(t)) with 0 <= t <= stop time (in h)
        fig_hamiltonian: Figure = plt.figure(2)
        symlog = []
        for h_i in self.__error["y"]:
            # Log of 0 tends to minus infinity
            if h_i == 0:
                symlog.append(0)
            else:
                sign = 1 if h_i > 0 else -1
                symlog.append(sign*log(abs(h_i)))
        plt.plot(self.__error["x"], symlog)
        y_bound = log(
            max(abs(max(self.__error["y"])), abs(min(self.__error["y"]))))
        plt.gca().set_ybound(-2*y_bound, 2*y_bound)
        plt.xlabel('t (hours)')
        plt.ylabel(r'$symlog(E_k + E_p$)')

        # H_(t+1) - H_(t) with 0 <= t < stop time (in h)
        fig_hamiltonian_delta: Figure = plt.figure(3)
        plt.plot(self.__error["x"][1:], self.__error["dy"][1:])
        plt.xlabel('t (hours)')
        plt.ylabel(r'$\Delta(E_k + E_p)$')

        def anim_func_main(i):
            for index, planet_dict in enumerate(self.__statedict.values()):
                self.__lines_main[index].set_data_3d(
                    planet_dict['x'][0:i], planet_dict['y'][0:i], planet_dict['z'][0:i])
            return self.__lines_main
        frame_nb = self.__duration//self.__step
        interval_step = min(self.__step, 10)
        anim = am.FuncAnimation(self.__fig, anim_func_main,
                                frames=frame_nb, interval=interval_step*1000/24, blit=True)
        # Print figures
        plt.show()


if __name__ == '__main__':
    from solar import presets  # nopep8
    ps = presets.convert_bodylikes([
        presets.sun,
        presets.mercury,
        presets.venus,
        presets.earth,
        presets.mars,
        presets.jupiter,
        presets.saturn,
        presets.uranus,
        presets.neptune,
        presets.pluto
    ])
    s = SOLARSimulator(ps, 7200, 10)
    s.run_simulation(lambda t: None, lambda: None)
    s.show_results()
