from flask import Flask

app = Flask(__name__)
app.static_folder = 'static'


@app.route('/')
def home():

    with open('static/index.html') as index_file:

        return index_file.read()


if __name__ == "__main__":
    app.run(port=8082)
