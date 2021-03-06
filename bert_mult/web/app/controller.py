import threading
import time
import docker
import json
import os
import requests
import shutil
import ctypes
import math
from random import shuffle
import sqlalchemy.exc
from deeppavlov import configs, train_model, build_model
from nltk.tokenize import sent_tokenize
from sqlalchemy import exc
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator




from app import db, app
from app.models import LearnSentence, TokenType


class Server:
    def __init__(self, rest1, rest2, webpath, deeppavlovpath, savepath, currentpath):
        self.rest1 = rest1
        self.rest2 = rest2
        self.rest = rest1
        self.serverstatus = False
        self.__serverstatustext = "Обучение не производится"
        self.webpath = webpath
        self.deeppavlovpath = deeppavlovpath
        self.savepath = savepath
        self.currentpath = currentpath
        self.thread = None
        if not os.path.exists(f"{deeppavlovpath}/downloads/bert_models/multi_cased_L-12_H-768_A-12/vocab.txt"):
            self.model = build_model("ner_ontonotes_bert_mult", download = True)
        else:
            self.model = build_model("ner_ontonotes_bert_mult", download = False)
        try:
            db.session.query(TokenType).first()
        except sqlalchemy.exc.ProgrammingError:
            with app.app_context():
                db.create_all()
                db.session.commit()
                self.fillTypes()
        if not os.path.exists(f"{currentpath}/downloads/bert_models/multi_cased_L-12_H-768_A-12/vocab.txt"):
            for root, dirs, files in os.walk(self.currentpath):
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))
            for src_dir, dirs, files in os.walk(f"{self.deeppavlovpath}"):
                dst_dir = src_dir.replace(f"{self.deeppavlovpath}", self.currentpath, 1)
                if not os.path.exists(dst_dir):
                    os.makedirs(dst_dir)
                for file_ in files:
                    src_file = os.path.join(src_dir, file_)
                    dst_file = os.path.join(dst_dir, file_)
                    if os.path.exists(dst_file):
                        os.remove(dst_file)
                    shutil.copy(src_file, dst_dir)

    # Добавить токены в бд
    @staticmethod
    def fillTypes():
        # Токены по умолчанию
        tokensType = [
            {'name': 'PERSON', 'b': 'B-PERSON', 'i': 'I-PERSON', 'color': 'RoyalBlue',
             'description': 'Люди, в том числе и вымышленные'},
            {'name': 'ORG', 'b': 'B-ORG', 'i': 'I-ORG', 'color': 'DarkTurquoise',
             'description': 'Компании, агенства, учреждения и '
                            'тд.'},
            {'name': 'LOC', 'b': 'B-LOC', 'i': 'I-LOC', 'color': 'LimeGreen', 'description': 'Место'},
            {'name': 'DATE', 'b': 'B-DATE', 'i': 'I-DATE', 'color': 'Black',
             'description': 'Абсолютная или относительная дата или '
                            'период'},
            {'name': 'MONEY', 'b': 'B-MONEY', 'i': 'I-MONEY', 'color': 'Gray', 'description': 'Денежная единица'},
            {'name': 'NORP', 'b': 'B-NORP', 'i': 'I-NORP', 'color': 'FireBrick',
             'description': 'Национальность, религия или '
                            'политическая '
                            'группа'},
            {'name': 'GPE', 'b': 'B-GPE', 'i': 'I-GPE', 'color': 'Gold', 'description': 'Страны, города, штаты'},
            {'name': 'FAC', 'b': 'B-FAC', 'i': 'I-FAC', 'color': 'Maroon',
             'description': 'Здания, аеропорты, дороги, мосты и тд'},
            {'name': 'PRODUCT', 'b': 'B-PRODUCT', 'i': 'I-PRODUCT', 'color': 'Chocolate',
             'description': 'Объекты, машины, еда и тд'},
            {'name': 'EVENT', 'b': 'B-EVENT', 'i': 'I-EVENT', 'color': 'MidnightBlue',
             'description': 'Именные ураганы, сражения, '
                            'спортивные '
                            'события и тд'},
            {'name': 'WORK_OF_ART', 'b': 'B-WORK_OF_ART', 'i': 'I-WORK_OF_ART', 'color': 'DarkGreen',
             'description': 'Названия книг, песен и тд'},
            {'name': 'LAW', 'b': 'B-LAW', 'i': 'I-LAW', 'color': 'HotPink', 'description': 'Нормативно-правовые акты'},
            {'name': 'LANGUAGE', 'b': 'B-LANGUAGE', 'i': 'I-LANGUAGE', 'color': 'SteelBlue', 'description': 'Язык'},
            {'name': 'TIME', 'b': 'B-TIME', 'i': 'I-TIME', 'color': 'DarkOliveGreen',
             'description': 'Время, которое меньше дня'},
            {'name': 'PERCENT', 'b': 'B-PERCENT', 'i': 'I-PERCENT', 'color': 'Khaki', 'description': 'Процент'},
            {'name': 'QUANTITY', 'b': 'B-QUANTITY', 'i': 'I-QUANTITY', 'color': 'Red',
             'description': 'Единица имерения, например вес '
                            'или длина'},
            {'name': 'ORDINAL', 'b': 'B-ORDINAL', 'i': 'I-ORDINAL', 'color': 'DarkBlue',
             'description': 'Первый, второй и тд'},
            {'name': 'CARDINAL', 'b': 'B-CARDINAL', 'i': 'I-CARDINAL', 'color': 'DarkBlue',
             'description': 'Числа, которые не попадают ни в '
                            'одну категорию'},
            {'name': 'ARM', 'b': 'B-ARM', 'i': 'I-ARM', 'color': 'Aqua', 'description': 'Вооружение РФ'}
        ]
        for t in tokensType:
            type = TokenType(name=t['name'], i=t['i'], b=t['b'], color=t['color'], description=t['description'])
            db.session.add(type)
        db.session.commit()


    @property
    def serverstatustext(self):
        return self.__serverstatustext
    @serverstatustext.setter
    def serverstatustext(self, value):
        self.__serverstatustext = value
        app.logger.info(value)

    def getstatus(self):
        rest = dict(status=self.rest.status, port=self.rest.port, image=self.rest.image, container=self.rest.container)
        server = dict(status=self.serverstatus, statustext=self.serverstatustext, rest=rest)
        return server

    # Получение сущностей из текста (вход: текст; выход: json с двумя ветками, в одном слова, в другом токены)
    def getEntityREST(self, text):
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }
        data = dict(x=[text])
        response = requests.post(f'http://{self.rest.socket}/model', headers=headers, json=data)
        return response.json()

    @staticmethod
    def getEntityRESTstatic(text, rest):
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }
        data = '{"x":["' + text + '"]}'

        response = requests.post(f'http://{rest.socket}/model', headers=headers, data=data.encode("utf-8"))
        return response.json()


    # Разделение текста на абзацы (вход: текст; выход: список абзацев)
    @staticmethod
    def devText(text):
        array = []  # Результирующий массив с абзацами
        i = 0
        texttemp = ''  # Временная строка, в которую заносится текст до символа переноса строки
        for symbol in text:
            if (symbol == '\n'):  # Если символ переноса строки, то строка до этого знака добавляется в список array
                if texttemp != '' and texttemp != '\n' and texttemp != '\r':
                    array.append(texttemp)
                texttemp = ''
                i = i + 1
                continue
            elif symbol == '\r':
                continue
            else:
                texttemp = texttemp + symbol
        if texttemp != '':
            array.append(texttemp)
        return array

    # Разделение абзаца на предложения (вход: абзац; выход: список предложений)
    @staticmethod
    def devSentenses(paragraph):
        array = []
        for sentenses in paragraph:
            arr = sent_tokenize(sentenses)
            array.append(arr)
        return array

    # Удалить последний символ в строке
    @staticmethod
    def remove_char(s):
        result = s[0: -1]
        return result

    # Формирование массива с токенами и словосочетаниями
    def devParagraphREST(self, paragraph):
        beginWord = False  # начато ли слово
        notSpace = False
        openedQuod = False
        resarray = []
        for sentense in paragraph:
            array = []
            id = 0
            wordtemp = ''
            i = ''
            entytyList = self.getEntityREST(str(sentense))
            for token in entytyList[0][1]:
                if beginWord:  # если слово начато
                    if "I-" in token:  # если токен начинается с I-, т.е слово не заканчивается на этом слове или символе
                        if entytyList[0][0][id] not in ["-", "»", "'", '"', "«", "»",
                                                        "."]:  # проверка на символы для добавления пробела
                            if notSpace:  # если символ стоит флаг не ставить пробел
                                wordtemp += f"{entytyList[0][0][id]}"  # символ или слова без пробела
                                notSpace = False  # после слова или символа уже можно ставить пробел
                            else:  # если не стоит флаг не ставить пробел
                                wordtemp += f" {entytyList[0][0][id]}"  # слово или символ с пробелом
                        if entytyList[0][0][id] in ["»", "'", '"', "«", "»"]:  # если символ - кавычки
                            if openedQuod:  # открыты ли кавычки? Да
                                wordtemp += f"{entytyList[0][0][id]}"  # пробел не ставится
                                openedQuod = False  # после слова пробел можно ставить
                                notSpace = False  # после слова пробел можно ставить
                            else:
                                wordtemp += f" {entytyList[0][0][id]}"
                                openedQuod = True
                                notSpace = True
                        if entytyList[0][0][id] in ["-",
                                                    "."]:  # при этих символах следующий символ или слово идет без пробела
                            wordtemp += f"{entytyList[0][0][id]}"
                            notSpace = True
                        id += 1
                        continue
                    else:
                        if entytyList[0][0][id] not in ["'", "-", '"', "»"]:
                            beginWord = False
                            word = dict(word=wordtemp, token=i.replace('B-', ''))
                            array.append(word)
                            wordtemp = ''
                        elif "B-" in token:
                            beginWord = False
                            word = dict(word=wordtemp, token=i.replace('B-', ''))
                            array.append(word)
                            wordtemp = ''
                        else:
                            wordtemp += entytyList[0][0][id]
                            openedQuod = False  # после слова пробел можно ставить
                            notSpace = False  # после слова пробел можно ставить
                            id += 1
                            continue
                if beginWord == False:
                    if token == "O":
                        if entytyList[0][0][id] in ["»", "'", '"', "«", "»"]:  # если символ - кавычки
                            if openedQuod:  # открыты ли кавычки? Да
                                openedQuod = False  # после слова пробел можно ставить
                                notSpace = False  # после слова пробел можно ставить
                            else:
                                openedQuod = True
                                notSpace = True
                        word = dict(word=entytyList[0][0][id], token='O')
                        array.append(word)
                        id += 1
                        continue
                    else:
                        beginWord = True
                        i = token
                        if entytyList[0][0][id] in ["'", '"', "«", "»"]:
                            if openedQuod:
                                wordtemp += f"{entytyList[0][0][id]}"
                                openedQuod = False
                                notSpace = False
                            else:
                                wordtemp += f"{entytyList[0][0][id]}"
                                openedQuod = True
                                notSpace = True
                        else:
                            if entytyList[0][0][id - 1] in ["'", '"', "«", "»", "("]:
                                array = array[:-1]
                                wordtemp += entytyList[0][0][id - 1]
                            wordtemp += entytyList[0][0][id]
                id += 1
            resarray.append(array)
        return resarray

    # Формирование html кода текста с сущностями (вход: список разделенный на абзацы, слова, предложения, и токены, список типов сущностей; выход: строка html)
    def reshtml(self, textarray, types):
        html = ''
        paragraphid = 0
        for paragraphs in textarray:
            html += '<p id ="' + str(paragraphid) + '" class=paragraph>'
            sentenceid = 0
            for sentence in paragraphs:
                html += '<span class="sentence" onmouseover="ChangeOver(this)" onmouseout="ChangeOut(this)" id ="' + str(
                    sentenceid) + '">'
                wordid = 0
                for word in sentence:
                    booltype = True
                    for type in types:
                        if type.name == word['token']:
                            html += f'<a class="card word" href="#top" oncontextmenu="RightClick(this)" ' \
                                    f'style="background-color:{type.color}" title="{type.description}" id="{str(wordid)}"' \
                                    f'data-token="{word["token"]}">{word["word"]}</a> '
                            booltype = False
                            break
                    if booltype:
                        if word['word'] == ',' or word['word'] == '.' or word['word'] == ';' or word['word'] == '!' or \
                                word[
                                    'word'] == '!' or word['word'] == ':':
                            html = self.remove_char(html)
                            html += '<span  onmouseover="ChangeOver(this)" onmouseout="ChangeOut(this)" oncontextmenu="RightClick(this)" class="word" id="' + str(
                                wordid) + '" data-token="' + word['token'] + '">' + \
                                    word['word'] + '</span> '
                        else:
                            html += '<span  onmouseover="ChangeOver(this)" onmouseout="ChangeOut(this)" oncontextmenu="RightClick(this)" class="word" id ="' + str(
                                wordid) + '" data-token="' + word['token'] + '">' + \
                                    word['word'] + '</span> '
                    wordid += 1
                html += '</span>'
                sentenceid += 1
            html += '</p>'
            paragraphid += 1
        return html

    # Функция корректирования данных, котрые отправляются пользователем с браузера в корректную jsonb строку
    def correctJsonString(self, json_obj):
        res = []
        for item in json_obj:
            if item['token'] != 'O':
                correctObj = self.getEntityREST(item['word'])
                first = True
                for correctObjItem in correctObj[0][0]:  # добавление токенам B- и I- значений
                    if first:
                        token = "B-" + item['token']
                        first = False
                    else:
                        token = "I-" + item['token']
                    correctObjDict = {'word': correctObjItem, 'token': token}
                    res.append(correctObjDict)
            else:
                res.append(item)
        return res

    # Запись файлов обучения
    @staticmethod
    def writetxtfile(filepath, datalist, count):
        writer = open(filepath, 'a')
        writer.seek(0, 2)
        while count != 0:
            sentence = datalist.pop()
            count -= 1
            i = 1
            for word in sentence.sentence:
                writer.write(f"{word['word']} {word['token']}\n")
                i += 1
                if i == 75:
                    writer.write("\n")
            if i != 75:
                writer.write("\n")

    # Формирование файлов обучения для нейросети DeepPavlov
    def gettxtfiles(self):
        shutil.copyfile(f"{self.webpath}/original txt/train.txt", f"{self.webpath}/actual txt/train.txt")
        shutil.copyfile(f"{self.webpath}/original txt/test.txt", f"{self.webpath}/actual txt/test.txt")
        shutil.copyfile(f"{self.webpath}/original txt/valid.txt", f"{self.webpath}/actual txt/valid.txt")
        learnSentences = db.session.query(LearnSentence).all()
        shuffle(learnSentences)
        count = len(learnSentences)
        testcount = math.ceil(count * 0.1)
        validcount = math.ceil(count * 0.1)
        traincount = count - testcount - validcount
        Server.writetxtfile(f"{self.webpath}/actual txt/train.txt", learnSentences, traincount)
        Server.writetxtfile(f"{self.webpath}/actual txt/test.txt", learnSentences, testcount)
        Server.writetxtfile(f"{self.webpath}/actual txt/valid.txt", learnSentences, validcount)

    # Копирование сформированных файлов обучения в папку нейронной сети
    def copyactualfiles(self):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), f"{self.deeppavlovpath}/models/ner_ontonotes_bert_mult")
        if os.path.exists(path) and os.path.isdir(path):
            shutil.rmtree(path)
        ontonotespath = os.path.join(os.path.abspath(os.path.dirname(__file__)), f"{self.deeppavlovpath}/downloads/ontonotes/")
        if not os.path.exists(ontonotespath):
            os.makedirs(ontonotespath)
        shutil.copyfile(f"{self.webpath}/actual txt/test.txt", f"{self.deeppavlovpath}/downloads/ontonotes/test.txt")
        shutil.copyfile(f"{self.webpath}/actual txt/valid.txt", f"{self.deeppavlovpath}/downloads/ontonotes/valid.txt")
        shutil.copyfile(f"{self.webpath}/actual txt/train.txt", f"{self.deeppavlovpath}/downloads/ontonotes/train.txt")

    # Сохранение модели с указанным именем
    def savemodel(self, modelname):
        self.serverstatus = True
        self.serverstatustext = "Сохранение модели"
        for root, dirs, files in os.walk(f"{self.savepath}/{modelname}"):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

        for src_dir, dirs, files in os.walk(self.deeppavlovpath):
            dst_dir = src_dir.replace(self.deeppavlovpath, f"{self.savepath}/{modelname}", 1)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            for file_ in files:
                src_file = os.path.join(src_dir, file_)
                dst_file = os.path.join(dst_dir, file_)
                if os.path.exists(dst_file):
                    os.remove(dst_file)
                shutil.copy(src_file, dst_dir)
        self.serverstatus = False
        self.serverstatustext = "Обучение не производится"

    # Сохранение переобученной модели в папку REST
    def savecurrentmodel(self):
        for root, dirs, files in os.walk(self.currentpath):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

        for src_dir, dirs, files in os.walk(self.deeppavlovpath):
            dst_dir = src_dir.replace(self.deeppavlovpath, self.currentpath, 1)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            for file_ in files:
                src_file = os.path.join(src_dir, file_)
                dst_file = os.path.join(dst_dir, file_)
                if os.path.exists(dst_file):
                    os.remove(dst_file)
                shutil.copy(src_file, dst_dir)

    # Удалить модель с указанным именем
    def deletemodel(self, modelname):
        shutil.rmtree(f"{self.savepath}/{modelname}")

    # Загрузить модель с указанным именем
    def loadmodel(self, modelname):
        self.serverstatus = True
        self.serverstatustext = "Загрузка модели"
        for root, dirs, files in os.walk(self.currentpath):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

        for src_dir, dirs, files in os.walk(f"{self.savepath}/{modelname}"):
            dst_dir = src_dir.replace(f"{self.savepath}/{modelname}", self.currentpath, 1)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            for file_ in files:
                src_file = os.path.join(src_dir, file_)
                dst_file = os.path.join(dst_dir, file_)
                if os.path.exists(dst_file):
                    os.remove(dst_file)
                shutil.copy(src_file, dst_dir)
        self.serverstatustext = "Перезапуск REST"
        self.changerest()
        self.serverstatustext = "Обучение не производится"
        self.serverstatus = False

    # Смена REST сервера для запуска переобученной модели
    def changerest(self):
        if self.rest == self.rest1:
            self.rest2.start()
            self.rest = self.rest2
            self.rest1.stop()
        else:
            self.rest1.start()
            self.rest = self.rest1
            self.rest2.stop()

    # Конвертация времени обучения
    @staticmethod
    def convert_to_preferred_format(sec):
        sec = sec % (24 * 3600)
        hour = sec // 3600
        sec %= 3600
        min = sec // 60
        sec %= 60
        return "%02d:%02d:%02d" % (hour, min, sec)

    # Получить список доступных моделей
    def getmodels(self):
        res = []
        n = 1
        files = os.listdir(self.savepath)
        for f in files:
            date = time.ctime(os.path.getmtime(f"{self.savepath}/{f}"))
            logpath = f'{self.savepath}/{f}/models/ner_ontonotes_bert_mult/logs/valid_log'
            if os.path.exists(logpath) and len(os.listdir(logpath)):
                files = os.listdir(logpath)
                logfile = files[0]
                if len(files) > 1:
                    for file in files:
                        if os.path.getsize(f'{logpath}/{file}') > os.path.getsize(f'{logpath}/{logfile}'):
                            logfile = file
                event_acc = EventAccumulator(f'{logpath}/{logfile}')
                event_acc.Reload()
                ner_f1 = 0
                modeltime = event_acc.Scalars("every_n_batches/ner_f1")[-1][0] - \
                            event_acc.Scalars("every_n_batches/ner_f1")[0][0]
                valid_log = []
                for data in event_acc.Scalars("every_n_batches/ner_f1"):
                    if data[2] > ner_f1:
                        ner_f1 = data[2]
                    valid_log.append(dict(time=time.ctime(data[0]), step=data[1], ner_f1=data[2]))
                model = dict(name=f, date=time.ctime(event_acc.Scalars("every_n_batches/ner_f1")[-1][0]), num=n,
                             ner_f1=ner_f1, time=Server.convert_to_preferred_format(modeltime), valid_log = str(valid_log))
                res.append(model)
            else:
                model = dict(name=f, date=date, num=n)
                res.append(model)
            n += 1
        return res



    # Запуск переобучения нейронной сети
    def train(self):
        try:
            self.serverstatus = True
            self.serverstatustext = "Сохранение предыдущей модели"
            self.savemodel("previous")
            self.serverstatus = True
            self.serverstatustext = "Создание файлов обучения"
            self.gettxtfiles()
            self.serverstatus = True
            self.serverstatustext = "Копирование файлов обучения"
            self.copyactualfiles()
            self.serverstatus = True
            self.serverstatustext = "Обучение модели"
            train_model(configs.ner.ner_ontonotes_bert_mult)
            self.serverstatustext = "Сохранение модели"
            self.savecurrentmodel()
            self.serverstatus = True
            self.serverstatustext = "Загрузка новой модели"
            self.changerest()
            self.serverstatustext = "Обучение не производится"
            self.serverstatus = False
        except ZeroDivisionError:
            self.serverstatustext = "Обучение не производится"
            self.serverstatus = False
        except:
            self.serverstatustext = f"Обучение завершилось с ошибкой ({self.serverstatustext})"
            self.serverstatus = False

    # Остановка переобучения нейронной сети
    def stoptrain(self):
        if self.thread.ident is None:
            raise ValueError('Поток не запущен')
        r = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self.thread.ident), ctypes.py_object(ZeroDivisionError))
        if r == 0:
            raise ValueError('Неправильный идентификатор потока')
        elif r > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(self.thread.ident, 0)
            raise SystemError('Неожиданное состояние среды выполнения')

class Rest:
    def __init__(self, port, image):
        self.status = True
        self.port = port
        self.image = image
        self.container = image

    @property
    def socket(self):
        return f"{self.image}:{self.port}"

    # Запуск REST сервера
    def start(self):
        client = docker.from_env()
        container = client.containers.get(self.container)
        container.start()
        while self.checkstatus() != True:
            time.sleep(5)
        self.status = True

    # Проверка наличия подключения к REST
    def checkstatus(self):
        try:
            Server.getEntityRESTstatic('test', self)
            result = True
        except:
            result = False
        return result

    # Остановка REST сервера
    def stop(self):
        client = docker.from_env()
        container = client.containers.get(self.container)
        container.stop()
        self.status = False

    # Перезапуск REST сервера
    def restart(self):
        client = docker.from_env()
        container = client.containers.get(self.container)
        container.restart()
        while self.checkstatus() != True:
            time.sleep(5)
        self.status = True





