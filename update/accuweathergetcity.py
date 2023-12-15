import requests
import json

'''
AccuWeather API를 사용하기 위해 도시 코드를 받아오는 API
'''

# AccuWeather API 키
api_key = 'API 키값'
lang = 'ko-kr'

def get_areacode(area_name):
    # API 엔드포인트 URL
    url = f'http://dataservice.accuweather.com/locations/v1/cities/search?apikey={api_key}&q={area_name}&language={lang}'
    # API 요청 보내기
    response = requests.get(url)
    # JSON 데이터 파싱
    data = json.loads(response.content.decode('utf-8'))
    # 파싱된 데이터 출력
    Key = data[0]['Key'] # 반환된 키값만 출력
    return(Key)