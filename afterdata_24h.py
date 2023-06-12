import requests #api 호출
import json #api 호출
import apidb #db호출 파일
import get_time #날짜 및 시간 호출 파일

''''
기상청 api로 부터 24시간 예측 데이터를 불러와 DB에 저장
'''

# API 요청 주소
url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"

# 발급 받은 인증키
service_key = "API키 값"

# 요청할 지역의 좌표
area = "복현2동"
xyvalue = apidb.dbconfreeselect(f'select x, y from xytable where area = "{area}"') #x, y좌표를 가져온다
x = xyvalue[0][0]
y = xyvalue[0][1]
location_code = int(apidb.dbcon_get_location_code(area)) #location_code를 가져온다

# 현재 시간 설정
base_date = get_time.get_base_date()
base_time = get_time.get_base_time()


# API 요청 파라미터 설정
payload = {
    "serviceKey": service_key,
    "pageNo": "1",
    "numOfRows": "1000",
    "dataType": "json",
    "base_date": base_date,
    "base_time": base_time,
    "nx": x,
    "ny": y
}

# 응답 받은 JSON 데이터 파싱
def get_pridict_data(): #데이터중 필요한 데이터만 추출
    result = []
    res = requests.get(url, params=payload) #API 요청
    res_json = json.loads(res.content) #응답값
    items = res_json["response"]['body']['items']['item'] #데이터들 아이템에 저장
    for i in items:
        if i["category"] == "WSD": # 풍속값
            result.append({
                "fcstDate": i["fcstDate"],
                "fcstTime": i["fcstTime"],
                "WSD": float(i["fcstValue"])
            })
        elif i["category"] == "REH": # 습도값
            result[-1]["REH"] = float(i["fcstValue"])
        elif i["category"] == "PCP": # 강수량값
            if type(i["fcstValue"]) == str:
                if i["fcstValue"] == '강수없음':
                    result[-1]["PCP"] = 0.0
                elif i["fcstValue"][-2:] == 'mm':
                    result[-1]["PCP"] = float(i["fcstValue"][:-2])
            else:
                result[-1]["PCP"] = float(i["fcstValue"])
        elif i["category"] == "TMN": # 최대온도값
            result[-1]["TMN"] = float(i["fcstValue"])
        elif i["category"] == "TMX": # 최소온도값
            result[-1]["TMX"] = float(i["fcstValue"])
    return result

data = get_pridict_data() #필요한 데이터만 추출된 값

upd = 0; ins = 0
table = "weather_storage_24hour" #저장될 DB의 테이블 명
for i in range (len(data)): # 받아온 data의 길이만큼 수행
    info = "null"; status = 0
    if 'TMX' in data[i]: # 해당 row에 TMX값이 있을경우 저장
        max_temp = data[i]["TMX"]
        status = 1
    elif 'TMN' in data[i]: # 해당 row에 TMN값이 있을경우 저장
        min_temp = data[i]["TMN"]
        status = 2
    else: 
        max_temp = 0

    check = f'date_time = "{data[i]["fcstDate"]}" and value_time = "{data[i]["fcstTime"]}" and Location_code = {location_code}'
    stat = apidb.dbcon_check_select(table, check)[0][0] #값이 있는지 없는지 체크 (있으면 UPDATE, 없으면 INSERT)
    if(stat == 1):
        info = "up" # 값이 있으면 UPDATE
        upd += 1
        if (status == 1): #max_temp값이 있는 경우
            values = f'wind_speed = {data[i]["WSD"]}, rainfall = {data[i]["PCP"]}, Humidity = {data[i]["REH"]}, max_temp = {max_temp}'
            sql = f'UPDATE {table} SET {values} WHERE date_time = "{data[i]["fcstDate"]}" and value_time = "{data[i]["fcstTime"]}" and Location_code = {location_code};'
            apidb.dbconfreeupdate(sql) #SQL 실행구문
        elif (status == 2): #min_temp값이 있는 경우
            values = f'wind_speed = {data[i]["WSD"]}, rainfall = {data[i]["PCP"]}, Humidity = {data[i]["REH"]}, min_temp = {min_temp}'
            sql = f'UPDATE {table} SET {values} WHERE date_time = "{data[i]["fcstDate"]}" and value_time = "{data[i]["fcstTime"]}" and Location_code = {location_code};'
            apidb.dbconfreeupdate(sql)
        else: # 최대 최소 온도둘다 없는 경우
            values = f'wind_speed = {data[i]["WSD"]}, rainfall = {data[i]["PCP"]}, Humidity = {data[i]["REH"]}'
            sql = f'UPDATE {table} SET {values} WHERE date_time = "{data[i]["fcstDate"]}" and value_time = "{data[i]["fcstTime"]}" and Location_code = {location_code};'
            apidb.dbconfreeupdate(sql)
    elif(stat == 0): # 값이 없으면 INSERT
        info = "inst"
        ins += 1
        values = f'0, {location_code}, "{data[i]["fcstDate"]}", "{data[i]["fcstTime"]}", {data[i]["WSD"]}, {data[i]["PCP"]}, {data[i]["REH"]}, {max_temp}, {min_temp}'
        apidb.dbconinsert(table, values) 
    else:
        info = "err"

print(get_time.get_today("-"), get_time.get_now_time(), "success insert_rate :", ins, "update_rate :", upd) #log 확인용