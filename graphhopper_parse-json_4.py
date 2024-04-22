import requests
import urllib.parse
import folium
import polyline
import sys
import os

route_url = "https://graphhopper.com/api/1/route?"
loc1 = "Washington, D.C."
loc2 = "Baltimore, Maryland"
key = "1ec33ae9-33e3-4f60-8585-71b11339918d"


def generate_osm_link(lat, lng):
    return f"https://www.openstreetmap.org/?mlat={lat}&mlon={lng}&zoom=12"


def geocoding(location, key):
    while location == "":
        location = input("Enter the location again: ")
    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode(
        {"q": location, "limit": "1", "key": key}
    )
    replydata = requests.get(url)
    json_data = replydata.json()
    json_status = replydata.status_code
    print("Geocoding API URL for " + location + ":\n" + url)
    if json_status == 200 and len(json_data["hits"]) != 0:
        lat = json_data["hits"][0]["point"]["lat"]
        lng = json_data["hits"][0]["point"]["lng"]
        name = json_data["hits"][0]["name"]
        value = json_data["hits"][0]["osm_value"]
        if "country" in json_data["hits"][0]:
            country = json_data["hits"][0]["country"]
        else:
            country = ""
        if "state" in json_data["hits"][0]:
            state = json_data["hits"][0]["state"]
        else:
            state = ""
        if len(state) != 0 and len(country) != 0:
            new_loc = name + ", " + state + ", " + country
        elif len(state) != 0:
            new_loc = name + ", " + country
        else:
            new_loc = name
            print(
                "Geocoding API URL for "
                + new_loc
                + " (Location Type: "
                + value
                + ")\n"
                + url
            )
    else:
        lat = "null"
        lng = "null"
        new_loc = location
        if json_status != 200:
            print(
                "Geocode API status: "
                + str(json_status)
                + "\nError message: "
                + json_data["message"]
            )
    return json_status, lat, lng, new_loc


def calculate_midpoint(coord1, coord2):
    mid_lat = (coord1[0] + coord2[0]) / 2
    mid_lng = (coord1[1] + coord2[1]) / 2
    return mid_lat, mid_lng


while True:
    waypoints = input("Do you want to display waypoints? (yes/no): ")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    print("Vehicle profiles available on Graphhopper:")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    print("car, bike, foot")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    profile = ["car", "bike", "foot"]
    vehicle = input("Enter a vehicle profile from the list above: ")
    if vehicle == "quit" or vehicle == "q":
        break
    elif vehicle in profile:
        vehicle = vehicle
    else:
        vehicle = "car"
        print("No valid vehicle profile was entered. Using the car profile.")
    loc1 = input("Starting Location: ")
    if loc1 == "quit" or loc1 == "q":
        break
    orig = geocoding(loc1, key)
    print(orig)
    loc2 = input("Destination: ")
    if loc2 == "quit" or loc2 == "q":
        break
    dest = geocoding(loc2, key)
    print("=================================================")
    if orig[0] == 200 and dest[0] == 200:
        op = f"&point={orig[1]},{orig[2]}"  # Origin point
        dp = f"&point={dest[1]},{dest[2]}"  # Destination point

        route_coordinates = [(orig[1], orig[2]), (dest[1], dest[2])]
        midpoint = calculate_midpoint((orig[1], orig[2]), (dest[1], dest[2]))
        mp = f"&point={midpoint[0]},{midpoint[1]}"  # Midpoint (checkpoint)

        route_coordinates = [(orig[1], orig[2]), (dest[1], dest[2])]
        route_points = ""
        for lat, lng in route_coordinates:
            route_points += f"&point={lat}%2C{lng}"

        full_route_osm_link = f"https://www.openstreetmap.org/directions?{route_points}&route={orig[1]}%2C{orig[2]}%3B{dest[1]}%2C{dest[2]}"

        paths_url = (
            route_url
            + urllib.parse.urlencode(
                {"key": key, "profile": vehicle, "optimize": "true"}
            )
            + op
            + mp
            + dp
        )
        paths_status = requests.get(paths_url).status_code
        paths_data = requests.get(paths_url).json()

        if "paths" in paths_data:
            # Extract polyline points
            encoded_points = paths_data["paths"][0]["points"]

            # Decode polyline points
            decoded_points = polyline.decode(encoded_points)

            # Create map
            mymap = folium.Map(
                location=[decoded_points[0][0], decoded_points[0][1]], zoom_start=15
            )

            # Add polyline to represent the route
            folium.PolyLine(locations=decoded_points, color="blue").add_to(mymap)

        # Add markers for waypoints
            if waypoints == "yes":
                for point in decoded_points:
                    folium.Marker(location=[point[0], point[1]]).add_to(mymap)

            # Add special marker for the midpoint
            folium.Marker(
                location=[midpoint[0], midpoint[1]],
                popup="Midpoint",
                icon=folium.Icon(color="green"),
            ).add_to(mymap)

            # Add instructions as popups
            for instruction in paths_data["paths"][0]["instructions"]:
                folium.Marker(
                    location=[
                        decoded_points[instruction["interval"][0]][0],
                        decoded_points[instruction["interval"][0]][1],
                    ],
                    popup=instruction["text"],
                    icon=folium.Icon(color="red", icon="info-sign"),
                ).add_to(mymap)

            # Save the map to an HTML file
            mymap.save("route_map_with_instructions.html")
            if sys.platform.startswith("win"):
                os.system(f"start route_map_with_instructions.html")
            else:
                os.system(f"open route_map_with_instructions.html")

            print(
                "Routing API Status: "
                + str(paths_status)
                + "\nRouting API URL:\n"
                + paths_url
            )
            print("=================================================")
            print("Directions from " + orig[3] + " to " + dest[3] + " by " + vehicle)
            print("=================================================")
            if paths_status == 200:
                miles = (paths_data["paths"][0]["distance"]) / 1000 / 1.61
                km = (paths_data["paths"][0]["distance"]) / 1000
                sec = int(paths_data["paths"][0]["time"] / 1000 % 60)
                min = int(paths_data["paths"][0]["time"] / 1000 / 60 % 60)
                hr = int(paths_data["paths"][0]["time"] / 1000 / 60 / 60)
                print("Distance Traveled: {0:.1f} miles / {1:.1f} km".format(miles, km))
                print("Trip Duration: {0:02d}:{1:02d}:{2:02d}".format(hr, min, sec))
                print("=================================================")
                for each in range(len(paths_data["paths"][0]["instructions"])):
                    path = paths_data["paths"][0]["instructions"][each]["text"]
                    distance = paths_data["paths"][0]["instructions"][each]["distance"]
                    print(
                        "{0} ( {1:.1f} km / {2:.1f} miles )".format(
                            path, distance / 1000, distance / 1000 / 1.61
                        )
                    )
                    print("=================================================")
            else:
                print("Error message: " + paths_data["message"])
                print("*************************************************")
            orig_osm_link = generate_osm_link(orig[1], orig[2])
            dest_osm_link = generate_osm_link(dest[1], dest[2])

            print("=================================================")
            print("OpenStreetMap link for starting point:", orig_osm_link)
            print("OpenStreetMap link for destination point:", dest_osm_link)
            print("=================================================")
            print("OpenStreetMap link for the entire route:", full_route_osm_link)