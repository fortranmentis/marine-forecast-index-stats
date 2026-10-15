# -*- coding: utf-8 -*-
"""
Created on Mon Auh 26 14:33:03 2024

@author: sang
"""


import pandas as pd
import numpy as np
import os
import warnings
# 경고창 숨기기
warnings.filterwarnings('ignore') 


# 파일을 읽어오는 함수
def read_file(file_name):
    if os.path.exists(file_name):
        return pd.read_excel(file_name)
    else:
        print(f"{file_name}이(가) 존재하지 않습니다.")
#        return None
        return pd.DataFrame(columns=["생산일", "강수량", "해상특보", "육상특보", "특보"])
    

# 각 파일에 대해 읽기 시도
sdm = read_file('sdmod.xlsx')
sdo = read_file('sdorg.xlsx')
sfm = read_file('sfmod.xlsx')
sfo = read_file('sforg.xlsx')
skm = read_file('skmod.xlsx')
sko = read_file('skorg.xlsx')
srm = read_file('srmod.xlsx')
sro = read_file('srorg.xlsx')
tlm = read_file('tlmod.xlsx')
tlo = read_file('tlorg.xlsx')
spm = read_file('spmod.xlsx')
spo = read_file('sporg.xlsx')
ssm = read_file('ssmod.xlsx')
sso = read_file('ssorg.xlsx')

# 데이터프레임 처리 함수
def process_dataframe(df, columns):
    if df is not None:
        return df[columns].replace('-', np.nan)
    return None

sdmA = process_dataframe(sdm, ["생산일","강수량","해상특보","육상특보"])
sfmA = process_dataframe(sfm, ["생산일","해상특보","육상특보"])
skmA = process_dataframe(skm, ["생산일","특보"])
srmA = process_dataframe(srm, ["생산일","해상특보","육상특보"])
tlmA = process_dataframe(tlm, ["생산일","강수량","해상특보","육상특보"])
spmA = process_dataframe(spm, ["생산일","강수량","해상특보","육상특보"])
ssmA = process_dataframe(ssm, ["생산일","해상특보","육상특보"])

# 데이터프레임 필터링 함수
def filter_dataframe(df, condition):
    if df is not None:
        return df[df.apply(lambda x: condition(x), axis=1)].drop_duplicates('생산일')
    return None

# 각 데이터프레임에 대한 필터링
if sdmA is not None:
    WW_sdmA = filter_dataframe(sdmA, lambda x: x['해상특보'] in ['WW1','WW2','WW3'])
    TY_sdmA = filter_dataframe(sdmA, lambda x: x['해상특보'] in ['TY1','TY2','TY3'])
    RD_sdmA = filter_dataframe(sdmA, lambda x: pd.notnull(x['강수량']) and int(x['강수량']) > 0)
    SS_sdmA = filter_dataframe(sdmA, lambda x: x['육상특보'] in ['SS1','SS2','SS3'])
    SR_sdmA = filter_dataframe(sdmA, lambda x: x['육상특보'] in ['SR1','SR2','SR3'])

if sfmA is not None:
    WW_sfmA = filter_dataframe(sfmA, lambda x: x['해상특보'] in ['WW1','WW2','WW3'])
    TY_sfmA = filter_dataframe(sfmA, lambda x: x['해상특보'] in ['TY1','TY2','TY3'])
    SS_sfmA = filter_dataframe(sfmA, lambda x: x['육상특보'] in ['SS1','SS2','SS3'])
    SR_sfmA = filter_dataframe(sfmA, lambda x: x['육상특보'] in ['SR1','SR2','SR3'])

if skmA is not None:
    WW_skmA = filter_dataframe(skmA, lambda x: x['특보'] in ['WW1','WW2','WW3'])
    TY_skmA = filter_dataframe(skmA, lambda x: x['특보'] in ['TY1','TY2','TY3'])
    SS_skmA = filter_dataframe(skmA, lambda x: x['특보'] in ['SS1','SS2','SS3'])
    SR_skmA = filter_dataframe(skmA, lambda x: x['특보'] in ['SR1','SR2','SR3'])

