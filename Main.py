from flask import Flask, request, jsonify
import Requester

app = Flask(__name__)
headers = {'Access-Control-Allow-Origin': '*'}


@app.route('/')
@app.route('/getPokemonByPage', methods=['GET'])
def get_pokemon_by_page():
    page = request.args.get('page')
    json = {'Error': 'Invalid page number'}
    status_code = 400
    if page.isdigit():
        json = Requester.get_pokemon_by_page(int(page))
        status_code = 200
    response = jsonify(json)
    response.status_code = status_code
    return response, headers


@app.route('/updateDatabaseRegisters', methods=['GET'])
def update_database_registers():
    args = request.args
    result = Requester.update_database_registers(args.get('username'), args.get('password'))
    response = jsonify(result[0])
    response.status_code = result[1]
    return response


if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0')
