'''
단위 변환 코드 모음
''' 

def change_W_to_KW(w):
    kw = w / 1000
    return round(kw, 3) #소수점 셋째자리 아래론 반올림

def change_W_TO_MJ(w):
    mj = w * 0.0036
    return round(mj, 3)

def change_KW_to_W(kw):
    w = kw * 1000
    return round(w, 3)

def change_KW_TO_MJ(kw):
    mj = change_KW_to_W(kw) * 0.0036
    return round(mj, 3)

def change_MJ_to_W(mj):
    w = change_MJ_to_KW(mj) * 1000
    return round(w, 3)

def change_MJ_to_KW(mj):
    kw = mj / 3.6
    return round(kw, 5)