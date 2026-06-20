from flask import Flask, request, render_template

from core.route_finder import get_nodes

app = Flask(__name__)
@app.route('/')
def routes_data():
    return render_template('index.html')
@app.route('/results', methods=['POST'])
def results():
    from_stop = request.form.get('from')
    to_stop = request.form.get('to')
    custom_time = request.form.get('time')

    departure_time = custom_time if custom_time else "сейчас"

    result = {"from": from_stop, "to": to_stop, "departure_time": departure_time, "route": []}

    return render_template('results.html', result=result)
