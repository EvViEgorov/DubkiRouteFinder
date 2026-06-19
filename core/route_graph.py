import json
from datetime import datetime


# маршрутная сеть в виде графа
class RouteNetwork:
    def __init__(self, datafile):
        # читаем файл с информацией
        with open(datafile, 'r', encoding='UTF-8') as f:
            data = json.load(f)
            N = len(data["nodes"])

        self.nodes = []
        self.edges = {}

        # записываем из файла все узлы
        for n in data["nodes"]:
            self.nodes.append(n)
            # для каждого узла сразу создаем список потенциальных ребер
            self.edges[n[0]] = []
        # записываем из файла все рёбра
        for e in data["connections"]:
            start, end, time = e
            self.edges[start].append((end, time))
            self.edges[end].append((start, time))

    # ТУТ ПРОПИСАТЬ АЛГОРИТМ ДЕЙКСТРЫ
    def get_fastest(self, start, end, cur_time):
        return 31 # ВРЕМЕННО

    # ТУТ ПРОПИСАТЬ ВОЗВРАТНЫЙ ПОИСК В ГЛУБИНУ ВСЕХ ВОЗМОЖНЫХ
    def get_all_routes(self, start, end):
        pass