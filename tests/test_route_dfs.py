# ТЕСТОВЫЙ ФАЙЛ
from datetime import datetime
from pathlib import Path

from core.route_graph import RouteNetwork
from pprint import pprint


# пути до файлов
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "connections_data.json"
SCHEDULE_PATH = BASE_DIR / "data" / "schedules.json"

# проверка, что функция вообще работает
def test_find_route():
    test_time = datetime.now()
    G = RouteNetwork(DATA_PATH, SCHEDULE_PATH)
    routes = G.get_all_routes(0, 13, test_time)  # пример: от 0 до 9
    pprint(routes)

test_find_route()