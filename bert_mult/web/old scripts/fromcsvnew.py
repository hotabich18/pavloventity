# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import requests
import json
import psycopg2
import csv
import time


def trycon():
    boolcon = True
    while (boolcon):
        try:
            con = psycopg2.connect(
                database="postgres",
                user="admin",
                password="secret",
                host="127.0.0.1",
                port="5432"
            )
            boolcon = False
            print("Подключение к БД выполнено!")
        except:
            print("Нет подключение к базе данных!")
            time.sleep(5)
    return con


def getcountnews():
    with open('arm.csv', newline='') as File:
        reader = csv.reader(File)
        count = 0
        for row in reader:
            count = count + 1
        return count


def insertRow(userword, wordtype, con):

    query_template = "INSERT INTO newwords (word,token) VALUES ('{word}', '{token}')"
    #query = query_template.format(word=userword, type=wordtype)

    try:
        cur = con.cursor()
        cur.execute("EXECUTE insuser(%s, %s)", (userword, wordtype))
        # cur.execute(query)
        con.commit()
        # print(query)
    except psycopg2.errors.UniqueViolation:
        print(userword + ' уже содержится в базе данных!')
    except psycopg2.errors.SyntaxError:
        print(userword + ' не удалось вставить в базу данных!')
    except psycopg2.errors.InFailedSqlTransaction:
        print(userword + ' не удалось вставить в базу данных!')


def lenta():
    with open('arm.csv', newline='') as File:
        reader = csv.reader(File)
        row_template = "__label__{category} {content}"
        count = 0
        id = 0
        with open("data1.txt", "w") as file:
            for row in reader:
                id = +1
                if (row[4] != 'Все' and row[4] != ''):
                    format_row = row_template.format(category=row[4], content=row[2])
                    print(format_row, file=file)
                    count += 1
                    print(count)


def getEntity(text):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    data = '{"x":["' + text + '"]}'

    # response = requests.post('http://10.10.17.1:5556/model', headers=headers, data=data.encode("utf-8"))
    response = requests.post('http://127.0.0.1:5556/model', headers=headers, data=data.encode("utf-8"))
    # print(response.json())

    return response.json()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    con = trycon()
    cur = con.cursor()
    cur.execute("PREPARE insuser AS " +
                "INSERT INTO newwords (word, token) VALUES ($1, $2)")

    with open('arm.csv', newline='') as File:
        reader = csv.reader(File)
        rowcount = getcountnews()
        count = 0
        percent = 0.00
        percent_template = "{percent}% (обработано {count})"

        for row in reader:
            first = True
            id = 0
            try:
                data = getEntity(row[0])
                for entity in data[0][0]:
                    if first:
                        insertRow(entity, 'B-ARM', con)
                        first = False
                    else:
                        insertRow(entity, 'I-ARM', con)
                    id += 1
                count = count + 1
                format_percent = percent_template.format(percent=percent, count=count)
                percent = count / rowcount * 100
                print(format_percent)
            except KeyError:
                continue
            except json.decoder.JSONDecodeError:
                continue
            except IndexError:
                continue
            except KeyboardInterrupt:
                raise SystemExit

    # insertRow('lox', 'o', con)
    # print(getEntity("Получайте ответы на вопросы по любой теме из области IT от специалистов в этой теме.")[0][1][3])

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
