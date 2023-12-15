import apidb
import get_time
import unit_change
import update_device
'''
예측된 일사량으로 해당 패널의 발전량 계산
'''

#등록된 기기의 위치 정보를 가져온다
Area_list = update_device.get_device_list()
table = "measurement" # 저장할 테이블
upd_count = 0 # 업데이트 횟수
ins_count = 0 # INSERT 횟수

#저장된 기기 각각 실행
for get_area in Area_list:
    device_ID = get_area[0] # 계산할 패널의 정보
    val = apidb.dbconfreeselect(f'SELECT area, Location_code, efficiency FROM device WHERE device_ID = "{device_ID}"') # 패널의 정보 획득
    panel_area = val[0][0]; Location_code = val[0][1]; panel_efficiency = val[0][2]# 면적, 지역코드, 패널 효율

    for i in range(3):
        target_date = get_time.get_after_date(i) 
        sql_date = get_time.get_after_date_line(i) # SQL문에 사용할 날짜
        sql = f'SELECT predict_solar_power FROM weather_storage_Day WHERE Date = "{target_date}" AND Location_code = {Location_code}'
        predict_solar = apidb.dbconfreeselect(sql)[0][0] # 해당일의 일사량 저장
        predict_out = unit_change.change_MJ_to_W(predict_solar * panel_area * panel_efficiency) # 계산된 측정값을 MJ단위에서 W단위로 변환 저장
        
        check = f'measure_date = "{sql_date}" AND device_ID = "{device_ID}"'
        stat = apidb.dbcon_check_select(table, check)[0][0] #값이 있는지 없는지 체크
        if (stat == 1): # 값이 있으면 UPDATE 실행
            UPDATE_VALUES = f"predictive_measure = {predict_out}"
            UPDATE_SQL = f'UPDATE {table} SET {UPDATE_VALUES} WHERE measure_date = "{sql_date}" AND device_ID = "{device_ID}"'
            apidb.dbconfreeupdate(UPDATE_SQL)
            upd_count += 1
        elif (stat == 0): # 값이 없으면 INSERT 실행
            INSERT_SQL = f'"{device_ID}", "{sql_date}", 0, {predict_out}, 0, 0'
            apidb.dbconinsert(table, INSERT_SQL)
            ins_count += 1
        else:
            print("ERROR")

print(f"{get_time.get_today('-')} {get_time.get_now_time()}, UPDATE RATE : {upd_count}, INSERT RATE : {ins_count}")
