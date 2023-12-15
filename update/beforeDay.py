import requests
from datetime import date, timedelta
import time
import json
import sun_imformation # 일출, 일몰값 제공 api
import csv

'''
학습에 필요한 지역의 과거 데이터를 csv파일 형태로 저장
'날짜', '일출', '일몰', '최소', '최대', '강수량', '풍속', '습도', '일조시간', '전운량', '일샤랑' 값들을 저장
'''

# API 요청 주소
url = "http://apis.data.go.kr/1360000/AsosDalyInfoService/getWthrDataList"

# 발급 받은 인증키
service_key = "API키 값" #디코딩된 키

# 요청할 지역의 좌표
code = 143 #대구 지역 코드

# 현재 시간
today = date.today() #오늘의 날짜 '0000-00-00'형식
start_date_form = date.today() - timedelta(1) #timedelta 만큼 전일
now_time = today.strftime('%Y%m%d') # '0000-11-22' 형식을 '00001122'형식으로 바꾼다 (api위해 생성)
start_date = start_date_form.strftime('%Y%m%d') #위와 동일

# API 요청 파라미터 설정
payload = {
    "serviceKey": service_key,
    "pageNo": "1",
    "numOfRows": "200",
    "dataType": "json",
    "dataCd" : "ASOS",
    "dateCd" : "DAY",
    "startDt": "0",
    "endDt": "0",
    "stnIds": code
}

# 응답 받은 JSON 데이터 파싱
def getsol(setdate): #데이터중 일사량만 추출
    payload["startDt"] = setdate; payload["endDt"] = setdate #추출할 날짜 설정
    try:
        print("wait ", end='')
        time.sleep(0.5)
        res = requests.get(url, params=payload) #API 요청
    except:
        print("wait 3", end='')
        time.sleep(3)
        res = requests.get(url, params=payload) #API 요청
    res_json = json.loads(res.content) #응답값
    items = res_json["response"]['body']['items']['item'] #데이터들 아이템에 저장
    #day = items[0]['tm'] # 날짜
    minTa = float(items[0]['minTa']) # 최저 온도
    maxTa = float(items[0]['maxTa']) # 최고 온도
    sumRn = items[0]['sumRn'] # 일강수량
    if sumRn == "":
        sumRn = float(0)
    else: sumRn = float(sumRn)
    avgWs = items[0]['avgWs'] # 평균 풍속
    if avgWs == "":
        return 1
    else: avgWs = float(avgWs)
    avgRhm = items[0]['avgRhm'] # 평균 습도
    if avgRhm == "":
        return 1
    else: avgRhm = float(avgRhm)
    sumSsHr = (items[0]['sumSsHr']) # 일조시간
    if sumSsHr == "":
        return 1
    else: sumSsHr = float(sumSsHr)
    #sumGsr = unit_change.change_MJ_to_W(float(items[0]['sumGsr'])) #합계 일사량
    sumGsr = float(items[0]['sumGsr'])
    avgTca = (float(items[0]['avgTca']) * 10 ) # 평균전운량
    lst = [minTa, maxTa, sumRn, avgWs, avgRhm, sumSsHr, avgTca, sumGsr] #데이터들 리스트로 반환
    return lst


liss = ['날짜', '일출', '일몰', '최소', '최대', '강수량', '풍속', '습도', '전운량', '일샤랑'] #추가될 데이터들 순서
print(liss)

with open('recent_data.csv', 'a', newline='') as csvfile: #csv파일에 받아온 값을 추가
    writer = csv.writer(csvfile)
    for i in range (1, 12): #어제(1)부터 몇개의 데이터를 뽑을건지
        print(i, end=' ')
        information = []
        start_date_form = date.today() - timedelta(i) # 오늘날에서 i만큰 전일 출력
        start_date = start_date_form.strftime('%Y%m%d') #위와 동일

        measure_sol = getsol(start_date)
        if (measure_sol == 1): #하나라도 값이 없으면 건너뛰기
            print("skip")
            continue
        information.append(start_date) # 해당 데이터의 날짜 추가
        sun = sun_imformation.get_sun(start_date) # 일출 일몰값 가져오기
        information.append(round(sun[0] + (sun[1] / 60), 3)) # 일출시간 추가
        information.append(round(sun[2] + (sun[3] / 60), 3)) # 일몰시간 추가
        measure_sol = getsol(start_date) # 기상청 API로 부터 해당일 데이터 받아오기 (리스트 반환)
        for i in measure_sol:
            information.append(i) # 데이터들 추가
        print(information) # 추가되는 데이터 확인
        writer.writerow(information) # csv 파일에 추가