if srmA is not None:
    WW_srmA = filter_dataframe(srmA, lambda x: x['해상특보'] in ['WW1','WW2','WW3'])
    TY_srmA = filter_dataframe(srmA, lambda x: x['해상특보'] in ['TY1','TY2','TY3'])
    SS_srmA = filter_dataframe(srmA, lambda x: x['육상특보'] in ['SS1','SS2','SS3'])
    SR_srmA = filter_dataframe(srmA, lambda x: x['육상특보'] in ['SR1','SR2','SR3'])

if tlmA is not None:
    WW_tlmA = filter_dataframe(tlmA, lambda x: x['해상특보'] in ['WW1','WW2','WW3'])
    TY_tlmA = filter_dataframe(tlmA, lambda x: x['해상특보'] in ['TY1','TY2','TY3'])
    RD_tlmA = filter_dataframe(tlmA, lambda x: pd.notnull(x['강수량']) and int(x['강수량']) > 0)
    SS_tlmA = filter_dataframe(tlmA, lambda x: x['육상특보'] in ['SS1','SS2','SS3'])
    SR_tlmA = filter_dataframe(tlmA, lambda x: x['육상특보'] in ['SR1','SR2','SR3'])

if spmA is not None:
    WW_spmA = filter_dataframe(spmA, lambda x: x['해상특보'] in ['WW1','WW2','WW3'])
    TY_spmA = filter_dataframe(spmA, lambda x: x['해상특보'] in ['TY1','TY2','TY3'])
    RD_spmA = filter_dataframe(spmA, lambda x: pd.notnull(x['강수량']) and int(x['강수량']) > 0)
    SS_spmA = filter_dataframe(spmA, lambda x: x['육상특보'] in ['SS1','SS2','SS3'])
    SR_spmA = filter_dataframe(spmA, lambda x: x['육상특보'] in ['SR1','SR2','SR3'])

if ssmA is not None:
    WW_ssmA = filter_dataframe(ssmA, lambda x: x['해상특보'] in ['WW1','WW2','WW3'])
    TY_ssmA = filter_dataframe(ssmA, lambda x: x['해상특보'] in ['TY1','TY2','TY3'])
    SS_ssmA = filter_dataframe(ssmA, lambda x: x['육상특보'] in ['SS1','SS2','SS3'])
    SR_ssmA = filter_dataframe(ssmA, lambda x: x['육상특보'] in ['SR1','SR2','SR3'])

# # 데이터프레임 병합 함수
# def merge_dataframes(*dfs):
#     result = None
#     for df in dfs:
#         if df is not None:
#             if result is None:
#                 result = df
#             else:
#                 result = pd.merge(result, df, on='생산일', how='outer')
#     return result


def merge_dataframes(*dfs):
    result = None
    for df in dfs:
        # '생산일' 열이 존재하는지 확인
        if df is not None and '생산일' in df.columns:
            if result is None:
                result = df
            else:
                result = pd.merge(result, df, on='생산일', how='outer')
    return result



# 데이터프레임 병합
merge_WW = merge_dataframes(WW_sdmA, WW_sfmA, WW_srmA)
merge_TY = merge_dataframes(TY_sdmA, TY_sfmA, TY_srmA)
merge_SS = merge_dataframes(SS_sdmA, SS_sfmA, SS_srmA)
merge_SR = merge_dataframes(SR_sdmA, SR_sfmA, SR_srmA)

mWW1 = merge_dataframes(merge_WW, WW_skmA, WW_tlmA)
mTY1 = merge_dataframes(merge_TY, TY_skmA, TY_tlmA)
mSS1 = merge_dataframes(merge_SS, SS_skmA, SS_tlmA)
mSR1 = merge_dataframes(merge_SR, SR_skmA, SR_tlmA)

mWW = merge_dataframes(mWW1, WW_spmA, WW_ssmA)
mTY = merge_dataframes(mTY1, TY_spmA, TY_ssmA)
mSS = merge_dataframes(mSS1, SS_spmA, SS_ssmA)
mSR = merge_dataframes(mSR1, SR_spmA, SR_ssmA)

