from flask import Flask, request, render_template

from core.route_finder import get_nodes

app = Flask(__name__)

@app.route('/data')
def routes_data():
    return render_template('graph_info.html')

@app.route('/square', methods=['GET'])
def squarenumber():
    num = request.args.get('num')

    if num is None:
        return render_template('squarenum.html')
    elif num.strip() == '':
        return "<h1>Invalid number. Please enter a number.</h1>"
    try:
        square = get_nodes()
        return render_template('answer.html', squareofnum=square, num=num)
    except ValueError:
        return "<h1>Invalid input. Please enter a valid number.</h1>"