from __future__ import annotations
from abc import ABCMeta, abstractmethod
from functools import partial
from typing import Any, Callable, Literal
from typing_extensions import Self

from solar.math.physic.body import Body

import solar_gui.core.utils as utils
from solar_gui.core.exceptions import ValidationError, StopValidation
from kivy.properties import ObjectProperty, NumericProperty, ObservableList, StringProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.floatlayout import FloatLayout
from solar.presets import DATA_PATH, get_presets_names, import_from_file, export_presets, import_saved_preset, remove_preset, save_n_body
from kivy.logger import Logger

APP_NAME = "Solar GUI: "


class HasErrorPopup:
    def dismiss_error_popup(self):
        """Closes the error popup
        """
        Logger.info(APP_NAME + "Closing error popup.")
        self._error_popup.dismiss()

    def open_error_popup(self, exception: Exception | str):
        """Opens a popup giving a feedback about the given exception or message

        Args:
        -----
            exception (Exception | str): the exception or message to be displayed
        """
        Logger.error(APP_NAME + f"Opening error popup: {exception!r}")
        content = ErrorDialog(ok=self.dismiss_error_popup,
                              message=str(exception))
        self._error_popup = Popup(
            title="Error!", content=content, size_hint=(0.5, 0.3))
        self._error_popup.open()


class HasPopup:
    def dismiss_popup(self):
        """Dismiss the current displayed popup
        """
        title = self._popup.title or ""
        Logger.info(APP_NAME + f"Leaving popup {title!r}.")
        self._popup.dismiss()

    def open_popup(self, *args, **kwargs):
        """Creates a new popup and pass  *args and **kwargs to it before opening it
        """
        title = kwargs.get("title", "")
        Logger.info(APP_NAME + f"Opening popup {title!r}.")
        self._popup = Popup(*args, **kwargs)
        self._popup.open()


class MainMenu(Screen):
    pass


class ManagePresets(Screen, HasErrorPopup, HasPopup):

    def load(self, _: str, filename: ObservableList):
        """Loads a preset file from file at filename[0]

        Args:
        -----
            _ (str): Any
            filename (ObservableList): list of strings which are path
                (first element will be taken as file path)
        """
        try:
            loaded_presets = import_from_file(filename[0])
            for preset in loaded_presets:
                save_n_body(str(DATA_PATH),
                            preset['system'], preset['name'])
            self.dismiss_popup()
        except (FileNotFoundError, ValueError, OSError) as e:
            self.open_error_popup(e)

    def export(self, path: str, filename: str):
        """Exports the presets to the given path in the file {filename}.solar.json

        Args:
        -----
            path (str): path to the directory where the file should be put
            filename (str): filename without an extension (also supports full path)
        """
        try:
            export_presets(path, filename.replace('.solar.json', ''))
            self.dismiss_popup()

        except OSError as e:
            try:
                filename = filename.split('\\')[-1].replace('.solar.json', '')
                export_presets(path, filename)
                self.dismiss_popup()
            except (FileExistsError, ValueError, OSError) as e:
                self.open_error_popup(e)
        except (FileExistsError, ValueError) as e:
            self.open_error_popup(e)

    def show_load(self):
        """Opens a popup to show loading preset dialog
        """
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self.open_popup(title="Load preset file", content=content,
                        size_hint=(0.9, 0.9))

    def show_export(self):
        """Opens a popup to show exporting preset dialog
        """
        content = ExportDialog(export=self.export, cancel=self.dismiss_popup)
        self.open_popup(title="Export presets", content=content,
                        size_hint=(0.9, 0.9))

    def show_delete(self):
        """Opens a popup to show deleting preset dialog
        """
        content = DeletePresetDialog(quit=self.dismiss_popup)
        self.open_popup(title="Delete presets", content=content,
                        size_hint=(0.9, 0.9))