# 데이터프레임 정렬 및 인덱스 재설정
for df in [mWW, mTY, mSS, mSR]:
    if df is not None:
        df.sort_values('생산일', inplace=True)
        df.reset_index(drop=True, inplace=True)

# 결측값 처리 함수
def fill_na(df):
    if df is not None:
        df.fillna({'해상특보': '', '육상특보': '', '특보': '', '강수량': '0'}, inplace=True)
    return df

mWW = fill_na(mWW)
mTY = fill_na(mTY)
mSS = fill_na(mSS)
mSR = fill_na(mSR)

# 특보 및 강수량 열 생성
def create_columns(df, prefix):
    if df is not None:
        df[f'해상특보{prefix}'] = df.filter(like='해상특보').fillna('').sum(axis=1)
        df[f'해상특보{prefix}'] = df.filter(like='특보').fillna('').sum(axis=1)
        df[f'육상특보{prefix}'] = df.filter(like='육상특보').fillna('').sum(axis=1)
        df[f'강수량{prefix}'] = df.filter(like='강수량').fillna(0).astype(int).sum(axis=1)
        df.drop(df.filter(regex='해상특보_|육상특보_|특보_|강수량_').columns, axis=1, inplace=True)
    return df

mWW = create_columns(mWW, 'WW')
mTY = create_columns(mTY, 'TY')
mSS = create_columns(mSS, 'SS')
mSR = create_columns(mSR, 'SR')

