from __future__ import annotations
import sys
from typing import Sequence
# Backend issues with matplotlib engine only on windows
if sys.platform == "win32":
    from ctypes import windll
    windll.user32.SetProcessDPIAware(-4)
from kivy.logger import Logger
from pkg_resources import resource_filename
from kivy.lang import Builder
from kivy.properties import NumericProperty, ObjectProperty
from kivy.clock import Clock
import threading as th
from kivy.app import App
from solar_gui.core.widgets import *
from solar.solar_simulator import SOLARSimulator
from solar.types import SingletonMeta
from solar.exceptions import BodyError
from kivy.uix.screenmanager import ScreenManager, NoTransition
import logging
from kivy.core.window import Window
# Forcing execution of logger module
import solar.logger  # nopep8


Logger.setLevel(logging.INFO)


class SolarAppMeta(SingletonMeta, type(App)):
    pass


class SolarApp(App, HasErrorPopup, HasPopup, metaclass=SolarAppMeta):
    current_sim: SOLARSimulator = ObjectProperty(None)
    sim_progression: int = NumericProperty(0)
    sm: ScreenManager = ObjectProperty(None)
    img_path: str = StringProperty(resource_filename(
        'solar_gui.resources', 'orion-nebula.jpg'))

    def build(self) -> ScreenManager:
        self.title = 'SOLAR'
        self.cancel = False
        self.sm = ScreenManager(transition=NoTransition())
        self.sm.add_widget(MainMenu(name='mainmenu'))
        self.sm.add_widget(ChoosePreset(name='presetmenu'))
        self.sm.add_widget(ManagePresets(name='preset_manager'))
        self.sm.add_widget(EncodeSystem(name='encodemenu'))
        Window.maximize()
        return self.sm

    def run_simulation(self, system: Sequence[Body], duration: float, step: float) -> None:
        """

        Args:
            system (Sequence[Body]): the system to do the simulation of
            duration (float): simulation  
            step (float): simulation step in hours
        """
        try:
            self.current_sim = SOLARSimulator(system, duration, step)
        except BodyError as e:
            self.open_error_popup(e)
            return

        def progression_callback(current_step):
            self.sim_progression = 100*step*(current_step / duration)
            if self.cancel:
                self.cancel = False
                self.dismiss_popup()
                Logger.info("Solar GUI: Cancelling simulation.")
                sys.exit()

        def close_popup_callback():
            self.progress_bar.value = 0
            self.dismiss_popup()

        def thread_callback():
            Logger.info("Solar GUI: Running simulation.")
            self.current_sim.run_simulation(
                progression_callback, close_popup_callback)

            def show_res(_):
                self.current_sim.show_results()
                Logger.info("Solar GUI: Leaving simulation.")
            Clock.schedule_once(show_res)

        layout = ProgressDialog(cancel=self.cancel_sim)
        self.progress_bar = layout.bar
        self.open_popup(title="Preparing data ...", content=layout,
                        auto_dismiss=False,
                        size_hint=(0.6, 0.3))

        thread = th.Thread(target=thread_callback)
        thread.start()

    def on_sim_progression(self, _: type[Self], value: float) -> None:
        """Event fired when the value of self.sim_progression is changed.
        Puts the value of self.progress_bar to the value arg  

        Args:
        -----
            _ (type[Self]): unused event arg
            value (float): the new value of self.sim_progression 
        """
        self.progress_bar.value = value

    def cancel_sim(self):
        """Sets self.cancel to True
        """
        self.cancel = True


Builder.load_file(resource_filename('solar_gui.core', 'main.kv'))
