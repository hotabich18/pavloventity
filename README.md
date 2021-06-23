# Pavlov Entity

![](https://static.tildacdn.com/tild6638-3538-4963-b964-373133313862/_DeepPavlov_-5.png)

### Описание
Pavlov Entity - это система, которая использует нейронную сеть DeepPavlov с целью выявления сущностей из текста новостного материала, а также для переобучения, сохранения и загрузки моделей нейронной сети.

### Установка
                
-  Собрать образы для bert_mult и pavlov_rest
```bash
docker build -t pavloventity ./bert_mult
docker build -t pavlovrest ./pavlov_rest
```
- Изменить строку подключения к базе данных в файле (при необходимости, если используется другая СУБД):
./bert_mult/web/config.py

```python
class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('PRODUCTION_DATABASE_URI') or \
	'postgresql://username:password@hostname:port/dbname'

```

- Запустить проект
```bash
sudo docker-compose up
```

### Структура проекта
- Pavloventity
  - bert_mult - модуль взаимодействия с нейронной сетью
    - current_model - текущая моделью для REST API нейронной сети
    - deeppavlov -  окружение и модель, необходимые для работы модуля взаимодействия с нейронной сетью
    - saved_models - сохраненные пользователем модели
    - web  - директория веб-интерфейса и api-функций модуля взаимодействия с нейронной сетью
      - actual txt - текущие файлы обучения, полученные слиянием предложений с БД и изначальных файлов обучения
      - app - директория веб-интерфейса и api-функций модуля взаимодействия с нейронной сетью
      - logs - логи веб-интерфейса и api-функций модуля взаимодействия с нейронной сетью
      - old scripts - старые скрипты для получения изначальных файлов обучения
      - original txt - изначальные файлы обучения
  - pavlov_rest - виртуальное окружение REST API нейронной сети





#API

**Обработка текста (выявление сущностей)**

POST: http://localhost:5550/api/getentity

Body raw: {"text": "your text"}
```bash
curl --location --request POST 'http://localhost:5550/api/getentity' \
--data-raw '{"text": "your text"}'
```
Пример результата:
```python
    [
      [
        [
          "your",
          "text"
        ],
        [
          "O",
          "O"
        ]
      ]
    ]
```
**Добавить тип сущности**

POST: http://localhost:5550/api/addentity

Body raw: {"name": "TEST", "i": "I-TEST", "b": "B-TEST", "color": "#d53032", "description": "test description"}
```bash
curl --location --request POST 'http://localhost:5550/api/addentity' \
--data-raw '{"name": "TEST", "i": "I-TEST", "b": "B-TEST", "color": "#d53032", "description": "test description"}'
```
Пример результата:
```python
{
  "status": "OK"
}
```
**Запуск обучения модели**

POST: http://localhost:5550/api/train

```bash
curl --location --request POST 'http://localhost:5550/api/train'
```
Пример результата:
```python
{
  "status": "Train started."
}
```
**Отмена обучения модели**

POST: http://localhost:5550/api/stoptrain

```bash
curl --location --request POST 'http://localhost:5550/api/stoptrain'
```
Пример результата:
```python
{
  "status": "Train stopped."
}
```
**Добавить предложение для дообучения модели**

POST: http://localhost:5550/api/addsentence

Body raw:
```bash
[{"word":"Высокоточный","token":"O"},{"word":"ракетный","token":"O"},{"word":"комплекс","token":"O"},{"word":"«Искандер»","token":"ARM"},{"word":"предназначен","token":"O"},{"word":"для","token":"O"},{"word":"уничтожения","token":"O"},{"word":"вражеских","token":"O"},{"word":"средств","token":"O"},{"word":"огневого","token":"O"},{"word":"поражения","token":"O"},{"word":"далеко","token":"O"},{"word":"за","token":"O"},{"word":"линией","token":"O"},{"word":"фронта","token":"O"},{"word":".","token":"O"}]
```
```bash
curl --location --request POST 'http://localhost:5550/api/getentity' \
--data-raw '{"text": "your text"}'
```
Пример результата:
```python
{
  "status": "OK"
}
```
**Загрузка сохраненной модели**

POST: http://localhost:5550/api/loadmodel?name=test

PARAMS: name: название модели

```bash
curl --location --request POST 'http://localhost:5550/api/loadmodel?name=test'
```
Пример результата:
```python
{
  "status": "OK"
}
```

**Сохранение модели**

POST: http://localhost:5550/api/savemodel?name=test

PARAMS: name: название модели

```bash
curl --location --request POST 'http://localhost:5550/api/savemodel?name=test1'
```
Пример результата:
```python
{
  "status": "OK"
}
```

**Удаление сохраненной модели**

POST: http://localhost:5550/api/delmodel?name=test1

PARAMS: name: название модели

```bash
curl --location --request POST 'http://localhost:5550/api/delmodel?name=test1'
```
Пример результата:
```python
{
  "status": "OK"
}
```
**Статус сервера**

POST: http://localhost:5550/api/getstatus

```bash
curl --location --request POST 'http://localhost:5550/api/getstatus'
```
Пример результата:
```python
{
  "rest": {
    "container": "deeppavlov_pavlov_rest_1_1",
    "image": "pavlov_rest_1",
    "port": 5000,
    "status": true
  },
  "status": false,
  "statustext": "Обучение не производится"
}
```
**Список сохраненных моделей**

POST: http://localhost:5550/api/getmodels

```bash
curl --location --request POST 'http://localhost:5550/api/getmodels'
```
Пример результата:
```python
[
  {
    "date": "Thu Jun  3 06:47:18 2021",
    "name": "previous",
    "num": 1
  },
  {
    "date": "Mon May 31 09:55:02 2021",
    "name": "work arm",
    "num": 2
  }
]
```
