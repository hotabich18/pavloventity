#import csv
import psycopg2
import time
completecount = 0
count = 0

def trycon():
    boolcon = True
    while(boolcon):
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

def getcount(con):
    cur = con.cursor()
    cur.execute('select count(*) from tokens')
    count = 0
    for row in cur:
        count = row[0]
    return count

def minid(con):
    cur = con.cursor()
    cur.execute('select min(id) from tokens')
    min = 0
    for row in cur:
        min = row[0]
    return min

def maxid(con):
    cur = con.cursor()
    cur.execute('select max(id) from tokens')
    max = 0
    for row in cur:
        max = row[0]
    return max

def dotfind(con, id):
    cur = con.cursor()
    startid = id - 37
    endid = id  + 37
    cur.execute('select id,word from tokens where id > %d and id < %d' % (startid, endid))
    result = id
    for row in cur:
        if row[1] == '.':
            result = row[0]
            break
    return result

def writetxt(startid, endid, filename):
    try:
        global count
        global completecount
        cur = con.cursor()
        rowcount = 0
        percent = 0.00

        writer = open(filename, 'w')

        cur.execute('SELECT * FROM tokens where id >= %s and id <= %s' % (startid, endid))
        for row in cur:
            word = row[1]
            type = row[2]
            if word == '.':
                writer.write("%s %s\n" % (word, type))
                writer.write('\n')
                rowcount = 0
            elif rowcount > 74:
                writer.write("%s %s\n" % (word, type))
                writer.write('\n')
                rowcount = 0
            else:
                writer.write("%s %s\n" % (word, type))
                rowcount = rowcount + 1
            completecount = completecount + 1
            percent = completecount / count * 100

            print('Выполнено %d%% ' % percent, end='')
            print('\r', end='')
    except KeyboardInterrupt:
        writer.close()
        raise SystemExit



if __name__ == '__main__':
    con = trycon()

    count = getcount(con)
    trainend = dotfind(con, count // 1.25)
    max = maxid(con)
    min = minid(con)
    validstart = trainend + 1
    validend = dotfind(con, count * 0.9 // 1)
    teststart = validend + 1

    writetxt(min, trainend, 'train.txt')
    writetxt(validstart, validend, 'valid.txt')
    writetxt(teststart, max, 'test.txt')