class EncodeSystem(Screen, HasErrorPopup, HasPopup):
    slider_container: TimeSliderContainer = ObjectProperty(None)
    last_body_inserted: int = NumericProperty(1)

    def show_save(self, sys: InputContainer) -> None:
        """Checks if the custom system inputs are ok and opens a popup to save the preset under a name
        """
        validate = self.validate_custom_system()
        if validate is None:
            return
        if validate is False:
            self.open_error_popup("Can't save an empty system!")
            return

        content = SaveSystemDialog(
            sys=sys, cancel=self.dismiss_popup, save=self.save_system)
        self.open_popup(title="Save custom system",
                        auto_dismiss=False, content=content, size_hint=(0.6, 0.3))

    def validate_custom_system(self) -> None | tuple[Body] | Literal[False]:
        """Checks if the custom system inputs are ok and returns a tuple of bodies,
        if not puts the background in red and returns None and if the system is empty returns False.

        Returns:
        --------
            tuple[Body]: the system converted if everything is ok
            None: an input is incorrectly filled
            False: the system is empty

        """
        try:
            inputs: InputContainer = self.ids.outer_container
            if len(data := utils.extract_data(inputs)) == 0:
                return False
            return data
        except StopValidation as e:
            self.open_error_popup(e)
            return None

    def save_system(self, sys_input: NotEmptyInput, system: InputContainer) -> None:
        """Saves the correctly encoded system in resources.presets.solar.json file. If the the name is already taken,
        a feedback notifies the user that the operation is impossible.

        Args:
        -----
            sys_input (NotEmptyInput): The preset's name
            system (InputContainer): The inputs containing the system
        """
        if not sys_input.validate_content():
            sys_input.notify_error()
            Logger.error(APP_NAME +
                         f"Preset name `{sys_input.text}` is incorrect please try another name.")
            return
        name = sys_input.text
        path = str(DATA_PATH)
        Logger.info(APP_NAME +
                    f"Trying to save preset {name} at {path}\presets.solar.json.")
        try:
            save_n_body(path, utils.extract_data(
                system), name)
            self.dismiss_popup()
            Logger.info(APP_NAME +
                        f"Successfully saved preset {name} at {path}\presets.solar.json.")
        except ValueError as e:
            Logger.error(APP_NAME +
                         f"Couldn\'t save preset {name} at {path}\presets.solar.json: {e!r}")
            self.open_error_popup(e)

    def run_simulation(self, callback) -> None:
        """Gets the step and duration and runs the simulation

        Args:
        -----
            callback ((tuple[Body],float,float)->None): the callback that will run the simulation
        """
        system = self.validate_custom_system()
        if system is None:

            return
        if system is False:
            self.open_error_popup("Can't run an empty simulation!")
            return
        duration = self.slider_container.duration.value
        step = self.slider_container.step.value
        step = min(step, duration)
        callback(system, duration, step)

    def add_input_body(self, input_container: InputContainer) -> None:
        """Adds a child to the given InputContainer

        Args:
        -----
            input_container (InputContainer): InputContainer to add a child to
        """
        # Add child
        Logger.info(APP_NAME + "Adding a new line.")
        input_container.add_widget(
            InputBody(number=self.last_body_inserted))
        self.last_body_inserted += 1

    def del_input_body(self, input_container: InputContainer) -> None:
        """Opens a dialog to delete the chosen children

        Args:
        -----
            input_container (InputContainer): InputContainer to delete the last child from
        """
        content = DeleteBodyDialog(
            input_container=input_container, quit=self.dismiss_popup)
        self.open_popup(title="Delete bodies",
                        auto_dismiss=False, content=content, size_hint=(0.8, 0.8))


