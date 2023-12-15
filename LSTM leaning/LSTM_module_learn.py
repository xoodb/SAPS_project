import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout

'''
LSTM 모델 학습시켜서 모델 생성
'''

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

# 3차원 배열 변환
X_train_scaled = np.reshape(X_train_scaled, (X_train_scaled.shape[0], X_train_scaled.shape[1], 1)) 
#(batcho size - 행개수, timestep - 열개수, 3차원 개수)
#순환 신경망 구성
regressor = Sequential() #초기화


memory_cell = 128 #뉴런의 수

#첫번째 LSTM layer
regressor.add(LSTM(units = 11, activation='tanh', return_sequences = True, input_shape = (X_train_scaled.shape[1], 1)))
regressor.add(Dropout(0.1)) #과적합을 피하기 위해 사용

#두번째 LSTM layer
regressor.add(LSTM(units = memory_cell, activation='tanh', return_sequences = True))
regressor.add(Dropout(0.1))

#네번째 LSTM layer
regressor.add(LSTM(units = memory_cell, activation='tanh'))
regressor.add(Dropout(0.1))

#출력층 추가
regressor.add(Dense(units = 1, activation='relu')) #차원의 개수
regressor.compile(optimizer = 'adam', loss = 'mean_squared_error')
# optimizer로 adam사용, 손실함수는 mean_squared_error

#LSTM 훈련시키기
regressor.fit(X_train_scaled, y_train_scaled, epochs = 256, batch_size = 16)

#모델 저장
regressor.save('SAPS_lstm_model_1.h5')

#테스트 데이터 불러오기
dataset_test = pd.read_csv('weather_data_test.csv', encoding='euc-kr')
date = dataset_test.iloc[:, :1].values #날짜 획득
dataset_test = dataset_test.drop('날짜', axis=1)
real_data = dataset_test.iloc[:, :-1].values #독립변수
real_value = dataset_test.iloc[:, -1].values #종속변수
date_val = [] # 테스트 데이터 날짜마다 확인하기 위해 저장
for i in range (len(date)):
    date_val.append(date[i])

#테스트 데이터 정형화
sc_x.fit(real_data)
real_data_scaled = sc_x.transform(real_data)
real_data_scaled = np.reshape(real_data_scaled, (real_data_scaled.shape[0], real_data_scaled.shape[1], 1))

# 테스트 데이터로 값 예측
predicted_solar_value = regressor.predict(real_data_scaled)
predicted_solar_value = sc_y.inverse_transform(predicted_solar_value) #정형화된 값 다시 원래값으로 바꾸기

'''
#아래는 출력값 확인
'''
aver_calc = 0
for i in range (len(real_value)):
    calc = (float(predicted_solar_value[i][0]) / float(real_value[i])) * 100
    print(date_val[i], "실제값 :", real_value[i], "예측값 :", predicted_solar_value[i][0], "정확도 :", calc )
    aver_calc += calc
print("평균 정확도 : ", round(aver_calc / len(real_value), 3))

# 그래프로 결과 가시화
plt.plot(real_value, color = 'red', label = 'Real')
plt.plot(predicted_solar_value, color = 'blue', label = 'Predicted')
plt.title('Solar Prediction')
plt.xlabel('Date')
plt.ylabel('solar')
plt.legend()
plt.show()
