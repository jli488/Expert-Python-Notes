from flask import Flask, request


app = Flask(__name__)


@app.route('/')
def echo():
    return (
        f'METHOD: <br>{request.method}<br><br>'
        f'HEADERS: <br>{request.headers}<br><br>'
        f'BODY: <br>{request.data.decode()}<br><br>'
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0')
