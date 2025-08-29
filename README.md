# Baldrick: Navigation Kneeboard Generator

A tool for flight-simmers to turn a flight route in a CSV file into a set of kneeboard images containing:
- Leg Headings
- Timings for each leg
- Distances for each leg
- Speeds

A legend kneeboard card will also be included, along with an overview card of the entire route,
and all of the above bundled into a zip file for easy sharing before a mission.

## Usage
### Route File
The route file is a CSV in the `./routes` folder
The tool will search for a map file that the starting coordinate of a route falls within. 
If such a map cannot be found the tool will give an error

The columns for each WP are:
- Waypoint Name - any text
- Latitude degrees component
- Latitude minutes component
- Latitude seconds component
- Longitude degrees component
- Longitude minutes component
- Longitude seconds component
- Notes for the leg. Leave empty for no notes
- Any additional tags for this waypoint

Tags for a waypoint can be:
- *Some Positive Integer* - Minimum terrain altitude for leg
- PUSH - marks the waypoint from which the ToT calculations will start. If not included the first WP will be used
- TGT - marks the waypoint as the target. This is what the time on target calculations will aimed to get to on time
- IP - marks the waypoint as the IP
- FIX - Navigation fix point - Automatically includes the coordinates for the fix in the notes for this leg's card
- MAGVAR*+/- some decimal* - e.g. `MAGVAR-1.2` - The magnetic declination for this waypoint.
    The first of these tags will be used as the magnetic declination for the route. If not set will default to 0.0
    
### Config.json
The tool has a number of default values that it uses for certain calculations.
These values can be found in and changed in the config.json
These values are:
- "metric": flags if the tool will read values in and out in metric instead of imperial
- "minCruiseSpeed": The minimum speed the ToT planner will allow a leg to be flown at
- "defaultCruiseSpeed": The default speed of legs if no ToT is specified
- "defaultDashSpeed": The speed that the IP to Target leg will be specified to be flown at
- "overviewCardDownsampleFactor": The amount the overview card will be downsampled in resolution.
This option is intended to allow bundle sizes to be kept reasonable for broad routes
- "routeColour": The hex colour code that drawings on the map will be made in

### Command Arguments
An example calling of the tool looks like `./baldrick test`
The arguments are:
- Route Name
- Optional: start time in hours:minutes:seconds
    - if not included defaults to 00:00:00
- Optional: ToT in hours:minutes:seconds
    - if not included defaults the speed to 430kts and sets leg times to hold that speed

If successful the tool will output the kneeboards in a folder with the same name as the route name specified