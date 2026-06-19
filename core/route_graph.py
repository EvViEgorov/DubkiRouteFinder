import json
from datetime import datetime, timedelta


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

    # Определение времени ожидания транспорта (если есть расписание)
    def schedule_wait_time(self, cur_time, leg_start, leg_end):
        # если нет раписания - возвращаем default = 0 (например для leg'ов пешкоым)
        return 0

    # АЛГОРИТМ ДЕЙКСТРЫ
    def get_fastest(
            self,
            start,
            end,
            cur_time: datetime = datetime.now()
    ):
        # Инициализируем словарь расстояний от start бесконечностями; для вершины start - нулевое расстояние
        dists = {node: float('inf') for node in self.edges}
        dists[start] = 0
        # Собираем список уже посещённых вершин
        visited = set()
        # Пишем родителей каждой вершины
        parents = {node: None for node in self.edges}

        # Цикл алгоритма Дейкстры
        while True:
            # Обнуляем текущий узел и расстояние (задаём бесконечность)
            cur_node = None
            cur_min_dist = float('inf')
            # Линейным поиском (O(n)) делаем текущей вершину с минимальным расстоянием от start
            for node in self.edges:
                if node not in visited and dists[node] < cur_min_dist:
                    cur_min_dist = dists[node]
                    cur_node = node

            # Выходим из цикла если достигли целевой вершины или уже посетили все
            if cur_node is None or cur_node == end:
                break

            # Помечаем cur_node посещенным
            visited.add(cur_node)

            # Считаем расстояния до непосещенных соседей
            for nbr, leg_time in self.edges[cur_node]:
                if nbr not in visited:
                    # Для наземного транспорта добавляем время ожидания ближайшего рейса
                    mins_enroute = dists[cur_node] # минут в пути
                    time_on_nbr = cur_time + timedelta(minutes=mins_enroute) # время в которое мы окажемся в этой точке
                    wait_time = self.schedule_wait_time(time_on_nbr, cur_node, nbr) # время ожидания транспорта
                    new_dist = mins_enroute + wait_time + leg_time
                    # Если новое время меньше старого - обновляем расстояние и маршрут
                    if new_dist < dists[nbr]:
                        dists[nbr] = new_dist
                        parents[nbr] = cur_node

        # Не нашли маршрута - ничего не возвращаем
        if dists[end] == float('inf'):
            return None

        # Идем в обратную сторону по родителям и возвращаем маршрут
        path = []
        cur_node = end
        while cur_node is not None: # останавливаемся когда достигнем стартовой вершины
            path.append(cur_node)
            cur_node = parents[cur_node]
        path.reverse() # разворачиваем назад

        # Пишем маршрут именами
        id_to_name = {node[0]: node[1] for node in self.nodes}
        path_names = [id_to_name[pid] for pid in path]

        total_travel_time = dists[end]
        arrival_time = cur_time + timedelta(minutes=total_travel_time)

        return {
            "path": path_names,
            "total_time_min": total_travel_time,
            "arrival_time": arrival_time
        }

    # ТУТ ПРОПИСАТЬ ВОЗВРАТНЫЙ ПОИСК В ГЛУБИНУ ВСЕХ ВОЗМОЖНЫХ
    def get_all_routes(self, start, end):
        pass