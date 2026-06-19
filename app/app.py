from flask import Flask, request, render_template

from core.square import get_square

app = Flask(__name__)

@app.route('/square', methods=['GET'])
def squarenumber():
    num = request.args.get('num')

    if num is None:
        return render_template('squarenum.html')
    elif num.strip() == '':
        return "<h1>Invalid number. Please enter a number.</h1>"
    try:
        square = get_square(num)
        return render_template('answer.html', squareofnum=square, num=num)
    except ValueError:
        return "<h1>Invalid input. Please enter a valid number.</h1>"