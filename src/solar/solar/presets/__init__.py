from __future__ import annotations
from numbers import Real
import pathlib
import sys
from typing import Collection, Generator, Iterable, Sequence, TypedDict
from solar.math.physic.body import Body, BodyLike
from json.decoder import JSONDecodeError
from solar.presets.raw import *
import json
import os
__WRONG_FORMAT = "Data format is not correct."


class PresetLike(TypedDict):
    system: Sequence[BodyLike]
    standardized_name: str
    name: str


class Preset(TypedDict):
    system: Sequence[Body]
    standardized_name: str
    name: str


def is_presetlike(data: list[PresetLike]) -> bool:
    """Checks whether data is a PresetLike

    Args:
    -----
        data (list[PresetLike]): the data to check

    Returns:
    --------
        bool: Whether data is a PresetLike
    """
    return (isinstance(data, list) and all(isinstance(ps, dict)
                                           and ps.keys() == PresetLike.__annotations__.keys()
                                           and isinstance(ps["name"], str)
                                           and isinstance(ps["standardized_name"], str)
                                           and isinstance(ps["system"], Sequence)
                                           and all(isinstance(p["mass"], Real)
                                                   and isinstance(p["name"], str)
                                                   and isinstance(p["position"], Sequence)
                                                   and isinstance(p["velocity"], Sequence)
                                                   and len(p["position"]) == 3
                                                   and len(p["velocity"]) == 3
                                                   and all(isinstance(x, Real) for x in p["position"])
                                                   and all(isinstance(x, Real) for x in p["velocity"])
                                                   and len(p["velocity"]) == 3
                                                   for p in ps["system"])
                                           for ps in data))


def get_all_presets() -> list[PresetLike]:
    """Gets all the presets in the resource presets.solar.json

    Returns:
    --------
        list[PresetLike]: all the presets found in the resource presets.solar.json

    Raises:
    -------
        ValueError: if the data is broken
    """

    with open(PRESET_PATH, 'r+') as fd:
        try:
            data: list[PresetLike] = json.load(fd)

            if not is_presetlike(data):
                raise ValueError(__WRONG_FORMAT)

        except JSONDecodeError:
            data = []
        return data


def remove_preset(name: str) -> None:
    """Removes a preset from the preset resource file.

    Args:
        name (str): the name of the preset

    Raises:
        ValueError: If the given names does not belong to a preset
    """
    assert isinstance(name, str)
    name = standardize_name(name)
    if not name in get_presets_standardized_names():
        raise ValueError("This preset doesn't exist.")
    with open(PRESET_PATH, 'r+') as fd:
        try:

            data: list[PresetLike] = json.load(fd)
        except JSONDecodeError:
            return
        assert isinstance(data, list)
        keys = PresetLike.__annotations__.keys()
        # All presets loaded have the same keys has PresetLike class
        assert all(ps.keys() == keys for ps in data)
        fd.seek(0)
        fd.truncate()
        json.dump(
            list(filter(lambda ps: ps["standardized_name"] != name, data)),
            fd, indent=4, sort_keys=True)


def standardize_name(name: str) -> str:
    """Removes all surrounding spaces, lower and replace inner spaces by underscores from a name

    Example:
    --------
    " I am a name " => "i_am_a_name"

    Args:
    -----
        name (str): source name

    Returns:
    --------
        str: standardized name
    """
    return name.lower().strip().replace(' ', '_')


def get_presets_names() -> tuple[str, ...]:
    """Returns all the names from the availables presets

    Returns:
        tuple[str]: the names from the availables presets
    """
    return tuple(ps["name"] for ps in get_all_presets())


def get_presets_standardized_names() -> tuple[str, ...]:
    """Returns all the standardized names from the availables presets

    Returns:
        tuple[str]: the standardized names from the availables presets
    """
    return tuple(ps["standardized_name"] for ps in get_all_presets())


def convert_bodylikes(data: Collection[BodyLike]) -> tuple[Body, ...]:
    """Returns a tuple of Body from a collection of BodyLike objects

    Args:
    -----
        data (Collection[BodyLike]): the data source

    Raises:
    -------
        ValueError: if the data is not the right format

    Returns:
    --------
        tuple[Body, ...]: a tuple of Body that represents the given n-body system
    """
    # Type checking
    assert isinstance(data, Collection)
    assert all(isinstance(d, dict) for d in data)

    keys = {'name', 'velocity', 'position', 'mass'}
    if not all(keys == set(d.keys()) for d in data):
        raise ValueError(
            "Incorrect data format.")
    return tuple(Body(**body_like) for body_like in data)


def import_saved_preset(preset_name: str) -> Preset:
    """Retrieves a Preset from resources/presets.solar.json.

    Args:
    -----
        preset_name (str): the wanted preset name

    Raises:
    -------
        ValueError: if the preset doesn't exist
        ValueError: if the data is not the right format

    Returns:
    --------
        Preset: the wanted Preset
    """
    # Type checking
    assert isinstance(preset_name, str)
    names = get_presets_names()
    if preset_name not in names:
        raise ValueError("Preset does not exist.")
    preset_name = standardize_name(preset_name)
    data: list[PresetLike] = get_all_presets()
    for preset_lk in data:
        if preset_lk["standardized_name"] == preset_name:
            preset_lk["system"] = convert_bodylikes(
                preset_lk["system"])
            return preset_lk


