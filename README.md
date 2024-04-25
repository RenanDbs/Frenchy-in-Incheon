# Frenchy-in-Incheon

# Route Planner with GraphHopper API

This Python script interacts with the GraphHopper API to plan routes between two locations. It provides functionalities to geocode addresses, calculate routes, and display them on a map.

## Setup

1. Install required libraries:
   ```bash
   pip install requests folium polyline
   ```
2. Obtain a GraphHopper API key from [GraphHopper](https://www.graphhopper.com/)
3. Replace the key variable in the script with your GraphHopper API key.

## Usage

#### 1. Run the script:
  ```bash
  python route_planner.py
  ```

#### 2. Follow the prompts to enter:
  - Vehicle profile (car, bike, foot)
  - Starting location
  - Destination
  - Whether to avoid tunnels

#### 3. The script will:
- Geocode the locations using the GraphHopper API.
- Calculate the route and display it on an interactive map.
- Provide route details such as distance, duration, and instructions.
- Generate OpenStreetMap links for the starting point, destination, and entire route.

#### 4. Open the generated HTML file (route_map_with_instructions.html) to view the route on the map.

## Notes

- The script uses the requests, folium, and polyline libraries for API requests, map visualization, and polyline decoding, respectively.
- You can customize vehicle profiles and route options through user input.
- Ensure an active internet connection to fetch geocoding and routing data from the GraphHopper API.
