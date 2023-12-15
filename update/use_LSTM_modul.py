import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import load_model
import apidb
import get_time
import update_device

'''
학습된 LSTM모델을 불러와 특성들을 넣어 그에 따른 일사량 예측량 추출
'''

#학습된 LSTM 모델
loaded_model = load_model('SAPS_lstm_model_1.h5')

# 데이터 파일 읽어오기
train_data = pd.read_csv('total_data.csv', encoding='euc-kr')
data = train_data.drop('날짜', axis=1) #날짜 컬럼 제거
X_train = data.iloc[:, :-1].values #독립변수
y_train = data.iloc[:, -1].values #종속변수
y_train = y_train.reshape(-1, 1) #2차원으로 변형
#일사량값 0~1사이로 정규화
sc_x = MinMaxScaler() #입력값
X_train_scaled = sc_x.fit_transform(X_train)
sc_y = MinMaxScaler() #출력값
y_train_scaled = sc_y.fit_transform(y_train)
#정규화 범위를 지정해주기 위해서 테스트 데이터도 호출

#등록된 기기의 위치 정보를 가져온다
Area_list = update_device.get_device_list()
area_count = 0
#저장된 기기 각각 실행
for get_area in Area_list:
    upd = 0 #업데이트 실행횟수
    area_count += 1
    Location_code = get_area[1] # 데이터 베이스에서 지역과 같은 Location_code 획득
    area = update_device.get_device_area(Location_code)[0][0] # 지역 이름
    Coordinates = update_device.get_Coordinates_Location_code(Location_code)# 해당 위치의 경도 위도값
    latitude = Coordinates[0][0] #경도
    longitude = Coordinates[0][1] #위도
    #테스트 데이터 불러오기
    date_arr = []
    organize_data = []
    for i in range (0, 4): #어제부터 2일 뒤까지 4일의 날짜값
        date_arr.append(get_time.get_after_date(i - 1))
    #처음과 마지막 날짜 사이의 값을 추출
    sql = f"select sunrise, sunset, Min_temp, Max_Temp, Rainfall, Snowing, Wind_speed, Humidity, Cloud from weather_storage_Day WHERE Date BETWEEN {date_arr[0]} AND {date_arr[-1]} AND Location_code = {Location_code}"
    data = apidb.dbconfreeselect(sql) #DB에 저장된 데이터를 받아온다
    for row in data: #받아온 데이터에 경도 위도값 추가
        store_data = []
        for i in range (len(row)):
            if (i == 2):
                store_data.append(latitude)
                store_data.append(longitude)
                store_data.append(row[i])
            else:
                store_data.append(row[i])
        organize_data.append(store_data)
    organize_data = np.array(organize_data) #정형화

    #테스트 데이터 정형화
    real_data_scaled = sc_x.transform(organize_data)
    real_data_scaled = np.reshape(real_data_scaled, (real_data_scaled.shape[0], real_data_scaled.shape[1], 1))


    # 테스트 데이터로 값 예측
    predicted_solar_value = loaded_model.predict(real_data_scaled)
    predicted_solar_value = sc_y.inverse_transform(predicted_solar_value)


    aver_calc = 0
    for i in range (len(organize_data)): # 예측한 데이터를 출력하고 DB에 삽입
        if (len(organize_data) == 3):
            predicted_value = round(predicted_solar_value[i][0], 3)
            values = f'predict_solar_power = {predicted_value}'
            sql = f'UPDATE weather_storage_Day SET {values} WHERE Date = "{date_arr[i+1]}" AND Location_code = {Location_code};'
            apidb.dbconfreeupdate(sql)
            upd += 1
        else:
            predicted_value = round(predicted_solar_value[i][0], 3)
            values = f'predict_solar_power = {predicted_value}'
            sql = f'UPDATE weather_storage_Day SET {values} WHERE Date = "{date_arr[i]}" AND Location_code = {Location_code};'
            apidb.dbconfreeupdate(sql)
            upd += 1
print(get_time.get_today("-"), get_time.get_now_time(), "PREDICT_RATE :", upd, "AREA COUNT", area_count) #log확인용
