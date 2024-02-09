from typing import Any, List, Optional, Tuple, cast

import blf
import bpy
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector

from ..core.states import state
from ..core.utils.ui import redraw_area


class NameTagSettings:
    def __init__(self):
        self.x_offset: float = 0
        self.y_offset: float = 0
        self.z_offset: float = 6.5
        self.fontsize: int = 25
        self.text_rgba: Tuple[float, float, float, float] = (1, 1, 1, 1)
        self.font_id: int = 0
        self.name_tag_handle: Any = None
        self.name_tag_draw: Any = None
        self.region: Optional[bpy.types.Region] = None


name_tag_settings = NameTagSettings()


def name_tag_draw():
    global name_tag_settings

    blf.size(name_tag_settings.font_id, name_tag_settings.fontsize)
    blf.color(name_tag_settings.font_id, *name_tag_settings.text_rgba)
    if name_tag_settings.region:
        region = name_tag_settings.region
        region_data = cast(bpy.types.RegionView3D, region.data)
    else:
        return

    dancer_names = state.dancer_names
    for name in dancer_names:
        try:
            dancer_obj = cast(bpy.types.Object, bpy.data.objects[name])
            dancer_location = dancer_obj.location
            text_location_3d = Vector(
                (
                    dancer_location[0] + name_tag_settings.x_offset,
                    dancer_location[1] + name_tag_settings.y_offset,
                    dancer_location[2] + name_tag_settings.z_offset,
                )
            )
            text_view_2d = location_3d_to_region_2d(
                region, region_data, text_location_3d
            )
            text_w, text_h = cast(
                Tuple[float, float], blf.dimensions(name_tag_settings.font_id, name)
            )
            blf.position(
                name_tag_settings.font_id,
                text_view_2d[0] - text_w / 2,
                text_view_2d[1] - text_h / 2,
                0,
            )
            blf.draw(name_tag_settings.font_id, name)

        except AttributeError:
            pass


def name_tag_handler():
    global name_tag_settings
    if name_tag_settings.name_tag_draw is not None:
        bpy.types.SpaceView3D.draw_handler_remove(
            name_tag_settings.name_tag_handle, "WINDOW"
        )
    name_tag_settings.name_tag_draw = bpy.types.SpaceView3D.draw_handler_add(
        name_tag_draw, (), "WINDOW", "POST_PIXEL"
    )


def mount():
    global name_tag_settings
    screen = cast(bpy.types.Screen, bpy.data.screens["Layout"])
    area = next(
        area
        for area in cast(List[bpy.types.Area], screen.areas)
        if area.type == "VIEW_3D"
    )
    region = next(
        region
        for region in cast(List[bpy.types.Region], area.regions)
        if region.type == "WINDOW"
    )
    name_tag_settings.region = region
    name_tag_settings.name_tag_handle = bpy.types.SpaceView3D.draw_handler_add(
        name_tag_handler, (), "WINDOW", "POST_PIXEL"
    )
    print("Name tag mounted")
    redraw_area({"VIEW_3D"})


def unmount():
    global name_tag_settings
    try:
        if name_tag_settings.name_tag_handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(
                name_tag_settings.name_tag_handle, "WINDOW"
            )
            name_tag_settings.name_tag_handle = None
    except:
        pass