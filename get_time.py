from datetime import date, datetime, timedelta

'''
날짜를 불러오는 파일
'''

today = date.today() # 오늘의 날짜

now = datetime.now()  # 현재 시간을 가져옴
hour = now.hour       # 시
minute = now.minute   # 분
second = now.second   # 초

def get_today(check): #오늘 날짜 반환
    if (check == "-"):
        today_date = today.strftime('%Y-%m-%d')
    else:
        today_date = today.strftime('%Y%m%d')
    return today_date

def get_after_date(plus): #미래 날짜 반환
    want_date = (today + timedelta(plus)).strftime('%Y%m%d')
    return want_date

def get_after_date_line(plus):
    want_date = (today + timedelta(plus)).strftime('%Y-%m-%d')
    return want_date

def get_now_time(): # 현재 시간을 int형으로 나타내줌
    now_time = (int(hour) * 100) + int(minute)
    return now_time

def get_base_date(): # 기상청 단기예보 api 사용을 위한 기준일 설정
    if get_now_time() < 230:
        yesterday = today - timedelta(1) #timedelta 만큼 전일
        base_date = yesterday.strftime('%Y%m%d')
    else:
        base_date = today.strftime('%Y%m%d')
    return base_date


def get_base_time(): # 기상청 단기예보 api 사용을 위한 base_time 구하기
    base_time = '0200'
    standard_time = get_now_time()
    if (standard_time >= 2330): #현재 시간에따라 base_time 변경
        base_time = '2300'
    elif (standard_time >= 2030):
        base_time = '2000'
    elif (standard_time >= 1730):
        base_time = '1700'
    elif (standard_time >= 1430):
        base_time = '1400'
    elif (standard_time >= 1130):
        base_time = '1100'
    elif (standard_time >= 830):
        base_time = '0800'
    elif (standard_time >= 530):
        base_time = '0500'
    elif (standard_time >= 230):
        base_time = '0200'
    else:
        base_time = 2300
    return base_time