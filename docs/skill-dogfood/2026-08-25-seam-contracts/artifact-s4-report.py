"""Print `<station>: <count>` per station read via the seam's shared parser."""
import os
from stations_parser import load_stations

if __name__ == "__main__":
    path = os.path.join(os.path.dirname(__file__), "stations.json")
    for record in load_stations(path):
        print(f"{record['station']}: {record['count']}")
