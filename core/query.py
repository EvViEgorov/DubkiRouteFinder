from pathlib import Path
from datetime import datetime
from core.route_graph import RouteNetwork

BASE_DIR      = Path(__file__).resolve().parent.parent
DATA_PATH     = BASE_DIR / "data" / "connections_data.json"
SCHEDULE_PATH = BASE_DIR / "data" / "schedules.json"

def insertion_sort(items, key=lambda x: x):

    # алгоритм: сортировка вставками (insertion sort), по возрастанию key(x)
    # сортирует список items на месте (in place) и возвращает его же
    # O(n^2) время в худшем/среднем случае, O(n) в лучшем случае;

    for i in range(1, len(items)):
        current = items[i]
        current_key = key(current)
        j = i - 1

        # сдвигаем элементы, которые больше current_key, на одну позицию вправо,
        # освобождая место для вставки current
        while j >= 0 and key(items[j]) > current_key:
            items[j + 1] = items[j]
            j -= 1

        # вставляем current на освободившееся место
        items[j + 1] = current

    return items

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
        insertion_sort(all_routes, key=lambda r: (r[2], r[1]))
    else:
        # сортировка: сначала минимум общего времени, потом время на улице
        insertion_sort(all_routes, key=lambda r: (r[1], r[2]))
    return all_routes