class ChoosePreset(Screen):
    slider_container: TimeSliderContainer = ObjectProperty(None)
    simulation_callback = ObjectProperty(None)

    def on_pre_enter(self, *args):
        """Leads to the preset menu (lets the user run a preset)
        and correctly sets the position of widgets
        """
        bxl: BoxLayout = self.ids.but_container
        names = get_presets_names()
        bxl.clear_widgets()
        for pn in names:
            btn = Button(size_hint=(None, None),
                         height=100,
                         width=200, text=f'Run {pn}')
            btn.bind(on_press=partial(self.run_simulation, pn))
            bxl.add_widget(btn)
        bxl.pos_hint = {
            'center_y': 0.5 - (len(names)*100)/(2*self.height),
            'center_x': 0.5 - (100/(2*self.width))}
        return super().on_pre_enter(*args)

    def run_simulation(self, preset: str, _: Button):
        """Gets the step and duration and runs the simulation

        Args:
        -----
            preset (str): the preset name
            _ (Button): the button this event is binded on
        """
        assert isinstance(preset, str)
        duration = self.slider_container.duration.value
        step = self.slider_container.step.value
        step = min(step, duration)
        try:
            system = import_saved_preset(preset)['system']
        except:
            return
        self.simulation_callback(system, duration, step)


class CustomTextInputMeta(ABCMeta, type(TextInput)):
    pass


class CustomTextInput(TextInput, metaclass=CustomTextInputMeta):

    @abstractmethod
    def validate_content(self) -> bool:
        raise NotImplementedError()

    def on_text_validate(self):
        """Event fired when enter key is pressed. Checks the rules in self.validate_content and apply or not a background color change
        """
        if self.validate_content():
            self.reset_error()
        else:
            self.notify_error()

    def reset(self):
        """Sets self.text to an empty string and makes sure self.background_color is white
        """
        self.reset_error()
        self.text = ''

    def notify_error(self):
        """Sets self.background_color to red
        """
        self.background_color = [242/255., 85/255., 68/255., 95/100.]

    def reset_error(self):
        """Sets self.background_color to white
        """
        self.background_color = [1, 1, 1, 1]


class NotEmptyInput(CustomTextInput):

    def validate_content(self) -> bool:
        """Checks whether self.text is empty or not

        Returns:
        --------
            bool: whether self.text is empty or not
        """
        return bool(self.text.strip())


class SupportsFloatInput(CustomTextInput):
    rule: Callable[[float], bool] = ObjectProperty(None)

    def validate_content(self) -> bool:
        """Checks whether self.text can be parsed as a float or not and apply self.rule if it is not None

        Returns:
        --------
            bool: false if self.text cannot be parsed as a float, otherwise true if self.rule is None or the result of self.rule(number)
        """
        try:
            res = float(self.text)
            if self.rule is not None:
                return self.rule(res)
            return True
        except:
            return False


class InputBody(BoxLayout):
    number: int = NumericProperty(0)
    relative_to: InputBody = ObjectProperty(None, allownone=True)
    dropdown: DropDown = ObjectProperty(None, allownone=True)

    def __repr__(self) -> str:
        # First time it is evaluated name doesn't exist
        try:
            return f'<InputBody: {self.ids.name.text}>'
        except AttributeError:
            return super(InputBody, self).__repr__()

    def reset(self):
        """Empties all inputs instances in self
        """
        children: list[SupportsFloatInput |
                       NotEmptyInput | Button] = self.children
        for child in children:
            if isinstance(child, CustomTextInput):
                child.reset()

    @property
    def name_input(self) -> NotEmptyInput:
        return self.ids.name

    @property
    def __position(self) -> tuple[float, float, float]:
        if self.relative_to is not None:
            bx, by, bz = self.relative_to.__position
        else:
            bx, by, bz = 0, 0, 0
        tx: SupportsFloatInput = self.ids.x_pos
        ty: SupportsFloatInput = self.ids.y_pos
        tz: SupportsFloatInput = self.ids.z_pos
        if not (tx.validate_content() or ty.validate_content() or tz.validate_content()):
            raise ValidationError()
        x = float(tx.text) + bx
        y = float(ty.text) + by
        z = float(tz.text) + bz
        return x, y, z

    @property
    def inputs(self) -> tuple[list[float], str, tuple[float, float, float]]:
        children: list[SupportsFloatInput |
                       NotEmptyInput | Button] = self.children
        float_dat = []
        error = False
        for child in children:
            if isinstance(child, SupportsFloatInput):
                if child.validate_content():
                    float_dat.append(float(child.text))
                else:
                    child.notify_error()
                    error = True

            elif isinstance(child, NotEmptyInput):
                if child.validate_content():
                    name = child.text
                else:
                    child.notify_error()
                    error = True
        if error:
            raise ValidationError()
        if self.relative_to is not None:
            translation = self.relative_to.__position
        else:
            translation = (0, 0, 0)
        float_dat.reverse()
        return float_dat, name, translation


