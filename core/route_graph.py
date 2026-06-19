import json


# маршрутная сеть в виде графа
class RouteNetwork:
    def __init__(self, datafile):
        # читаем файл с информацией
        with open(datafile, 'r', encoding='UTF-8') as f:
            data = json.load(f)
            N = len(data["nodes"])

        self.nodes = []
        self.edges = {}

        # записываем все узлы
        for n in data["nodes"]:
            self.nodes.append(n)
            self.edges[n[0]] = []
        # записываем все ребра
        for e in data["connections"]:
            start, end, time = e
            # пишем ребро в массив рёбер для каждой вершины
            self.edges[start].append((end, time))
            self.edges[end].append((start, time))

    # ТУТ ПРОПИСАТЬ АЛГОРИТМ ДЕЙКСТРЫ
    def get_fastest(self, start, end):
        return 31 # ВРЕМЕННО

    # ТУТ ПРОПИСАТЬ ВОЗВРАТНЫЙ ПОИСК В ГЛУБИНУ ВСЕХ ВОЗМОЖНЫХ
    def get_all_routes(self, start, end):
        pass