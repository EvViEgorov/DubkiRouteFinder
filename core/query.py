from pathlib import Path
from datetime import datetime
from core.route_graph import RouteNetwork

BASE_DIR      = Path(__file__).resolve().parent.parent
DATA_PATH     = BASE_DIR / "data" / "connections_data.json"
SCHEDULE_PATH = BASE_DIR / "data" / "schedules.json"


def get_sorted_routes(
    start: int,
    end: int,
    dep_time: datetime,
    less_outside: int,
) -> list[tuple]:

    # возвращает все маршруты из start в end, отсортированные по критерию, отмеченному пользователем
    # маршрут - это кортеж (path_names, time_enroute_min, street_time_min, arrival_str),
    # где path_names — список пар [id, name] (узлы пути).

    # создаем экземпляр маршрутной сети и выполняем по ней поиск
    network = RouteNetwork(DATA_PATH, SCHEDULE_PATH)
    all_routes = network.get_all_routes(start, end, dep_time)

    if less_outside == 1:
        # сортировка: сначала минимум времени на улице, потом общее время
        all_routes.sort(key=lambda r: (r[2], r[1]))
    else:
        # сортировка: сначала минимум общего времени, потом время на улице
        all_routes.sort(key=lambda r: (r[1], r[2]))

    return all_routes