import csv
import math
from waypoint import WayPoint
from map_file import MapFile, find_map_from_wp
from tot_planner import get_waypoint_times, time_to_minutes
import PIL
from PIL import ImageDraw, Image, ImageOps
import time
PIL.Image.MAX_IMAGE_PIXELS = 10000000000

aspect_ratio = 6 / 4
# ratio of leg length we want the board height to be
margin_ratio = 1.25

waypoint_circle_radius_ratio = 0.06
waypoint_circle_width_ratio = 0.008
waypoint_circle_max_rad = 100
waypoint_circle_max_width = 20

cropping_margin = 8000


class Route:
    name = None
    map = None
    waypoints = []
    start_time = None
    time_on_target = None
    cruise_speed = None
    dash_speed = 500

    def __init__(self, route_name, start_time=(0, 0, 0), time_on_target=None):
        route_filename = "./routes/%s.csv" % route_name

        with open(route_filename, newline='') as csv_file:
            reader = csv.reader(csv_file, delimiter=',', quotechar='|')
            for i, record in enumerate(reader):
                if i > 0:
                    self.waypoints.append(WayPoint(record, i-1))
        if len(self.waypoints) < 1:
            raise Exception("Empty route")
        dcs_map_name = find_map_from_wp(self.waypoints[0].lat, self.waypoints[0].long)
        if dcs_map_name is None:
            raise Exception("No map data for specified route")
        self.name = route_name
        self.map = MapFile(dcs_map_name)
        self.start_time = start_time
        self.time_on_target = time_on_target
        self.set_wp_bearings()
        self.map_wp_pixels()
        self.set_tot_times()
        self.set_map_magvar()
        self.max_x = max(map(lambda wp: wp.x_pixel, self.waypoints))
        self.max_y = max(map(lambda wp: wp.y_pixel, self.waypoints))
        self.min_x = min(map(lambda wp: wp.x_pixel, self.waypoints))
        self.min_y = min(map(lambda wp: wp.y_pixel, self.waypoints))
        self.img = self.map.get_map_image()

    def map_wp_pixels(self):
        for wp in self.waypoints:
            (x, y) = self.map.get_pixels_for(wp.lat, wp.long)
            wp.x_pixel = x
            wp.y_pixel = y

    def get_cropped_map_image(self):
        img = self.img.copy()
        (x_max, y_max) = img.size

        img = img.crop((0, 0, min(self.max_x + cropping_margin, x_max), min(self.max_y + cropping_margin, y_max)))
        return img

    def set_map_magvar(self):
        all_tags = []
        for wp in self.waypoints:
            for tag in wp.tags:
                all_tags.append(tag)

        magvar_tags = list(filter(lambda tag: "MAGVAR" in tag, all_tags))

        if len(magvar_tags) > 0:
            working_tag = magvar_tags[0].replace("MAGVAR", "").strip()
            try:
                self.map.mag_var = float(working_tag)
            except ValueError:
                return

    def set_wp_bearings(self):
        for wp in self.waypoints:
            if wp.index > 0:
                prev = self.waypoints[wp.index-1]
                wp.bearing_from_last = wp.bearing_from(prev)
                wp.distance_from_last = wp.distance_from(prev)
            if wp.index < len(self.waypoints)-1:
                next_wp = self.waypoints[wp.index + 1]
                wp.bearing_to_next = next_wp.bearing_from(wp)

    def set_tot_times(self):
        [target_wp] = [x for x in self.waypoints if "TGT" in x.tags]
        timed_route = self.waypoints[0:target_wp.index+1]

        distances = list(map(lambda wp: wp.distance_from_last, timed_route))
        (times, speed) = get_waypoint_times(distances, self.start_time, self.time_on_target, self.dash_speed)
        self.cruise_speed = speed
        for i, time in enumerate(times):
            if i <= len(self.waypoints):
                self.waypoints[i].time = time
                self.waypoints[i].speed = speed
                if i == len(self.waypoints)-1:
                    self.waypoints[i].speed = self.dash_speed

    def kneeboard_width_for_wp_index(self, i, min_width=800, min_height=1200):
        if i < 1:
            return min_width, min_height
        current = self.waypoints[i]
        prev = self.waypoints[i-1]

        # (x_cur, y_cur) = self.map.get_pixels_for(current.lat, current.long)
        # (x_prev, y_prev) = self.map.get_pixels_for(prev.lat, prev.long)

        height = math.sqrt((prev.x_pixel - current.x_pixel) ** 2 + (prev.y_pixel - current.y_pixel) ** 2) * margin_ratio
        width = height * (1 / aspect_ratio)

        if height < min_height:
            return 800, 1200

        return width * margin_ratio, height * margin_ratio

    def draw_for_wp_index(self, index, draw, circle_radius, line_width, is_focused):
        wp = self.waypoints[index]
        # (x_cur, y_cur) = self.map.get_pixels_for(wp.lat, wp.long)
        x_cur = wp.x_pixel
        y_cur = wp.y_pixel
        is_ip = "IP" in wp.tags
        is_tgt = "TGT" in wp.tags
        alpha = 150
        if is_focused:
            alpha = 255

        if is_ip or is_tgt:
            if wp.bearing_from_last is None:
                raise Exception("IP and TgT must not be the first waypoint in a route")

            if is_tgt:
                draw.regular_polygon(
                    (x_cur, y_cur, circle_radius),
                    3,
                    120 + self.map.get_angle_off_north(wp.lat, wp.long) - wp.bearing_from_last,
                    outline=(0, 0, 0, alpha),
                    width=line_width
                )
            if is_ip:
                draw.regular_polygon(
                    (x_cur, y_cur, circle_radius),
                    4,
                    self.map.get_angle_off_north(wp.lat, wp.long) - wp.bearing_from_last,
                    outline=(0, 0, 0, alpha),
                    width=line_width
                )
        else:
            draw.ellipse(
                (
                    (x_cur - circle_radius, y_cur - circle_radius),
                    (x_cur + circle_radius, y_cur + circle_radius)
                ),
                outline=(0, 0, 0, alpha),
                width=line_width
            )

    def draw_route_for_wp_from_prev(self, img, index, draw, circle_radius, line_width, is_focused):
        if index > 0:
            wp = self.waypoints[index]
            prev = self.waypoints[index-1]

            wp_radius = circle_radius
            if "TGT" in wp.tags:
                wp_radius = circle_radius * 0.55
            if "IP" in wp.tags:
                wp_radius = circle_radius * 0.75

            # (x, y) = self.map.get_pixels_for(wp.lat, wp.long)
            # (x_prev, y_prev) = self.map.get_pixels_for(prev.lat, prev.long)

            alpha = 150
            if is_focused:
                alpha = 255

            angle = math.atan2(prev.y_pixel - wp.y_pixel, prev.x_pixel - wp.x_pixel)

            draw.line(
                (
                    (prev.x_pixel - (circle_radius * math.cos(angle)), prev.y_pixel - (circle_radius * math.sin(angle))),
                    (wp.x_pixel + (wp_radius * math.cos(angle)), wp.y_pixel + (wp_radius * math.sin(angle)))
                ),
                (0, 0, 0, alpha),
                line_width
            )
            if is_focused and wp.time is not None and prev.time is not None:
                minutes_for_leg = time_to_minutes(wp.time) - time_to_minutes(prev.time)
                minutes_to_draw = math.floor(minutes_for_leg)
                minute_x_distance = (prev.x_pixel - wp.x_pixel) / minutes_for_leg
                minute_y_distance = (prev.y_pixel - wp.y_pixel) / minutes_for_leg

                tag_len = line_width * 3

                # perp = (math.degrees(angle) + 90) % 360
                perp = angle + math.radians(90)
                x_distance = math.floor(math.cos(perp)*tag_len)
                y_distance = math.floor(math.sin(perp)*tag_len)

                for i in range(1, minutes_to_draw + 1):
                    x_center = wp.x_pixel + (minute_x_distance * i)
                    y_center = wp.y_pixel + (minute_y_distance * i)
                    draw.line(
                        (
                            (x_center + x_distance, y_center + y_distance),
                            (x_center - x_distance, y_center - y_distance)
                        ),
                        (0, 0, 0, 255),
                        math.floor(line_width/2)
                    )
                    temp = Image.new('L', (55, 55))
                    d = ImageDraw.Draw(temp)
                    d.text((0, 0), "%s" % i, fill=255, font_size=50, align="left")

                    text_angle = ((360-math.degrees(angle)) + 360 + 90) % 360
                    if 270 > text_angle > 90:
                        direction_invert = -1

                    rot = temp.rotate(text_angle, expand=1)
                    direction_invert = 1

                    img.paste(
                        ImageOps.colorize(rot, (0, 0, 0, 0), (0, 0, 0, 255)),
                        (math.floor((x_center + (x_distance * 2 * direction_invert))), math.floor(y_center + (y_distance * 2 * direction_invert))),
                        rot
                    )
                    # draw.text(
                    #     (x_center + (x_distance * 2), y_center + (y_distance * 2)),
                    #     "%s" % i,
                    #     fill="black",
                    #     align="left",
                    #     font_size=50,
                    # )

    def crop_board_for_wp(self, index, img):
        wp = self.waypoints[index]
        # (x, y) = self.map.get_pixels_for(wp.lat, wp.long)
        x = wp.x_pixel
        y = wp.y_pixel
        (board_width, board_height) = self.kneeboard_width_for_wp_index(index)
        local_img = img
        if index > 0:
            prev = self.waypoints[index - 1]
            # (x_prev, y_prev) = self.map.get_pixels_for(prev.lat, prev.long)

            x_centre = math.floor((x + prev.x_pixel) / 2)
            y_centre = math.floor((y + prev.y_pixel) / 2)

            bearing_from_prev = math.degrees(math.atan2(y - prev.y_pixel, x - prev.x_pixel)) + 90

            local_img = img.rotate(bearing_from_prev, center=(x_centre, y_centre))

            return local_img.crop((
                x_centre - board_width / 2,
                y_centre - board_height / 2,
                x_centre + board_width / 2,
                y_centre + board_height / 2
            ))

        return img.crop((
            x - (board_width / 2),
            y - (board_height / 2),
            x + (board_width / 2),
            y + (board_height / 2)
        ))

    def add_doghouse_for_wp(self, index, img):
        wp = self.waypoints[index]
        draw = ImageDraw.Draw(img, 'RGBA')
        font_height = get_font_size(img)

        margin = math.floor(font_height * 0.5)

        heading = "N/A"
        if index > 0:
            prev = self.waypoints[index-1]
            heading = "%s°" % ((wp.bearing_from(prev)-self.map.mag_var) % 360)
        next_heading = "N/A"

        if index < len(self.waypoints)-1:
            next_wp = self.waypoints[index+1]
            next_heading = "%s°" % ((next_wp.bearing_from(wp)-self.map.mag_var) % 360)

        distance = "N/A"
        if wp.distance_from_last is not None:
            distance = "%snm" % round(wp.distance_from_last, 1)

        time = "N/A"
        if wp.time is not None:
            hours = ("%s" % wp.time[0]).zfill(2)
            minutes = ("%s" % wp.time[1]).zfill(2)
            seconds = ("%s" % wp.time[2]).zfill(2)
            time = f"{hours}:{minutes}:{seconds}"

        speed = "N/A"
        if wp.speed is not None:
            speed = "%skts" % wp.speed

        min_alt = "N/A"
        if wp.min_alt is not None:
            min_alt = f"{wp.min_alt:,}ft"

        lines = [
            ("WP:", wp.name),
            ("MC:", heading),
            ("DIST:", distance),
            ("ETA:", time),
            ("ESA:", min_alt),
            ("TAS:", speed),
            ("NMC:", next_heading)
        ]

        headings_width = max(map(lambda j: draw.textlength(j[0], font_size=font_height), lines))
        values_width = max(map(lambda j: draw.textlength(j[1], font_size=font_height), lines))
        column_space = img.width * 0.005

        # background_x_min = math.floor(img.width*0.66)
        background_x_min = 0
        # background_base = (img.height*0.33)
        background_base = img.height - (len(lines) * (font_height + margin))
        background_width = math.floor(headings_width + values_width + column_space + margin*2)
        line_width = math.floor(img.width*0.004)

        draw.polygon(
            [
                (background_x_min, background_base),
                (background_x_min + background_width, background_base),
                (background_x_min + background_width, background_base + (font_height+margin)*len(lines)),
                (background_x_min, background_base + (font_height+margin)*len(lines)),
            ],
            (0, 0, 0, 255),
            (255, 255, 255, 200),
            width=line_width
        )

        for i, (heading, value) in enumerate(lines):
            height = background_base + ((margin + font_height) * i)
            draw.line(
                [
                    (background_x_min, height),
                    (background_x_min + background_width, height)
                ],
                (255, 255, 255, 200),
                width=line_width
            )
            draw.text(
                (background_x_min + margin, height + margin/3),
                heading,
                # font=font,
                align="left",
                fill="white",
                font_size=font_height
            )
            draw.text(
                (background_x_min + margin + headings_width + column_space, height + margin/3),
                value,
                # font=font,
                align="left",
                fill="white",
                font_size=font_height
            )
        return img

    def create_board_for_wp(self, index):
        img = self.get_cropped_map_image()

        draw = ImageDraw.Draw(img, "RGBA")
        (board_height, board_width) = self.kneeboard_width_for_wp_index(index)
        circle_radius = min(math.floor(board_width * waypoint_circle_radius_ratio), waypoint_circle_max_rad)
        line_width = min(math.floor(board_width * waypoint_circle_width_ratio), waypoint_circle_max_width)
        for i, wp in enumerate(self.waypoints):
            is_current = i == index
            is_previous = i == index - 1
            self.draw_for_wp_index(i, draw, circle_radius, line_width, is_previous or is_current)

            self.draw_route_for_wp_from_prev(img, i,  draw, circle_radius, line_width, is_current)
        return img

    def save_boards(self):
        for i, wp in enumerate(self.waypoints):
            board = self.create_board_for_wp(i)
            cropped_board = self.crop_board_for_wp(i, board)
            annotated_board = self.add_doghouse_for_wp(i, cropped_board)
            annotated_board = annotated_board.resize((1600, 2400), resample=PIL.Image.BILINEAR)
            board_name = "./%s/%s-wp%s.jpg" % (self.name, self.map.name, i+1)
            annotated_board.save(board_name)
            print("%s/%s  %s Board Complete" % (i+1, len(self.waypoints), board_name))

        # full_board = self.create_board_for_wp(i)
        # full_board.save("./%s/%s-Overview.jpg" % (self.name, self.map.name))

    def debug_doghouse(self):
        for index, wp in enumerate(self.waypoints):

            heading = "N/A"
            if index > 0:
                prev = self.waypoints[index - 1]
                heading = "%s°" % ((wp.bearing_from(prev) - self.map.mag_var) % 360)
            next_heading = "N/A"

            if index < len(self.waypoints) - 1:
                next_wp = self.waypoints[index + 1]
                next_heading = "%s°" % ((next_wp.bearing_from(wp) - self.map.mag_var) % 360)

            distance = "N/A"
            if wp.distance_from_last is not None:
                distance = "%snm" % round(wp.distance_from_last, 1)

            time = "N/A"
            if wp.time is not None:
                hours = ("%s" % wp.time[0]).zfill(2)
                minutes = ("%s" % wp.time[1]).zfill(2)
                seconds = ("%s" % wp.time[2]).zfill(2)
                time = f"{hours}:{minutes}:{seconds}"

            speed = "N/A"
            if wp.speed is not None:
                speed = "%skts" % wp.speed

            min_alt = "N/A"
            if wp.min_alt is not None:
                min_alt = f"{wp.min_alt:,}ft"

            lines = [
                ("WP:", wp.name),
                ("MC:", heading),
                ("DIST:", distance),
                ("ETA:", time),
                ("ESA:", min_alt),
                ("TAS:", speed),
                ("NMC:", next_heading)
            ]
            print(lines)
        print(("Magvar: ", self.map.mag_var))

    def write_flight_notes(self):
        output = ""
        max_name_len = 0
        for wp in self.waypoints:
            if len(wp.name) > max_name_len:
                max_name_len = len(wp.name)
        for wp in self.waypoints:
            lat_second_round = 0
            if wp.lat[2] >= 30:
                lat_second_round = 1
            long_second_round = 0
            if wp.long[2] >= 30:
                long_second_round = 1

            name_padding = " " * (max_name_len - len(wp.name))
            output += (
                    "%s%s\tN%02d %02d E%02d %02d\t%s\n" %
                    (
                        wp.name,
                        name_padding,
                        wp.lat[0],
                        wp.lat[1] + lat_second_round,
                        wp.long[0],
                        wp.long[1] + long_second_round,
                        ", ".join(wp.tags)
                    )
            )
        return output


def get_font_size(img):
    line_height_ratio = 0.02
    return math.floor(line_height_ratio * img.height)


if __name__ == "__main__":
    # Route("example", (0, 0, 0), (0, 30, 0)).save_boards()
    print(Route("01-05-2025-training", (0, 0, 0), (0, 30, 0)).save_boards())

