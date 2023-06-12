import apidb #db호출 파일
import sun_imformation #일출 일몰 데이터 가져옴
import get_time #시간 제공 파일

'''
DB에 저장된 24시간 24개의 데이터를 읽어 일일로 평균내어 정리하여 DB에 삽입
''' 

# 요청할 지역의 좌표
area = "복현2동" #지역의 지명
location_code = apidb.dbcon_get_location_code(area) #location_code를 가져온다

Day_Data = { #평균낸 값을 저장할 딕셔너리 생성
    "Date": 20000101,
    "Sunrise": 0,
    "Sunset": 0,
    "Min_Temp": 0,
    "Max_Temp": 0,
    "Rainfall": 0,
    "Wind_speed": 0,
    "Humidity": 0,
    "Suntime": 0,
    "Cloud": 0,
    "location_code": 0
}


def get_24hour_data(date): #24시간 데이터를 일일 데이터로 변환
    count = 0
    wind = 0
    rainy = 0
    humidity = 0
    max_temp = 0
    min_temp = 0
    max_count = 0
    min_count = 0
    sql = f"SELECT wind_speed, rainfall, Humidity, max_temp, min_temp FROM weather_storage_24hour WHERE date_time = '{get_time.get_after_date(date)}' AND Location_code = {location_code}"
    today = apidb.dbconfreeselect(sql) #날짜에 맞는 데이터 가져오기
    for i in range(0, len(today)): #가져온 24개의 데이터를 일일로 평균 내기
        wind += today[i][0]
        rainy += today[i][1]
        humidity += today[i][2]
        max_temp += today[i][3]
        if (today[i][3] != 0): 
            max_count += 1
        min_temp += today[i][4]
        if (int(today[i][4]) != 0): 
            min_count += 1
        count += 1
    Day_Data["Date"] = get_time.get_after_date(date) # 계산한 없을 딕셔너리에 설정
    Day_Data["Wind_speed"] = round(wind / count, 1)
    Day_Data["Rainfall"] = rainy
    Day_Data["Humidity"] = round(humidity / count, 1)
    Day_Data["Max_Temp"] = round(max_temp / max_count, 1)
    Day_Data["Min_Temp"] = round(min_temp / min_count, 1)
    Day_Data["location_code"] = location_code
    return 0

def get_day_data(date): # solar_api_5day테이블에서 날짜에 맞는 일사량, 구름량을 가져온다
    sql = f"SELECT solar_time, cloud FROM solar_api_5day WHERE date = '{get_time.get_after_date(date)}'"
    sec_data = apidb.dbconfreeselect(sql)
    sun_info = sun_imformation.get_sun(get_time.get_after_date(date))
    Day_Data["Sunrise"] = round(sun_info[0] + (sun_info[1] / 60), 3)
    Day_Data["Sunset"] = round(sun_info[2] + (sun_info[3] / 60), 3)
    Day_Data["Cloud"] = sec_data[0][1]
    return 0

inst = 0; upd = 0
table = "weather_storage_Day"
for i in range(3): 
    get_day_data(i)
    get_24hour_data(i)
    check = f'Date = "{Day_Data["Date"]}" AND Location_code = {Day_Data["location_code"]}'
    stat = apidb.dbcon_check_select(table, check)[0][0] #값이 있는지 없는지 체크
    if (stat == 1): # 값이 있으면 UPDATE 실행
        values = f'Sunrise = {Day_Data["Sunrise"]}, Sunset = {Day_Data["Sunset"]}, Min_Temp = {Day_Data["Min_Temp"]}, Max_Temp = {Day_Data["Max_Temp"]}, Rainfall = {Day_Data["Rainfall"]}, Wind_speed = {Day_Data["Wind_speed"]}, Humidity = {Day_Data["Humidity"]}, Cloud = {Day_Data["Cloud"]}'
        sql = f'UPDATE {table} SET {values} WHERE Date = "{Day_Data["Date"]}" AND Location_code = {Day_Data["location_code"]};'
        apidb.dbconfreeupdate(sql) #SQL 실행구문
        upd += 1
    elif (stat == 0): # 값이 없으면 INSERT 실행
        values = f'"{Day_Data["Date"]}", {Day_Data["location_code"]}, {Day_Data["Sunrise"]}, {Day_Data["Sunset"]}, {Day_Data["Min_Temp"]}, {Day_Data["Max_Temp"]}, {Day_Data["Rainfall"]}, {Day_Data["Wind_speed"]}, {Day_Data["Humidity"]}, {Day_Data["Cloud"]}, 0'
        apidb.dbconinsert(table, values) 
        inst += 1
    else:
        print("ERROR")

print(get_time.get_today("-"), get_time.get_now_time(), "success insert_rate :", inst, "update_rate :", upd) #log 확인용