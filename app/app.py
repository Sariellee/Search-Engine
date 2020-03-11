import json

from flask import Flask, request

from app.search_engine.query import QueryProcessor

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return json.dumps({'prompt': 'search'})


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    result = query_processor.search(query)
    return json.dumps({'result': result})


@app.route('/retrieve', methods=['GET'])
def retrieve():
    article_title = request.args.get('title')
    result = query_processor._index.get_from_full_collection(article_title)
    return json.dumps({'result': result})


@app.before_first_request
def before_script():
    global query_processor
    query_processor = QueryProcessor()


if __name__ == '__main__':
    app.run()
