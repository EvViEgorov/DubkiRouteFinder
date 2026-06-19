from pathlib import Path

from core.route_graph import RouteNetwork

# пути до файлов
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "connections_data.json"


def get_nodes():
    # создаем маршрутную сеть
    RN = RouteNetwork(DATA_PATH)
    return(RN.nodes)

# print(get_nodes())