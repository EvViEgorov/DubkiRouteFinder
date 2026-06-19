# ТЕСТОВЫЙ ФАЙЛ
from pathlib import Path

from core.route_graph import RouteNetwork


# пути до файлов
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "connections_data.json"

# проверка, что функция вообще работает
def test_find_route():
    G = RouteNetwork(str(DATA_PATH))
    routes = G.get_all_routes(0, 9, None)  # пример: от 0 до 9
    print(routes)

test_find_route()