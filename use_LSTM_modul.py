import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import load_model
import apidb
import get_time

'''
학습된 LSTM모델을 불러와 특성들을 넣어 그에 따른 일사량 예측량 추출 
'''

loaded_model = load_model('SAPS_lstm_model_1.h5')

# 데이터 파일 읽어오기
train_data = pd.read_csv('weather_data_train.csv', encoding='euc-kr')
data = train_data.drop('날짜', axis=1) #날짜 컬럼 제거
#training_set = df.iloc[:, 9:10].values #2556개 일사량값만
X_train = data.iloc[:, :-1].values #독립변수
y_train = data.iloc[:, -1].values #종속변수
y_train = y_train.reshape(-1, 1) #2차원으로 변형
#일사량값 0~1사이로 정규화
sc_x = MinMaxScaler() #입력값
X_train_scaled = sc_x.fit_transform(X_train)
sc_y = MinMaxScaler() #출력값
y_train_scaled = sc_y.fit_transform(y_train)
#정규화 범위를 지정해주기 위해서 테스트 데이터도 호출

#테스트 데이터 불러오기
date_arr = []
for i in range (0, 4): #어제부터 2일 뒤까지 4일의 날짜값
    date_arr.append(get_time.get_after_date(i - 1))
#처음과 마지막 날짜 사이의 값을 추출
sql = f"select sunrise, sunset, Min_temp, Max_Temp, Rainfall, Wind_speed, Humidity, Cloud from weather_storage_Day WHERE Date BETWEEN {date_arr[0]} AND {date_arr[-1]}"
data = apidb.dbconfreeselect(sql)
data_arr = np.array(data) #정형화


#테스트 데이터 정형화
real_data_scaled = sc_x.transform(data_arr)
real_data_scaled = np.reshape(real_data_scaled, (real_data_scaled.shape[0], real_data_scaled.shape[1], 1))


# 테스트 데이터로 값 예측
predicted_solar_value = loaded_model.predict(real_data_scaled)
predicted_solar_value = sc_y.inverse_transform(predicted_solar_value)


aver_calc = 0
for i in range (len(data_arr)): # 예측한 데이터를 출력하고 DB에 삽입
    predicted_value = round(predicted_solar_value[i][0], 3)
    values = f'predict_solar_power = {predicted_value}'
    sql = f'UPDATE weather_storage_Day SET {values} WHERE Date = "{date_arr[i]}";'
    apidb.dbconfreeupdate(sql)
    print(date_arr[i], "예측값 :", predicted_value, " | ", end='') #log확인용
