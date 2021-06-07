import threading
import time
import docker
import json
import os
import requests
import shutil
import ctypes
from deeppavlov import configs, train_model
from nltk.tokenize import sent_tokenize

from app import db
from app.models import LearnSentence


class Server:
    def __init__(self, rest1, rest2, webpath, deeppavlovpath, savepath, currentpath):
        self.rest1 = rest1
        self.rest2 = rest2
        self.rest = rest1
        self.serverstatus = False
        self.serverstatustext = "Обучение не производится"
        self.webpath = webpath
        self.deeppavlovpath = deeppavlovpath
        self.savepath = savepath
        self.currentpath = currentpath
        self.thread = None

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

        data = '{"x":["' + text + '"]}'

        # response = requests.post('http://localhost:5556/model', headers=headers, data=data.encode("utf-8"))
        #
        response = requests.post(f'http://{self.rest.socket}/model', headers=headers, data=data.encode("utf-8"))
        # print(response.json())
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
        sentenseid = 0
        for sentense in paragraph:
            array = []
            id = 0
            wordtemp = ''
            i = ''
            entytyList = self.getEntityREST(sentense)
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
        print(json_obj)
        for item in json_obj:
            if item['token'] != 'O':
                correctObj = self.getEntityREST(item['word'].replace('"', '\\"'))
                print(correctObj)
                first = True
                for correctObjItem in correctObj[0][0]:  # добавление токенам B- и I- значений
                    token = ''
                    if first:
                        token = "B-" + item['token']
                        first = False
                    else:
                        token = "I-" + item['token']
                    correctObjDict = {'word': correctObjItem, 'token': token}
                    res.append(correctObjDict)
            else:
                res.append(item)
        resString = json.dumps(res)
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
        count = len(learnSentences)
        testcount = int(count * 0.1)
        validcount = int(count * 0.1)
        traincount = count - testcount - validcount
        Server.writetxtfile(f"{self.webpath}/actual txt/train.txt", learnSentences, traincount)
        Server.writetxtfile(f"{self.webpath}/actual txt/test.txt", learnSentences, testcount)
        Server.writetxtfile(f"{self.webpath}/actual txt/valid.txt", learnSentences, validcount)

    # Копирование сформированных файлов обучения в папку нейронной сети
    def copyactualfiles(self):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), f"{self.deeppavlovpath}/models/ner_ontonotes_bert_mult")
        shutil.rmtree(path)
        shutil.copyfile(f"{self.webpath}/actual txt/train.txt", f"{self.deeppavlovpath}/downloads/ontonotes/train.txt")
        shutil.copyfile(f"{self.webpath}/actual txt/test.txt", f"{self.deeppavlovpath}/downloads/ontonotes/test.txt")
        shutil.copyfile(f"{self.webpath}/actual txt/valid.txt", f"{self.deeppavlovpath}/downloads/ontonotes/valid.txt")

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

    # Получить список доступных моделей
    def getmodels(self):
        res = []
        n = 1
        files = os.listdir(self.savepath)
        for f in files:
            date = time.ctime(os.path.getmtime(f"{self.savepath}/{f}"))
            model = dict(name=f, date=date, num = n)
            n += 1
            res.append(model)
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
            self.serverstatustext = "Обучение завершилось с ошибкой"
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