class InputContainer(GridLayout):

    def reset_inputs(self):
        """Empties all InputBody instances in self
        """
        for i, child in enumerate(self.children):
            child.reset()
            child.ids.name.text = f"Body_{i}"
        self.on_children(self, self.children)

    def on_children(self, instance: Self, value: list[Any]):
        """Is called each time an update is made (add or remove) to the children list of self

        Args:
        -----
            instance (InputContainer): instance of the InputContainer which is modified
            value (list[Any]): the children list after action
        """
        def set_text(button: Button, _: NotEmptyInput, value: str):
            setattr(button, 'text', f'Relative\nto {value}')

        def set_relative_to(input: InputBody, other: InputBody, dropdown: DropDown, opener: Button, button: Button) -> None:
            setattr(input, 'relative_to', other)
            if other is not None:
                other.name_input.bind(text=partial(set_text, opener))
            dropdown.select(button.text)

        def looped(src: InputBody, dst: InputBody):
            if src is None or dst is None:
                return False
            return src is dst or looped(src, getattr(dst, 'relative_to'))

        def setattr_wrapper(opener, _, x):
            setattr(opener, 'text', x)

        def before_open(current: InputBody, dropdown: DropDown, input_lst: list[InputBody], opener_txt: str, opener: Button):
            dropdown.clear_widgets()
            if current.relative_to is not None:
                if current.relative_to not in input_lst:
                    current.relative_to = None
                    opener_txt = "Relative\nto (0,0,0)"
                else:
                    zero_but = Button(
                        text="Relative\nto (0,0,0)", size_hint_y=None, height=50)
                    zero_but.bind(on_release=partial(set_relative_to,
                                                     current, None, dropdown, opener))
                    dropdown.add_widget(zero_but)

            for other in input_lst:
                if current is not other and not looped(current, other):
                    btn = Button(
                        text=f"Relative\nto {other.name_input.text}", size_hint_y=None, height=50)
                    btn.bind(
                        on_release=partial(set_relative_to, current, other, dropdown, opener))
                    dropdown.add_widget(btn)
            setattr(opener, 'text', opener_txt)
            dropdown.open(opener)
        # Cleaning list
        value: list[InputBody] = [
            el for el in value if isinstance(el, InputBody)]

        # When all lines are removed except the first one which is compulsary
        if len(value) == 1 and len(value[0].children) > 0:
            if isinstance(value[0].children[0], Button):
                value[0].remove_widget(value[0].children[0])
            return
        # Update drop downs
        for child in value:

            # First generation skip iteration
            if len(child.children) == 0:
                continue

            last = child.children[0]
            if isinstance(last, Button):
                cached_txt: str = last.text
                child.remove_widget(last)
            else:
                cached_txt = "Relative\nto (0,0,0)"

            dropdown = DropDown(dismiss_on_select=True)

            opener = Button(text=cached_txt)
            opener.bind(on_release=partial(
                before_open, child, dropdown, value, cached_txt))

            dropdown.bind(on_select=partial(setattr_wrapper, opener))
            child.add_widget(opener)
            child.dropdown = dropdown
        return super(InputContainer, self).on_children(instance, value)

    @property
    def input_list(self) -> list[tuple[list[float], str, tuple[float, float, float]]]:
        stop = False
        values = []

        # Forcing all child update
        for child in self.children:
            try:
                values.append(child.inputs)
            except ValidationError:
                stop = True

        if stop:
            raise StopValidation("Inputs in red are not correctly filled.")
        return values


