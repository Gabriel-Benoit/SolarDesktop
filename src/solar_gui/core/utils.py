from __future__ import annotations
from solar.math.physic.body import Body
import solar_gui.core.widgets as w


def extract_data(data: w.InputContainer) -> tuple[Body]:
    bodies = tuple()
    for body_dat, name, (tx, ty, tz) in data.input_list:
        nx = tx + body_dat[0]
        ny = ty + body_dat[1]
        nz = tz + body_dat[2]
        bodies += (Body(body_dat[-1], (nx, ny, nz), body_dat[3:6], name),)

    return bodies
