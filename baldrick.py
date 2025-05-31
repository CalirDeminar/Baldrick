import sys
import os
from os import path
import shutil
from route import Route
from map_file import find_map_from_wp
from tot_planner import parse_time

bundle_dir = path.abspath(path.dirname(__file__))
cwd = os.getcwd()
print("CWD: %s" % cwd)


def main():
    route_name = sys.argv[1]
    # route_file = "./routes/%s.csv" % route_name
    route_file = path.join(cwd, 'routes\\%s.csv' % route_name)
    # Args 2 and 3 are either ToT and blank or Start Time and ToT
    start_time = (0, 0, 0)
    time_on_target = None
    if len(sys.argv) > 3:
        start_time = parse_time(sys.argv[2])
        time_on_target = parse_time(sys.argv[3])
    if len(sys.argv) > 2:
        time_on_target = parse_time(sys.argv[2])
    if not os.path.exists(route_file):
        raise Exception("%s route file not found at %s" % (route_name, route_file))

    route = Route(route_name, start_time, time_on_target)
    if os.path.exists("./" + route_name):
        shutil.rmtree("./" + route_name)
    os.mkdir("./" + route_name)
    notes_filename = path.join(cwd, "%s\\notes.txt" % route_name)
    with open(notes_filename, "w") as f:
        f.write(route.write_flight_notes())
    legend_filename = path.join(bundle_dir, "./data/legend.jpg")
    legend_copy_loc = path.join(cwd, "./%s/legend.jpg" % route_name)
    shutil.copyfile(legend_filename, legend_copy_loc)
    route.save_boards()
    shutil.make_archive(path.join(cwd, "./%s_bundle" % route_name), 'zip', path.join(cwd, "./%s" % route_name))
    # shutil.make_archive("./%s_bundle" % route_name, 'zip', "./%s" % route_name)
    shutil.move(path.join(cwd, "./%s_bundle.zip" % route_name), path.join(cwd, "./%s/%s_bundle.zip" % (route_name, route_name)))
    # shutil.move("./%s_bundle.zip" % route_name, "./%s/%s_bundle.zip" % (route_name, route_name))


if __name__ == '__main__':
    main()
