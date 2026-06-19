import json
from datetime import datetime, timedelta


# маршрутная сеть в виде графа
class RouteNetwork:
    def __init__(self, datafile, schedulefile):
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
            start, end, time, _ = e
            self.edges[start].append((end, time))
            self.edges[end].append((start, time))

        # подгружаем расписание
        with open(schedulefile, 'r', encoding='UTF-8') as f:
            schedule_data = json.load(f)

        self.schedules = schedule_data

    # Определение времени ожидания транспорта (если есть расписание)
    def schedule_wait_time(self, cur_time, leg_start, leg_end):
        # ключ для поиска по словарям
        leg_key = "-".join([str(leg_start), str(leg_end)])

        # если нет раcписания - возвращаем default = 0 (например для leg'ов пешком)
        if leg_key not in self.schedules:
            return 0

        # берем расписание для нужного дня недели. У дубовозок суббота - рабочий
        day_type = "weekday" if cur_time.weekday() < 6 else "weekend"
        schedule_list = self.schedules[leg_key].get(day_type, [])
        if not schedule_list: # если его нет - возвращаем 0
            return 0

        # текущее время переводим в минуты для удобного сравнения
        cur_mins = cur_time.hour * 60 + cur_time.minute

        # инициализируем время ожидания
        for time_str in schedule_list:
            # Строку переводим в минуты для удобного сравнения
            h, m = map(int, time_str.split(':'))
            dep_mins = h * 60 + m

            # Ищем дельту
            wait = dep_mins - cur_mins
            # Выбираем первый маршрут с неотрицательной дельтой (раписание и так сортированное)
            if wait >= 0:
                return wait

        # Если не нашлось рейсов в этот день, то смотрим завтра
        return float('inf')

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
    def get_all_routes(self, start, end, dep_time):

        all_routes = [] # Сюда будем собирать все найденные маршруты

        def dfs(current, visited, path, total_time):
            # поиск в глубину обход графа в глубину
            # current: текущая вершина
            # visited: множество уже посещенных вершин (чтобы не ходить кругами)
            # path: текущий путь от start до current
            # total_time: суммарное время, потраченное на текущий путь

            # базовый случай: дошли до конечной вершины
            if current == end:
                # cохраняем копию пути
                all_routes.append((path.copy(), total_time.strftime("%d.%m %H:%M:%S")))
                return  # возвращаемся, чтобы найти другие маршруты

            # перебираем соседей: смотрим все возможные направления из текущей вершины
            for neighbor, delta in self.edges[current]:
                if neighbor not in visited: # проверяем, не были ли уже в этой вершине на текущем пути
                    visited.add(neighbor) # отмечаем вершину как посещенную
                    path.append(neighbor) # добавляем в путь

                    # переводим время в timedelta
                    delta = timedelta(minutes=delta)
                    wait_mins = self.schedule_wait_time(total_time, path[-1], neighbor)
                    wait_time = timedelta(minutes=wait_mins)

                    # реккурсивное: идем глубже
                    # передаем total_time + time (добавляем время этого перегона)
                    dfs(neighbor, visited, path, total_time + wait_time + delta)

                    # убираем вершину из пути и посещенных => пробовать другие маршруты
                    path.pop()  # убираем последнюю вершину из пути
                    visited.remove(neighbor)  # разотмечаем как посещенную

        # начальные условия для старта поиска
        visited = {start}  # start уже посещен
        path = [start]  # путь начинается со start

        # поиск в грубину от начальной вершины
        dfs(start, visited, path, dep_time)

        return all_routes # возвращаем все найденные маршруты
