# ТЕСТОВЫЙ ФАЙЛ
from pathlib import Path

from core.route_graph import RouteNetwork


# пути до файлов
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "connections_data.json"


# проверка, что функция вообще работает
def test_find_route():
    # создаем объект класса
    G = RouteNetwork(DATA_PATH)
    print(G.nodes)


print(test_find_route())