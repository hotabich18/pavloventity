from app import app, db
import json
from threading import Thread
from runner import rest1, rest2, server
from flask import render_template, request
from app.models import TokenType, LearnSentence
from app.forms import AddType

# with app.app_context():
#     db.create_all()

# Токены по умолчанию
tokensType = [
    {'name': 'PERSON', 'b': 'B-PERSON', 'i': 'I-PERSON', 'color': 'RoyalBlue', 'description': 'Люди, в том числе и вымышленные'},
    {'name': 'ORG', 'b': 'B-ORG', 'i': 'I-ORG', 'color': 'DarkTurquoise', 'description': 'Компании, агенства, учреждения и '
                                                                                   'тд.'},
    {'name': 'LOC', 'b': 'B-LOC', 'i': 'I-LOC', 'color': 'LimeGreen', 'description': 'Место'},
    {'name': 'DATE', 'b': 'B-DATE', 'i': 'I-DATE', 'color': 'Black', 'description': 'Абсолютная или относительная дата или '
                                                                             'период'},
    {'name': 'MONEY', 'b': 'B-MONEY', 'i': 'I-MONEY', 'color': 'Gray', 'description': 'Денежная единица'},
    {'name': 'NORP', 'b': 'B-NORP', 'i': 'I-NORP', 'color': 'FireBrick', 'description': 'Национальность, религия или '
                                                                                 'политическая '
                                                                                 'группа'},
    {'name': 'GPE', 'b': 'B-GPE', 'i': 'I-GPE', 'color': 'Gold', 'description': 'Страны, города, штаты'},
    {'name': 'FAC', 'b': 'B-FAC', 'i': 'I-FAC', 'color': 'Maroon', 'description': 'Здания, аеропорты, дороги, мосты и тд'},
    {'name': 'PRODUCT', 'b': 'B-PRODUCT', 'i': 'I-PRODUCT', 'color': 'Chocolate', 'description': 'Объекты, машины, еда и тд'},
    {'name': 'EVENT', 'b': 'B-EVENT', 'i': 'I-EVENT', 'color': 'MidnightBlue', 'description': 'Именные ураганы, сражения, '
                                                                                      'спортивные '
                                                                                      'события и тд'},
    {'name': 'WORK_OF_ART', 'b': 'B-WORK_OF_ART', 'i': 'I-WORK_OF_ART', 'color': 'DarkGreen',
     'description': 'Названия книг, песен и тд'},
    {'name': 'LAW', 'b': 'B-LAW', 'i': 'I-LAW', 'color': 'HotPink', 'description': 'Нормативно-правовые акты'},
    {'name': 'LANGUAGE', 'b': 'B-LANGUAGE', 'i': 'I-LANGUAGE', 'color': 'SteelBlue', 'description': 'Язык'},
    {'name': 'TIME', 'b': 'B-TIME', 'i': 'I-TIME', 'color': 'DarkOliveGreen', 'description': 'Время, которое меньше дня'},
    {'name': 'PERCENT', 'b': 'B-PERCENT', 'i': 'I-PERCENT', 'color': 'Khaki', 'description': 'Процент'},
    {'name': 'QUANTITY', 'b': 'B-QUANTITY', 'i': 'I-QUANTITY', 'color': 'Red', 'description': 'Единица имерения, например вес '
                                                                                   'или длина'},
    {'name': 'ORDINAL', 'b': 'B-ORDINAL', 'i': 'I-ORDINAL', 'color': 'DarkBlue', 'description': 'Первый, второй и тд'},
    {'name': 'CARDINAL', 'b': 'B-CARDINAL', 'i': 'I-CARDINAL', 'color': 'DarkBlue',
     'description': 'Числа, которые не попадают ни в '
                    'одну категорию'},
    {'name': 'ARM', 'b': 'B-ARM', 'i': 'I-ARM', 'color': 'Aqua', 'description': 'Вооружение РФ'}
]
#Добавить токены в бд
def fillTypes():
    for t in tokensType:
        type = TokenType(name=t['name'], i=t['i'], b=t['b'], color=t['color'], description=t['description'])
        db.session.add(type)
    db.session.commit()

# Формирование результатов работы нейронной сети (вход: текст, который будет разделен на сущности)
@app.route('/', methods=['POST', 'GET'])
def test():
    if request.method == 'POST':
        text = request.form.get('content_news') # текст, который будет разделен на сущности
        textList = server.devText(text) # Список абзацев
        textListArray = server.devSentenses(textList) # Список предложений по абзацам
        resArray = [] # Массив со словами и токенами, разделенные на предложения и абзацы
        for paragraph in textListArray:
            resArray.append(server.devParagraphREST(paragraph))
        tokensType = db.session.query(TokenType).all() # получение списка сущностей из базы данных
        html = server.reshtml(resArray, tokensType) # размеченный html код текста с сущностями
        return render_template('test.html', textarray=resArray, types=tokensType, entitytext=html)
    else:
        return render_template('test.html')

# Функция отправки исправленного предложения в промежуточную базу данных переобучения нейронной сети
@app.route('/sendwords', methods=['POST'])
def sendwords():
    data = request.form['data']
    print(data)
    json_obj = json.loads(data)
    print(json_obj)
    correct = server.correctJsonString(json_obj)
    sentence = LearnSentence(sentence=correct)

    # Чтобы сохранить наш объект ClassName, мы добавляем его в наш сессию:
    db.session.add(sentence)
    db.session.commit()
    return json.dumps({'status': 'OK'})

@app.route('/types', methods=['POST', 'GET'])
def types():
    form = AddType()
    if request.method == 'POST':
        if form.validate_on_submit():
            name = form.name.data
            color = form.color.data
            description = form.description.data
            b = f'B-{name}'
            i = f'I-{name}'
            type = TokenType(name=name, i=i, b=b, color=color, description=description)
            db.session.add(type)
            db.session.commit()
            tokensType = db.session.query(TokenType).all()
            return render_template('types.html', types=tokensType, form=form)
        index = request.form['index']
        if "delete_" in index:
            TokenType.query.filter(TokenType.id == index.replace("delete_", "")).delete()
            db.session.commit()
    tokensType = db.session.query(TokenType).all()
    return render_template('types.html', types=tokensType, form=form)

@app.route('/learn')
def learn():
    learnSentences = db.session.query(LearnSentence).all()
    return render_template('learn.html', learnSentences=learnSentences)

@app.route('/admin', methods=['post', 'get'])
def admin():
    if request.method == 'POST':
        index = request.form['index']
        if(index == 'restart1'):
            rest1.restart()
        if (index == 'restart2'):
            rest2.restart()
        if (index == 'start1'):
            if rest1.status: rest1.stop()
            else: rest1.start()
        if (index == 'start2'):
            if rest2.status:
                rest2.stop()
            else:
                rest2.start()
        if (index == 'train'):
            server.thread = Thread(target=server.train)
            server.thread.start()
        if (index == 'stoptrain'):
            try:
                server.stoptrain()
                server.thread.join()
            except:
                pass
        if (index == "save_model"):
            model_name = request.form.get('model_name')
            server.savemodel(model_name)
        if "delete_" in index:
            server.deletemodel(index.replace('delete_', ''))
        if "load_" in index:
            server.loadmodel(index.replace('load_', ''))
    return render_template('control.html', trainstatus = server.serverstatus, trainstatustext = server.serverstatustext, reststatus1 = rest1.status, reststatus2 = rest2.status, models = server.getmodels())
