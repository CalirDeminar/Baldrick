# Dead Reckoning Kneeboard Generator

A tool for flight-simmers to turn a flight route in a CSV file into a set of kneeboard images containing:
- Leg Headings
- Timings for each leg
- Distances for each leg
- Speeds

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
- Any additional tags for this waypoint

Tags for a waypoint can be:
- *Some Positive Integer* - Minimum terrain altitude for leg
- TGT - marks the waypoint as the target. This is what the time on target calculations will aimed to get to on time
- IP - marks the waypoint as the IP
- FI - Fence In - TBI
- FO - Fence Out - TBI
- FIX - Navigation fix point - TBI
- MAGVAR*+/- some decimal* - e.g. `MAGVAR-1.2` - The magnetic declination for this waypoint.
    The first of these tags will be used as the magnetic declination for the route. If not set will default to 0.0

### Command Arguments
An example calling of the tool looks like `baldrick test 00:30:00`
The arguments are:
- Route Name
- Optional: start time in hours:minutes:seconds
    - if not included defaults to 00:00:00
- Optional: ToT in hours:minutes:seconds
    - if not included defaults the speed to 430kts and sets leg times to hold that speed

If successful the tool will output the kneeboards in a folder with the same name as the route name specified