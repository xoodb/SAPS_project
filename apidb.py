import pymysql
'''
RDS와 연결해주는 SQL구문
'''

def dbconinsert(table, values): #테이블과 값 입력시 Insert
    con = pymysql.connect(host='', user='', password='', db='', charset='utf8')
    cursor = con.cursor()
    sql = f"INSERT INTO {table} VALUES ({values});"
    cursor.execute(sql)
    con.commit()
    con.close()

def dbconupdate(table, values, date): #테이블과 업데이트값, 값 입력시 Update
    con = pymysql.connect(host='', user='', password='', db='', charset='utf8')
    cursor = con.cursor()
    sql = f'UPDATE {table} SET {values} WHERE date = "{date}";'
    cursor.execute(sql)
    con.commit()
    con.close()

def dbconfreeupdate(value): #자율적인 update구문
    con = pymysql.connect(host='', user='', password='', db='', charset='utf8')
    cursor = con.cursor()
    sql = f'{value};'
    cursor.execute(sql)
    con.commit()
    con.close()

def dbconselect(table, date): #테이블과 조건 입력시 Select
    con = pymysql.connect(host='', user='', password='', db='', charset='utf8')
    cursor = con.cursor()
    sql = f'SELECT * FROM {table} WHERE date = "{date}";'
    cursor.execute(sql)
    rows = cursor.fetchall()
    con.close()
    return rows

def dbconfreeselect(value): #Select로 모든 데이터를 받지않고 세부적인 데이터를 받을떄 사용
    con = pymysql.connect(host='', user='', password='', db='', charset='utf8')
    cursor = con.cursor()
    sql = f'{value};'
    cursor.execute(sql)
    rows = cursor.fetchall()
    con.close()
    return rows

def dbcon_check_select(table, value): #테이블과 조건 입력시 Select
    con = pymysql.connect(host='', user='', password='', db='', charset='utf8')
    cursor = con.cursor()
    sql = f'SELECT COUNT(*) FROM {table} WHERE {value};'
    cursor.execute(sql)
    rows = cursor.fetchall()
    con.close()
    return rows

def dbcon_get_location_code(area): # xytable에서 지역명으로 location_code 반환하는 sql문
    con = pymysql.connect(host='', user='', password='', db='', charset='utf8')
    cursor = con.cursor()
    sql = f'SELECT location_code FROM xytable WHERE area = "{area}";'
    cursor.execute(sql)
    rows = cursor.fetchall()
    con.close()
    return rows[0][0]