def import_from_file(path: str) -> Generator[Preset, None, None]:
    """Retrieves a generator of Preset from a *.solar.json encoded file.
    JSON required structure :\n
    [
        {
            "standardized_name": str
            "name": str,
            "system": list[BodyLike]
        }, ...
    ]

    Args:
    -----
        path (str): the data source path

    Raises:
    -------
        ValueError: if the data is not the right format in the source file
        ValueError: if the file extension is not .solar.json
        FileNotFoundError: if the file is broken or does not exist


    Yields:
    --------
        Generator[Preset]: a generator of Preset for each source n-body system
    """
    # Type checking
    assert isinstance(path, str)

    if not (os.path.exists(path) and os.path.isfile(path)):
        raise FileNotFoundError("Unable to find the file.")

    if not path.endswith(".solar.json"):
        raise ValueError("Incorrect file extension.")

    with open(path, 'r+') as fd:
        def update_and_return(dict, key, value):
            dict[key] = value
            return dict
        return (update_and_return(preset, "system", convert_bodylikes(preset["system"])) for preset in json.load(fd))


def save_n_body(dir_path: str, data: Iterable[Body], preset_name: str) -> None:
    """Appends the given Iterable[Body] on a list[BodyLike] format and the preset name in the {dir_path}/presets.solar.json file\n
    JSON structure :\n
    [
        {
            "standardized_name": str
            "name": str,
            "system": list[BodyLike]
        }, ...
    ]

    Args:
    -----
        dir_path (str): the data destination dir path
        data (Iterable[Body]): the data to save
        preset_name (str): the name of the preset

    Raises:
    -------
        NotADirectoryError: if the path is not a directory
        ValueError: if the given preset_name is already taken


    """
    # Type checking
    assert isinstance(data, Iterable)
    assert isinstance(dir_path, str)
    assert isinstance(preset_name, str)

    if not os.path.isdir(dir_path):
        raise NotADirectoryError("dir_path must be a directory.")
    standardized = standardize_name(preset_name)
    filename = f"{dir_path}/presets.solar.json"

    with open(filename, 'r+') as fd:
        try:
            current: list[PresetLike] = json.load(fd)
            for bd_like in current:
                if bd_like["standardized_name"] == standardized:
                    raise ValueError("Preset name is already taken.")
        except JSONDecodeError:
            current = []

        current.append({"standardized_name": standardized,
                        "name": preset_name,
                        "system": [body.jsonify() for body in data]
                        })
        fd.seek(0)
        fd.truncate()
        json.dump(current, fd, indent=4, sort_keys=True)


def export_presets(path: str, filename: str) -> None:
    """Export all presets to the given path and filename in solar.json format

    Args:
    -----
        path (str): the path to the directory
        filename (str): the file name (without any extension)

    Raises:
    -------
        ValueError: if the filename is empty
        ValueError: if the path arg is not a directory path
        FileExistsError: if the file already exists in the given directory directory
    """
    assert isinstance(path, str)
    assert isinstance(filename, str)
    if not filename:
        raise ValueError("File name can't be empty.")

    if not os.path.exists(path) and os.path.isdir(path):
        raise ValueError("Path must be a directory.")

    path = f"{path}/{filename}.solar.json"

    if os.path.exists(path):
        raise FileExistsError("File already exists.")

    with open(PRESET_PATH, 'r+') as src_fd,  open(path, 'w+') as dst_fd:
        json.dump(json.load(src_fd), dst_fd, indent=4, sort_keys=True)


def get_datadir() -> pathlib.Path:
    """Returns a parent directory path
    where persistent application data can be stored.

    Returns:
    --------
        linux: ~/.local/share\n
        macOS: ~/Library/Application Support\n
        windows: C:/Users/<USER>/AppData/Roaming\n
    """

    home = pathlib.Path.home()

    if sys.platform == "win32":
        return home / "AppData/Roaming"
    elif sys.platform == "linux":
        return home / ".local/share"
    elif sys.platform == "darwin":
        return home / "Library/Application Support"


"""Set up the preset file in the user data dir
"""

DATA_PATH = get_datadir() / "SolarApp"

try:
    DATA_PATH.mkdir(parents=True)
except FileExistsError:
    pass
PRESET_PATH = DATA_PATH/"presets.solar.json"
if not PRESET_PATH.exists():

    builtin_preset: PresetLike = [{
        'name': 'Solar system',
        'standardized_name': 'solar_system',
        'system':
        [
            sun,
            mercury,
            venus,
            earth,
            mars,
            jupiter,
            saturn,
            uranus,
            neptune,
            pluto
        ]

    }]
    with open(PRESET_PATH, 'w+') as fd:
        json.dump(builtin_preset, fd)


if __name__ == '__main__':
    pass
