from core.route_graph import RouteNetwork

from pathlib import Path

# пути до файлов
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "connections_data.json"
SCHEDULE_PATH = BASE_DIR / "data" / "schedules.json"

def get_sorted_routes(start, end, dep_time, less_outside):
    routes = RouteNetwork(DATA_PATH, SCHEDULE_PATH)
    all_routes = routes.get_all_routes(start, end, dep_time)

    if less_outside == 1:
        all_routes.sort(key=lambda r: (r[2], r[1]))
    else:
        all_routes.sort(key=lambda r: (r[1], r[2]))

    return all_routes