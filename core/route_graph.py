import json
from calendar import weekday
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
            start, end, time, street_time = e
            self.edges[start].append((end, time, street_time))
            self.edges[end].append((start, time, street_time))

        # подгружаем расписание
        with open(schedulefile, 'r', encoding='UTF-8') as f:
            schedule_data = json.load(f)

        self.schedules = schedule_data

    # определение времени ожидания транспорта (если есть расписание): O(k)
    def schedule_wait_time(self, cur_time, leg_start, leg_end):
        # ключ для поиска по словарям
        leg_key = "-".join([str(leg_start), str(leg_end)])

        # если нет раcписания - возвращаем default = 0 (например для leg'ов пешком)
        if leg_key not in self.schedules:
            return 0

        leg_info = self.schedules[leg_key]

        # метро и МЦД ночью не выдаются
        if leg_info.get("type") in ("metro", "mcd"):
            cur_mins = cur_time.hour * 60 + cur_time.minute
            night_start = 1 * 60        # 1:00
            night_end = 5 * 60 + 30     # 5:30

            # если ночь - возвращаем wait_time до открытия метро
            if night_start <= cur_mins < night_end:
                return night_end - cur_mins
            # рабочее время метро/МЦД - считаем, что ждать не нужно
            return 0

        # берем расписание для нужного дня недели. у дубовозок суббота - будний день
        day_type = "weekday" if cur_time.weekday() < 6 else "weekend"
        schedule_list = self.schedules[leg_key].get(day_type, [])
        if not schedule_list: # если его нет - возвращаем 0
            return 0

        # текущее время переводим в минуты для удобного сравнения
        cur_mins = cur_time.hour * 60 + cur_time.minute

        # инициализируем время ожидания
        for time_str in schedule_list:
            # строку переводим в минуты для удобного сравнения
            h, m = map(int, time_str.split(':'))
            dep_mins = h * 60 + m

            # ищем дельту
            wait = dep_mins - cur_mins
            # выбираем первый маршрут с неотрицательной дельтой (расписание и так сортированное)
            if wait >= 0:
                return wait

        # если не нашлось рейсов в этот день, то смотрим завтра
        time_till_midnight = 24 * 60 - cur_mins

        # смотрим завтрашний день недели
        next_weekday = (cur_time.weekday() + 1) % 7
        next_day_type = "weekday" if next_weekday < 6 else "weekend"
        next_schedule_list = self.schedules[leg_key].get(next_day_type, [])
        if not next_schedule_list:
            return float('inf')

        # из завтрашних подойдет самый первый рейс
        first_tomorrow_time = next_schedule_list[0]
        h, m = map(int, first_tomorrow_time.split(':'))
        first_tomorrow_mins = h * 60 + m

        # плюсуем время первого автобуса со вчерашним остатком времени
        wait = time_till_midnight + first_tomorrow_mins
        return wait

    # алгоритм Дейкстры: O(V² + E)
    def get_fastest(
            self,
            start,
            end,
            cur_time: datetime = datetime.now()
    ):
        # инициализируем словарь расстояний от start бесконечностями; для вершины start - нулевое расстояние
        dists = {node: float('inf') for node in self.edges}
        dists[start] = 0
        # собираем список уже посещённых вершин
        visited = set()
        # пишем родителей каждой вершины
        parents = {node: None for node in self.edges}

        # цикл алгоритма Дейкстры:
        while True:
            # обнуляем текущий узел и расстояние (задаём бесконечность)
            cur_node = None
            cur_min_dist = float('inf')
            # линейным поиском (O(n)) делаем текущей вершину с минимальным расстоянием от start
            for node in self.edges:
                if node not in visited and dists[node] < cur_min_dist:
                    cur_min_dist = dists[node]
                    cur_node = node

            # выходим из цикла если достигли целевой вершины или уже посетили все
            if cur_node is None or cur_node == end:
                break

            # помечаем cur_node посещенным
            visited.add(cur_node)

            # считаем расстояния до непосещенных соседей
            for nbr, leg_time, street_time in self.edges[cur_node]:
                if nbr not in visited:
                    # для наземного транспорта добавляем время ожидания ближайшего рейса
                    mins_enroute = dists[cur_node] # минут в пути
                    time_on_nbr = cur_time + timedelta(minutes=mins_enroute) # время в которое мы окажемся в этой точке
                    wait_time = self.schedule_wait_time(time_on_nbr, cur_node, nbr) # время ожидания транспорта
                    new_dist = mins_enroute + wait_time + leg_time
                    # если новое время меньше старого - обновляем расстояние и маршрут
                    if new_dist < dists[nbr]:
                        dists[nbr] = new_dist
                        parents[nbr] = cur_node

        # не нашли маршрута - ничего не возвращаем
        if dists[end] == float('inf'):
            return None

        # идем в обратную сторону по родителям и возвращаем маршрут
        path = []
        cur_node = end
        while cur_node is not None: # останавливаемся когда достигнем стартовой вершины
            path.append(cur_node)
            cur_node = parents[cur_node]
        path.reverse()

        # пишем маршрут именами
        id_to_name = {node[0]: node[1] for node in self.nodes}
        path_names = [id_to_name[pid] for pid in path]

        total_travel_time = dists[end]
        arrival_time = cur_time + timedelta(minutes=total_travel_time)

        return {
            "path": path_names,
            "total_time_min": total_travel_time,
            "arrival_time": arrival_time
        }

    # возвратный поиск в глубину для всех возможных: O(V!) / O(2^V) в худшем случае
    def get_all_routes(self, start, end, dep_time):

        all_routes = [] # все найденные маршруты

        def dfs(current, visited, path, total_time, total_street_time):
            # поиск в глубину обход графа в глубину
            # current: текущая вершина
            # visited: множество уже посещенных вершин (чтобы не ходить кругами)
            # path: текущий путь от start до current
            # total_time: суммарное время, потраченное на текущий путь

            # базовый случай: дошли до конечной вершины
            if current == end:
                path_names = [self.nodes[pid] for pid in path]
                # время в пути записываем для удобного сравнения в минутах позже
                time_enroute = (total_time - dep_time).total_seconds() / 60
                # cохраняем копию пути
                all_routes.append((path_names, time_enroute, total_street_time, total_time.strftime("%d.%m %H:%M")))
                return  # возвращаемся, чтобы найти другие маршруты

            # перебираем соседей: смотрим все возможные направления из текущей вершины
            for neighbor, delta, street_time in self.edges[current]:
                if neighbor not in visited: # проверяем, не были ли уже в этой вершине на текущем пути
                    visited.add(neighbor) # отмечаем вершину как посещенную
                    path.append(neighbor) # добавляем в путь

                    # переводим время в timedelta
                    delta = timedelta(minutes=delta)
                    wait_mins = self.schedule_wait_time(total_time, current, neighbor)

                    # если путь уже занимает бесконечно времени - не записываем его
                    if wait_mins == float('inf'):
                        path.pop()
                        visited.remove(neighbor)
                        continue

                    wait_time = timedelta(minutes=wait_mins)
                    new_time = total_time + wait_time + delta

                    # увеличиваем общее время на улице
                    new_total_street_time = total_street_time + street_time

                    # реккурсивное: идем глубже
                    # передаем total_time + time (добавляем время этого перегона)
                    dfs(neighbor, visited, path, new_time, new_total_street_time)

                    # убираем вершину из пути и посещенных => пробовать другие маршруты
                    path.pop()  # убираем последнюю вершину из пути
                    visited.remove(neighbor)  # разотмечаем как посещенную

        # начальные условия для старта поиска
        visited = {start}  # start уже посещен
        path = [start]  # путь начинается со start

        # поиск в грубину от начальной вершины
        dfs(start, visited, path, dep_time, 0)

        return all_routes # возвращаем все найденные маршруты
