from flask import Flask, request, render_template
from datetime import datetime

from core.query import get_sorted_routes

app = Flask(__name__)

# словарь: название остановки - id узла в графе
STOP_NAME_TO_ID = {
    "Дубки":                    0,
    "Дубки-остановка":          1,
    "Одинцово-остановка":       2,
    "Одинцово-МЦД":             3,
    "Славянский Бульвар-МЦД":   4,
    "Славянский Бульвар-остановка": 5,
    "Славянский Бульвар-метро": 6,
    "Молодежная-остановка":     7,
    "Молодежная-метро":         8,
    "Курская-метро":            9,
    "Курская-МЦД":              10,
    "Крылатское-метро":         11,
    "Крылатское-остановка":     12,
    "Басмач":                   13,
    "Лесной городок":           14,
}


@app.route('/')
def index():
    # главная страница
    return render_template('index.html')


@app.route('/results', methods=['POST'])
def results():
    # обрабатывает форму и возвращает найденные маршруты. получает  from, to, time, less_outdoor (1, если отмечено)
    # передает routes как список маршрутов со структурой (path_names, time_enroute_min, street_time_min, arrival_str), from_name, to_name
    # dep_time_str (для отображения)
    from_name = request.form.get('from', '').strip()
    to_name   = request.form.get('to', '').strip()
    time_str  = request.form.get('time', '').strip()
    less_outdoor = 1 if request.form.get('less_outdoor') == '1' else 0

    # парсим время отправления
    now = datetime.now()
    if time_str:
        try:
            # сегодняшняя дата + введённое время
            dep_time = now.replace(
                hour=int(time_str.split(':')[0]),
                minute=int(time_str.split(':')[1]),
                second=0, microsecond=0
            )
        except (ValueError, IndexError):
            dep_time = now  # некорректный ввод, значит, используем текущее время
    else:
        dep_time = now

    dep_time_str = dep_time.strftime('%H:%M')

    # получаем id узлов и запускаем поиск

    start_id = STOP_NAME_TO_ID[from_name]
    end_id   = STOP_NAME_TO_ID[to_name]

    # get_sorted_routes возвращает список кортежей:
    # (path_names, time_enroute_min, street_time_min, arrival_str)
    routes = get_sorted_routes(start_id, end_id, dep_time, less_outdoor)[:5]

    return render_template(
        'results.html',
        routes=routes,
        from_name=from_name,
        to_name=to_name,
        dep_time_str=dep_time_str,
    )
