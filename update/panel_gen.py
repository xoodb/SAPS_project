import apidb
import get_time
'''
측정한 패널의 전류, 전압, 예측 일사량을 사용하여 예측 발전량을 계산합니다
''' 
panel = '' #패널의 이름
table = 'panel_measure'
yesterday = get_time.get_after_date(-1)
yesterday_for = get_time.get_after_date_format(-1)

data = apidb.dbconfreeselect(f'SELECT voltage, current FROM {table} WHERE Date = "{yesterday}"')

voltage = data[0][0]; cuurrent = data[0][1]
chg_W = voltage * cuurrent
W_24 = chg_W * 24

apidb.dbconfreeupdate(f'UPDATE measurement SET measure = {W_24} WHERE measure_date = "{yesterday_for}" AND device_ID = "{panel}"')