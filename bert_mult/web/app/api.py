from app import app, db
from app.models import TokenType, LearnSentence
from runner import server
from flask import request, jsonify
from threading import Thread
import json

# Обработка текста нейронной сетью
@app.route('/api/getentity', methods=['POST'])
def getentity():
    req_data = request.get_json(force=True)
    text = req_data['text']
    res = server.getEntityREST(text)
    return jsonify(res)

# Добавить тип сущности в базу данных
@app.route('/api/addentity', methods=['POST'])
def addentity():
    req_data = request.get_json(force=True)
    name = req_data['name']
    i = req_data['i']
    b = req_data['b']
    color = req_data['color']
    description = req_data['description']
    type = TokenType(name=name, i=i, b=b, color=color, description=description)
    db.session.add(type)
    db.session.commit()
    return json.dumps({'status': 'OK'}), 200

# Добавить предложение для переобучения нейронной сети в базу
@app.route('/api/addsentence', methods=['POST'])
def addsentence():
    data = request.get_json(force=True)
    correct = server.correctJsonString(data)
    sentence = LearnSentence(sentence=correct)
    db.session.add(sentence)
    db.session.commit()
    return json.dumps({'status': 'OK'}), 200

# Запуск обучения нейронной сети
@app.route('/api/train', methods=['POST'])
def train():
    if server.serverstatus == False:
        thread = Thread(target=server.train)
        thread.start()
        return json.dumps({'status': 'Train started.'}), 200
    else:
        return json.dumps({'status': f'Server busy. Try later. ({server.serverstatustext})'}), 400

# Сохранить модель с указанным именем
@app.route('/api/savemodel', methods=['POST'])
def savemodel():
    if server.serverstatus == False:
        name = request.args.get("name")
        thread = Thread(target=server.savemodel, args=[name])
        thread.start()
        return json.dumps({'status': 'OK'}), 200
    else:
        return json.dumps({'status': f'Server busy. Try later. ({server.serverstatustext})'}), 400

# Загрузить модель с указанным именем
@app.route('/api/loadmodel', methods=['POST'])
def loadmodel():
    if server.serverstatus == False:
        name = request.args.get("name")
        for model in server.getmodels():
            if name in model['name']:
                thread = Thread(target=server.loadmodel, args=[name])
                thread.start()
                return json.dumps({'status': 'OK'}), 200
        return json.dumps({'status': 'Bad name'}), 400
    else: return json.dumps({'status': f'Server busy. Try later. ({server.serverstatustext})'}), 400

# Удалить модель с указанным именем
@app.route('/api/delmodel', methods=['POST'])
def delmodel():
    if server.serverstatus == False:
        name = request.args.get("name")
        for model in server.getmodels():
            if name in model['name']:
                thread = Thread(target=server.deletemodel, args=[name])
                thread.start()
                return json.dumps({'status': 'OK'}), 200
        return json.dumps({'status': 'Bad name'}), 400
    else:
        return json.dumps({'status': f'Server busy. Try later. ({server.serverstatustext})'}), 400

# Получить данные о статусе сервера
@app.route('/api/getstatus', methods=['POST'])
def getstatus():
    res = server.getstatus()
    return res
