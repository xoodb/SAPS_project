import requests
import json
import xmltodict
import apidb

'''
해당 경도 위도의 일출, 일몰 시간을 가져오는 API
'''
#데이터를 가져올 지역의 위도, 경도
longittude = 0 # 경도
latitue = 0 # 위도
Coordinates_list = []

def get_Coordinates(area):
    Coordinates_list = apidb.dbconfreeselect(f"SELECT Latitude_sec/100, longitude_sec/100 FROM xytable WHERE area = '{area}'")
    longittude = Coordinates_list[0][1] # 경도
    latitue = Coordinates_list[0][0] # 위도
    return 0

key = 'API키값' #API키값
url = 'http://apis.data.go.kr/B090041/openapi/service/RiseSetInfoService/getLCRiseSetInfo' #일출정보


def get_sun(date, area): # 일출, 일몰값을 리스트 형태로 일출(시), 일출(분), 일몰(시), 일몰(분) 형태로 저장
    get_Coordinates(area)
    params ={'serviceKey' : key, 'locdate' : date, 'longitude' : longittude, 'latitude' : latitue, 'dnYn' : 'Y' } # 입력값
    response = requests.get(url, params=params)
    xpars = xmltodict.parse(response.text) #XML 형태로 제공해 JSON타입으로 변환
    jsonDump = json.dumps(xpars)
    res_json = json.loads(jsonDump)
    items = res_json["response"]['body']['items']['item']
    sunrise = int(items['sunrise'])
    sunset = int(items['sunset'])
    list = [int(sunrise / 100), sunrise % 100, int(sunset / 100), sunset % 100]
    return list