class SaveSystemDialog(FloatLayout):
    sys: InputContainer = ObjectProperty(None)
    cancel = ObjectProperty(None)
    save = ObjectProperty(None)


class AbstractDeleteDialogMeta(ABCMeta, type(FloatLayout)):
    pass


class AbstractDeleteDialog(FloatLayout, HasPopup, metaclass=AbstractDeleteDialogMeta):
    layout: BoxLayout = ObjectProperty(None)
    quit = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.render()

    @abstractmethod
    def render(self): ...


class DeleteBodyDialog(AbstractDeleteDialog):
    input_container: InputContainer = ObjectProperty(None)

    def delete_input_body(self, input_body: InputBody, btn: Button):
        """Deletes the passed InputBody from the current custom system

        Args:
        -----
            input_body (InputBody): the InputBody to delete
            btn (Button): instance attached to this event
        """
        Logger.info(APP_NAME + f"Removing body {input_body!r}.")
        self.layout.remove_widget(btn)
        self.input_container.remove_widget(input_body)

    def render(self):
        """Renders correctly all bodies that can be deleted
        """
        Logger.debug(
            APP_NAME + f"DeleteBodyDialog.render: {self.layout=}, {self.layout.width=}")
        self.layout.clear_widgets()
        #size = (self.layout.width, 60)
        for body in self.input_container.children:
            self.layout.add_widget(Button(text=f"Delete {body.name_input.text}", on_press=partial(
                self.delete_input_body, body), size_hint=(1, None)))


class DeletePresetDialog(AbstractDeleteDialog):

    def confirm(self, name: str):
        """Confirms the deletion of the preset that has {name} arg

        Args:
        -----
            name (str): The preset to delete
        """
        remove_preset(name)
        self.dismiss_popup()
        self.render()

    def handle_delete(self, name: str, _: Button):
        """Event to call when a delete button is pressed

        Args:
        -----
            name (str): The preset to delete
            _ (Button): button given by the event this method will binded to
        """

        content = ConfirmDialog(confirm=partial(self.confirm, name),
                                cancel=self.dismiss_popup, name=name)

        self.open_popup(title="Confirmation",
                        content=content, size_hint=(0.6, 0.3))

    def render(self):
        """Renders correctly all presets that can be deleted
        """
        self.layout.clear_widgets()
        names = get_presets_names()
        for pn in names:
            self.layout.add_widget(Button(text=f"Delete {pn}", on_press=partial(
                self.handle_delete, pn), size_hint=(1, None)))


class ConfirmDialog(FloatLayout):
    cancel = ObjectProperty(None)
    confirm = ObjectProperty(None)
    name = StringProperty(None)


class LoadDialog(FloatLayout):
    data_path = StringProperty(str(DATA_PATH))
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class ExportDialog(FloatLayout):
    data_path = StringProperty(str(DATA_PATH))
    export = ObjectProperty(None)
    cancel = ObjectProperty(None)
    text_input = ObjectProperty(None)


class ErrorDialog(FloatLayout):
    ok = ObjectProperty(None)
    message = StringProperty(None)


class TimeSliderContainer(BoxLayout):
    step: Slider = ObjectProperty(None)
    duration: Slider = ObjectProperty(None)

    def handle_step_move(self, value):
        self.step.value = min(self.duration.value, value)

    def handle_duration_move(self, value):
        self.duration.value = max(self.step.value, value)


class ProgressDialog(FloatLayout):
    cancel = ObjectProperty(None)
    bar = ObjectProperty(None)
