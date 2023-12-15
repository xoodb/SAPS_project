import update.apidb as apidb
'''
등록된 기기의 정보를 가져오는 함수
'''
DB_list = apidb.dbconfreeselect(f"SELECT device_ID, Location_code FROM device;")
Device_list = []

for i in DB_list:
    Device_list.append([i[0], i[1]])

def get_device_list(): #기기 리스트 반환
    return Device_list

def get_device_area(location_code): #기기의 Location_code를 반환
    area = apidb.dbconfreeselect(f'SELECT area FROM xytable WHERE Location_code = {location_code}')
    return area

def get_Coordinates_Location_code(location_code): #기기의 경도 위도를 반환
    Coordinates = apidb.dbconfreeselect(f"SELECT `Latitude_sec/100`, `longitude_sec/100` FROM xytable WHERE Location_code = {location_code}")
    return Coordinates