# 최종 데이터프레임 병합
merge_all = merge_dataframes(RD_sdmA, mWW, mTY, mSS, mSR, RD_tlmA, RD_spmA)
#merge_all.drop(merge_all.filter(regex='해상특보_|육상특보_|특보_|강수량_').columns, axis=1, inplace=True)
강수량_cols = [col for col in merge_all.columns if '강수량' in col]
merge_all['강수량'] = merge_all[강수량_cols].fillna(0).sum(axis=1)
merge_all['강수량'] = merge_all['강수량'].replace(0, np.nan)
merge_all.drop(merge_all.filter(regex='해상특보_|육상특보_|특보_|강수량_|강수량WW|강수량TY|강수량SS|강수량SR').columns, axis=1, inplace=True)
# 통계 계산 및 결과 출력 부분
if merge_all is not None:
    count_day = merge_all['생산일'].count()
    count_WW = merge_all['해상특보WW'].count()
    count_TY = merge_all['해상특보TY'].count()
    count_SS = merge_all['육상특보SS'].count()
    count_SR = merge_all['육상특보SR'].count()
    count_RD = merge_all['강수량'].count()
    
    count_TYWW = merge_all[(merge_all['해상특보WW'].notnull()) & (merge_all['해상특보TY'].notnull())]['해상특보WW'].count()
    count_TYSS = merge_all[(merge_all['육상특보SS'].notnull()) & (merge_all['해상특보TY'].notnull())]['육상특보SS'].count()
    count_TYSR = merge_all[(merge_all['육상특보SR'].notnull()) & (merge_all['해상특보TY'].notnull())]['육상특보SR'].count()
    count_WWSS = merge_all[(merge_all['해상특보WW'].notnull()) & (merge_all['육상특보SS'].notnull())]['해상특보WW'].count()
    count_WWSR = merge_all[(merge_all['해상특보WW'].notnull()) & (merge_all['육상특보SR'].notnull())]['해상특보WW'].count()
    count_SSSR = merge_all[(merge_all['육상특보SS'].notnull()) & (merge_all['육상특보SR'].notnull())]['육상특보SS'].count()
    count_TYRD = merge_all[(merge_all['해상특보TY'].notnull()) & (merge_all['강수량'].notnull())]['해상특보TY'].count()
    count_WWRD = merge_all[(merge_all['해상특보WW'].notnull()) & (merge_all['강수량'].notnull())]['해상특보WW'].count()
    count_SSRD = merge_all[(merge_all['육상특보SS'].notnull()) & (merge_all['강수량'].notnull())]['육상특보SS'].count()
    count_SRRD = merge_all[(merge_all['육상특보SR'].notnull()) & (merge_all['강수량'].notnull())]['육상특보SR'].count()
    
    count_TYWWSS = merge_all[(merge_all['해상특보WW'].notnull()) & (merge_all['해상특보TY'].notnull()) & (merge_all['육상특보SS'].notnull())]['해상특보WW'].count()
    count_TYWWSR = merge_all[(merge_all['해상특보WW'].notnull()) & (merge_all['해상특보TY'].notnull()) & (merge_all['육상특보SR'].notnull())]['해상특보WW'].count()
    count_TYWWRD = merge_all[(merge_all['해상특보WW'].notnull()) & (merge_all['해상특보TY'].notnull()) & (merge_all['강수량'].notnull())]['해상특보WW'].count()
    count_TYSSSR = merge_all[(merge_all['육상특보SS'].notnull()) & (merge_all['해상특보TY'].notnull()) & (merge_all['육상특보SR'].notnull())]['육상특보SS'].count()
    count_TYSSRD = merge_all[(merge_all['육상특보SS'].notnull()) & (merge_all['해상특보TY'].notnull()) & (merge_all['강수량'].notnull())]['육상특보SS'].count()
    count_TYSRRD = merge_all[(merge_all['육상특보SR'].notnull()) & (merge_all['해상특보TY'].notnull()) & (merge_all['강수량'].notnull())]['육상특보SR'].count()
    count_WWSSSR = merge_all[(merge_all['해상특보WW'].notnull()) & (merge_all['육상특보SS'].notnull()) & (merge_all['육상특보SR'].notnull())]['해상특보WW'].count()
    count_WWSSRD = merge_all[(merge_all['해상특보WW'].notnull()) & (merge_all['육상특보SS'].notnull()) & (merge_all['강수량'].notnull())]['해상특보WW'].count()
    count_WWSRRD = merge_all[(merge_all['해상특보WW'].notnull()) & (merge_all['육상특보SR'].notnull()) & (merge_all['강수량'].notnull())]['해상특보WW'].count()
    count_SSSRRD = merge_all[(merge_all['육상특보SS'].notnull()) & (merge_all['육상특보SR'].notnull()) & (merge_all['강수량'].notnull())]['육상특보SS'].count()
    
    count_TYWWSSSR = merge_all[(merge_all['해상특보WW'].notnull()) & (merge_all['해상특보TY'].notnull()) & (merge_all['육상특보SS'].notnull()) & (merge_all['육상특보SR'].notnull())]['해상특보WW'].count()
    count_TYWWSSRD = merge_all[(merge_all['해상특보WW'].notnull()) & (merge_all['해상특보TY'].notnull()) & (merge_all['육상특보SS'].notnull()) & (merge_all['강수량'].notnull())]['해상특보WW'].count()
    count_TYWWSRRD = merge_all[(merge_all['해상특보WW'].notnull()) & (merge_all['해상특보TY'].notnull()) & (merge_all['육상특보SR'].notnull()) & (merge_all['강수량'].notnull())]['해상특보WW'].count()
    count_TYSSSRRD = merge_all[(merge_all['육상특보SS'].notnull()) & (merge_all['해상특보TY'].notnull()) & (merge_all['육상특보SR'].notnull()) & (merge_all['강수량'].notnull())]['육상특보SS'].count()
    count_WWSSSRRD = merge_all[(merge_all['해상특보WW'].notnull()) & (merge_all['육상특보SS'].notnull()) & (merge_all['육상특보SR'].notnull()) & (merge_all['강수량'].notnull())]['해상특보WW'].count()
    
    count_TYWWSSSRRD = merge_all[(merge_all['해상특보WW'].notnull()) & (merge_all['해상특보TY'].notnull()) & (merge_all['육상특보SS'].notnull()) & (merge_all['육상특보SR'].notnull()) & (merge_all['강수량'].notnull())]['해상특보WW'].count()

    def calculate_percentage(count):
        return round(count / count_day * 100, 1) if count_day != 0 else 0

    print("생산일 :", count_day, "일")
    print("태풍 :", count_TY, "일,", calculate_percentage(count_TY), '%')
    print("풍랑 :", count_WW, "일,", calculate_percentage(count_WW), '%')
    print("폭풍해일 :", count_SS, "일,", calculate_percentage(count_SS), '%')
    print("호우 :", count_SR, "일,", calculate_percentage(count_SR), '%')
    print("강수일 :", count_RD, "일,", calculate_percentage(count_RD), '%')

    print("태풍&풍랑 :", count_TYWW, "일,", calculate_percentage(count_TYWW), '%')
    print("태풍&폭풍해일 :", count_TYSS, "일,", calculate_percentage(count_TYSS), '%')
    print("태풍&호우 :", count_TYSR, "일,", calculate_percentage(count_TYSR), '%')
    print("태풍&강수 :", count_TYRD, "일,", calculate_percentage(count_TYRD), '%')
    print("풍랑&폭풍해일 :", count_WWSS, "일,", calculate_percentage(count_WWSS), '%')
    print("풍랑&호우 :", count_WWSR, "일,", calculate_percentage(count_WWSR), '%')
    print("풍랑&강수 :", count_WWRD, "일,", calculate_percentage(count_WWRD), '%')
    print("폭풍해일&호우 :", count_SSSR, "일,", calculate_percentage(count_SSSR), '%')
    print("폭풍해일&강수 :", count_SSRD, "일,", calculate_percentage(count_SSRD), '%')
    print("호우&강수 :", count_SRRD, "일,", calculate_percentage(count_SRRD), '%')

    print("태풍&풍랑&폭풍해일 :", count_TYWWSS, "일,", calculate_percentage(count_TYWWSS), '%')
    print("태풍&풍랑&호우 :", count_TYWWSR, "일,", calculate_percentage(count_TYWWSR), '%')
    print("태풍&풍랑&강수 :", count_TYWWRD, "일,", calculate_percentage(count_TYWWRD), '%')
    print("태풍&폭풍해일&호우 :", count_TYSSSR, "일,", calculate_percentage(count_TYSSSR), '%')
    print("태풍&폭풍해일&강수 :", count_TYSSRD, "일,", calculate_percentage(count_TYSSRD), '%')
    print("태풍&호우&강수 :", count_TYSRRD, "일,", calculate_percentage(count_TYSRRD), '%')
    print("풍랑&폭풍해일&호우 :", count_WWSSSR, "일,", calculate_percentage(count_WWSSSR), '%')
    print("풍랑&폭풍해일&강수 :", count_WWSSRD, "일,", calculate_percentage(count_WWSSRD), '%')
    print("풍랑&호우&강수 :", count_WWSRRD, "일,", calculate_percentage(count_WWSRRD), '%')
    print("폭풍해일&호우&강수 :", count_SSSRRD, "일,", calculate_percentage(count_SSSRRD), '%')

    print("태풍&풍랑&폭풍해일&호우 :", count_TYWWSSSR, "일,", calculate_percentage(count_TYWWSSSR), '%')
    print("태풍&풍랑&폭풍해일&강수 :", count_TYWWSSRD, "일,", calculate_percentage(count_TYWWSSRD), '%')
    print("태풍&풍랑&호우&강수 :", count_TYWWSRRD, "일,", calculate_percentage(count_TYWWSRRD), '%')
    print("태풍&폭풍해일&호우&강수 :", count_TYSSSRRD, "일,", calculate_percentage(count_TYSSSRRD), '%')
    print("풍랑&폭풍해일&호우&강수 :", count_WWSSSRRD, "일,", calculate_percentage(count_WWSSSRRD), '%')

    print("태풍&풍랑&폭풍해일&호우&강수 :", count_TYWWSSSRRD, "일,", calculate_percentage(count_TYWWSSSRRD), '%')

else:
    print("처리할 데이터가 없습니다.")




