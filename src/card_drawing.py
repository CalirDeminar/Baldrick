from PIL import ImageDraw
from PIL import ImageColor

from src.config import Config
from waypoint import WayPoint


def mark_wp_with_draw(draw: ImageDraw, wp: WayPoint, circle_radius: int, line_width: int, is_focused: bool= False):
    x_cur = wp.x_pixel
    y_cur = wp.y_pixel
    alpha = 150
    if is_focused:
        alpha = 255
    colour = (0, 0, 0, alpha)
    hex_colour = Config.route_colour()
    rgb_colour = ImageColor.getcolor(hex_colour, "RGB")
    colour = (rgb_colour[0], rgb_colour[1], rgb_colour[2], alpha)

    if wp.is_ip or wp.is_tgt:
        if wp.bearing_from_last is None:
            raise Exception("IP and TgT must not be the first waypoint in a route")

        if wp.is_tgt:
            draw.regular_polygon(
                (x_cur, y_cur, circle_radius),
                3,
                120 - wp.bearing_from_last,
                outline=colour,
                width=line_width
            )
        if wp.is_ip:
            draw.regular_polygon(
                (x_cur, y_cur, circle_radius),
                4,
                self.map.get_angle_off_north(wp.lat, wp.long) - wp.bearing_from_last,
                outline=colour,
                width=line_width
            )
    else:
        draw.ellipse(
            (
                (x_cur - circle_radius, y_cur - circle_radius),
                (x_cur + circle_radius, y_cur + circle_radius)
            ),
            outline=colour,
            width=line_width
        )
