import sys
import os
from os import path
import shutil
from route import Route
from map_file import find_map_from_wp
from tot_planner import parse_time

bundle_dir = path.abspath(path.dirname(__file__))
cwd = os.getcwd()

is_prod = "_internal" in str(bundle_dir)

data_dir = path.join(bundle_dir, '../data')
routes_dir = path.join(bundle_dir, '../routes')
if is_prod:
    data_dir = path.join(bundle_dir, './data')

def main():
    route_name = sys.argv[1]
    route_file = path.join(routes_dir, f"{route_name}.csv")
    route_folder = f"{routes_dir}/../{route_name}"
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
    if os.path.exists("../" + route_name):
        shutil.rmtree("../" + route_name)
    os.mkdir(f"{routes_dir}/../{route_name}")
    notes_filename = path.join(f"{route_folder}/notes.txt")
    with open(notes_filename, "w") as f:
        f.write(route.write_flight_notes())
    legend_filename = path.join(data_dir, "legend.jpg")
    legend_copy_loc = path.join(f"{route_folder}/legend.jpg")

    shutil.copyfile(legend_filename, legend_copy_loc)
    route.save_boards()

    # shutil.make_archive(path.join(cwd, "../%s_bundle" % route_name), 'zip', path.join(cwd, "../%s" % route_name))
    shutil.make_archive(path.join(cwd, f"./{route_name}_bundle"), 'zip', route_folder)

    # shutil.move(path.join(cwd, "../%s_bundle.zip" % route_name), path.join(cwd, "../%s/%s_bundle.zip" % (route_name, route_name)))
    shutil.move(path.join(cwd, f"./{route_name}_bundle.zip"),
                path.join(f"{route_folder}/{route_name}_bundle.zip"))


if __name__ == '__main__':
    main()
