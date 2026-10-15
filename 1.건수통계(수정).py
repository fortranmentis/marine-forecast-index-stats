# -*- coding: utf-8 -*-
"""
Created on Mon Auh 26 14:33:03 2024

@author: sang
"""


#mod=서비스
#org=예측


import pandas as pd
import numpy as np
import os
import warnings
# 경고창 숨기기
warnings.filterwarnings('ignore') 


print()
print()
# 파일 존재 여부 확인

mod_file = 'sdmod.xlsx'
org_file = 'sdorg.xlsx'

if not os.path.exists(mod_file) or not os.path.exists(org_file):
    print('SD자료가 없습니다')
else:
    sdm = pd.read_excel('sdmod.xlsx')
    sdo = pd.read_excel('sdorg.xlsx')
    
    SD_row = sdm.shape[0]
    
    # 같은 요소의 개수와 같은 권역의 개수를 세는 작업
    grouped = sdm.groupby(['권역', '지역']).size().reset_index(name='총 예보건수')
    
    # 권역 요소별 총합 계산
    grouped_sum = grouped.groupby('권역')['총 예보건수'].sum().reset_index(name='총 예보건수')
    
    
    # 권역 요소 아래에 총합 행 추가
    result = pd.concat([grouped, grouped_sum])
    
    SD_new_order3 = ['황해중부', '황해남부', '제주도','남해서부','남해동부','동해남부','동해중부']
    result['권역'] = pd.Categorical(result['권역'], categories=SD_new_order3, ordered=True)
    result = result.sort_values(['권역','지역']).reset_index(drop=True)
    
    # 권역 열의 맨 아래에 총합 위치
    result.loc[result['지역'] == '총합', '권역'] = np.nan
    result = result.fillna('A')
    SD_loc_row = result
    
    
    sdo['해상특보']=''
    sdo['육상특보']=''
    sdo['특보점수']=''
    
    sdm1 = sdm[["생산일","권역","지역","기온점수","풍속점수","날씨점수","해상특보","육상특보","특보점수","예보지수"]]
    sdo1 = sdo[["생산일","권역","지역","기온점수","풍속점수","날씨점수","해상특보","육상특보","특보점수","예보지수"]]
    
    compare = sdm1['예보지수'] == sdo1['예보지수']
    csdm = sdm1[~compare]
    csdo = sdo1[~compare]
    
    
    different_row_sd = (sdm1['예보지수'] != sdo1['예보지수']).sum()
    
    csdm_c = csdm.copy()
    
    csdm_c['강수량']=sdm["강수량"]
    csdm_c['강수점수']=sdm["강수점수"]
    
    csdm_c = csdm_c.sort_values(by=['권역','지역'], ascending=[True, True])
    csdo = csdo.sort_values(by=['권역','지역'], ascending=[True, True])
    
    csdm_c.rename(columns={'기온점수':'기온점수m'},inplace=True)
    csdo.rename(columns={'기온점수':'기온점수o'},inplace=True)
    csdm_c.rename(columns={'풍속점수':'풍속점수m'},inplace=True)
    csdo.rename(columns={'풍속점수':'풍속점수o'},inplace=True)
    csdm_c.rename(columns={'날씨점수':'날씨점수m'},inplace=True)
    csdo.rename(columns={'날씨점수':'날씨점수o'},inplace=True)
    csdm_c.rename(columns={'예보지수':'예보지수m'},inplace=True)
    csdo.rename(columns={'예보지수':'예보지수o'},inplace=True)
    
    sd_result = pd.concat([csdm_c,csdo],axis=1)
    
    # 중복된 열을 제거하여 유일한 값을 가지도록 만듦
    sd_result = sd_result.loc[:, ~sd_result.columns.duplicated(keep='first')]
    
    # 컬럼 순서 변경
    sd_result = sd_result[['생산일', '권역', '지역', '기온점수m','기온점수o','풍속점수m','풍속점수o','날씨점수m','날씨점수o','강수량','강수점수','해상특보','육상특보','특보점수','예보지수m','예보지수o']]
    sd_result = sd_result.reset_index(drop=True)
    sd_result.index = sd_result.index + 1
    
    # 셀 색칠 함수
    def highlight_diff(x, color):
        style = 'background-color: {}'.format(color)
        if x[0] != x[1]:
            return [style, style]
        else:
            return ['', '']
    
    def highlight_special_R(row):
        if row.name == '강수량':
            return ['background-color: orange' if x != '-' else '' for x in row]
        else:
            return [''] * len(row)
    
    def highlight_special_sea(row):
        if row.name == '해상특보':
            return ['background-color: green' if x != '-' else '' for x in row]
        else:
            return [''] * len(row)
    def highlight_special_land(row):
        if row.name == '육상특보':
            return ['background-color: cyan' if x != '-' else '' for x in row]
        else:
            return [''] * len(row) 
    
    # 열 비교하여 값이 다른 경우 해당 셀 색칠
    sd_html = sd_result.style.apply(highlight_diff, color='yellow', axis=1, subset=['기온점수m', '기온점수o']) \
                  .apply(highlight_diff, color='blue', axis=1, subset=['풍속점수m', '풍속점수o']) \
                  .apply(highlight_diff, color='red', axis=1, subset=['날씨점수m', '날씨점수o']) \
                  .apply(lambda x: highlight_special_R(x), axis=0) \
                  .apply(lambda x: highlight_special_sea(x), axis=0) \
                  .apply(lambda x: highlight_special_land(x), axis=0) \
                  .set_properties(**{'border': '1px solid black'})
    
    # 스타일이 적용된 데이터프레임을 HTML 파일로 저장
    with open('갈라짐.html', 'w') as f:
        f.write(sd_html.to_html())
        
    # 스타일이 적용된 데이터프레임을 xlsx 파일로 저장
    sd_html.to_excel('갈라짐.xlsx', index=True)
    
    #각 권역의 갯수, 각 지역의 갯수, 각 변경요인 갯수
    sd_loc = sd_result['권역'].value_counts().sort_index().to_frame(name='횟수').reset_index().rename(columns={'index': '권역'})
    sd_locp = sd_result.groupby(['권역', '지역'])['지역'].count().reset_index(name='횟수')
    
    #각 권역의 각각의 변경요인 갯수
    #각 지역의 각각의 변경요인 갯수
    def count_changes_SD1(df, groupby_col, sea_warn_col='해상특보', land_warn_col='육상특보', rain_col='강수량'):
        count = df.groupby(groupby_col).apply(lambda x: pd.Series({'기온점수count': (x['기온점수m'] != x['기온점수o']).sum(),
                                                                      '풍속점수count': (x['풍속점수m'] != x['풍속점수o']).sum(),
                                                                      '날씨점수count': (x['날씨점수m'] != x['날씨점수o']).sum(),
                                                                      '태풍&강수count': ((x[sea_warn_col].isin(['TY1','TY2','TY3','TY'])) & (x[rain_col] != '-')).sum(),
                                                                      '폭우&강수count': ((x[land_warn_col].isin(['SR2', 'SR3','SR1','SR'])) & (x[rain_col] != '-')).sum(),
                                                                      '폭풍해일&강수count': ((x[land_warn_col].isin(['SS2', 'SS3', 'SS1', 'SS'])) & (x[rain_col] != '-')).sum(),})).reset_index()
    
        #해상 특보와 육상 특보에 대한 필터링 및 경고 횟수 계산
        sea_warn = df[df[sea_warn_col] != '-'].groupby(groupby_col + [sea_warn_col]).size().reset_index(name=sea_warn_col+'count')
        land_warn = df[df[land_warn_col].isin(['SR2', 'SR1','SR3','SS2', 'SS3','SS1'])].groupby(groupby_col + [land_warn_col]).size().reset_index(name=land_warn_col+'count')
        #피벗 테이블 생성
        sea_pivot = sea_warn.pivot_table(index=groupby_col, columns=sea_warn_col, values=sea_warn_col+'count', fill_value=0).reset_index()
        land_pivot = land_warn.pivot_table(index=groupby_col, columns=land_warn_col, values=land_warn_col+'count', fill_value=0).reset_index()
    
        #경고 횟수 데이터를 count DataFrame에 추가
        count = count.merge(sea_pivot, on=groupby_col, how='left').fillna(0)
        count = count.merge(land_pivot, on=groupby_col, how='left').fillna(0)
        
        rain = df[df[rain_col].astype(int) > 0].groupby(groupby_col + [rain_col]).size().reset_index(name=rain_col+'count')
        rain_pivot = rain.pivot_table(index=groupby_col, columns=rain_col, values=rain_col+'count', fill_value=0).reset_index()
        rain_pivot[rain_col+'count'] = rain_pivot[rain_pivot.columns[1:]].sum(axis=1)
        rain_pivot = rain_pivot.drop(columns=rain_pivot.columns[1:-1])
        count = count.merge(rain_pivot, on=groupby_col, how='left').fillna(0)
        return count
    
    def count_changes_SD2(df, groupby_col, sea_warn_col='해상특보', land_warn_col='육상특보', rain_col='강수량'):
        count = df.groupby(groupby_col).apply(lambda x: pd.Series({'기온점수count': (x['기온점수m'] != x['기온점수o']).sum(),
                                                                      '풍속점수count': (x['풍속점수m'] != x['풍속점수o']).sum(),
                                                                      '날씨점수count': (x['날씨점수m'] != x['날씨점수o']).sum(),
                                                                      '태풍&강수count': ((x[sea_warn_col] != '-') & (x[rain_col] != '-')).sum(),
                                                                      '폭우&강수count': ((x[land_warn_col].isin(['SR2', 'SR3', 'SR1'])) & (x[rain_col] != '-')).sum(),
                                                                      '폭풍해일&강수count': ((x[land_warn_col].isin(['SS2', 'SS3', 'SS1'])) & (x[rain_col] != '-')).sum(),})).reset_index()
    
        #해상 특보와 육상 특보에 대한 필터링 및 경고 횟수 계산
        sea_warn = df[df[sea_warn_col] != '-'].groupby(groupby_col + [sea_warn_col]).size().reset_index(name=sea_warn_col+'count')
        land_warn = df[df[land_warn_col].isin(['SR2', 'SR3', 'SR1','SS2', 'SS3', 'SS1'])].groupby(groupby_col + [land_warn_col]).size().reset_index(name=land_warn_col+'count')
        #피벗 테이블 생성
        sea_pivot = sea_warn.pivot_table(index=groupby_col, columns=sea_warn_col, values=sea_warn_col+'count', fill_value=0).reset_index()
        land_pivot = land_warn.pivot_table(index=groupby_col, columns=land_warn_col, values=land_warn_col+'count', fill_value=0).reset_index()
    
        #경고 횟수 데이터를 count DataFrame에 추가
        count = count.merge(sea_pivot, on=groupby_col, how='left').fillna(0)
        count = count.merge(land_pivot, on=groupby_col, how='left').fillna(0)
        
        rain = df[df[rain_col].astype(int) > 0].groupby(groupby_col + [rain_col]).size().reset_index(name=rain_col+'count')
        rain_pivot = rain.pivot_table(index=groupby_col, columns=rain_col, values=rain_col+'count', fill_value=0).reset_index()
        rain_pivot[rain_col+'count'] = rain_pivot[rain_pivot.columns[1:]].sum(axis=1)
        rain_pivot = rain_pivot.drop(columns=rain_pivot.columns[2:-1])
        count = count.merge(rain_pivot, on=groupby_col, how='left').fillna(0)
        return count
    
    
    count2_sd1 = count_changes_SD1(sd_result, ['권역'])
    count2_sd1 = count2_sd1.groupby('권역').agg('sum').reset_index()
    count2_sd2 = count_changes_SD2(sd_result, ['권역', '지역'])
    
    
    
    # WW2와 WW3열이 모두 존재하는 경우에만 WW2와 WW3열을 합쳐서 WW열로 만듦
    # TY2와 TY3열이 모두 존재하는 경우에만 TY2와 TY3열을 합쳐서 TY열로 만듦
    def combine_columns(df, col1, col2, new_col):
        if col1 in df.columns and col2 in df.columns:
            df[new_col] = df[col1] + df[col2]
            df.drop([col1, col2], axis=1, inplace=True)
        elif col1 in df.columns:
            df[new_col] = df[col1]
            df.drop([col1], axis=1, inplace=True)
        elif col2 in df.columns:
            df[new_col] = df[col2]
            df.drop([col2], axis=1, inplace=True)
        else:
            df[new_col] = 0
        return df
    
    count2_sd1 = combine_columns(count2_sd1, 'WW2', 'WW3', 'WW_1')
    count2_sd2 = combine_columns(count2_sd2, 'WW2', 'WW3', 'WW_1')
    count2_sd1 = combine_columns(count2_sd1, 'TY2', 'TY3', 'TY_1')
    count2_sd2 = combine_columns(count2_sd2, 'TY2', 'TY3', 'TY_1')
    count2_sd1 = combine_columns(count2_sd1, 'SS2', 'SS3', 'SS_1')
    count2_sd2 = combine_columns(count2_sd2, 'SS2', 'SS3', 'SS_1')
    count2_sd1 = combine_columns(count2_sd1, 'SR2', 'SR3', 'SR_1')
    count2_sd2 = combine_columns(count2_sd2, 'SR2', 'SR3', 'SR_1')
    
    count2_sd1 = combine_columns(count2_sd1, 'SR_1', 'SR1', 'SR')
    count2_sd2 = combine_columns(count2_sd2, 'SR_1', 'SR1', 'SR')
    count2_sd1 = combine_columns(count2_sd1, 'WW_1', 'WW1', 'WW')
    count2_sd2 = combine_columns(count2_sd2, 'WW_1', 'WW1', 'WW')    
    count2_sd1 = combine_columns(count2_sd1, 'TY_1', 'TY1', 'TY')
    count2_sd2 = combine_columns(count2_sd2, 'TY_1', 'TY1', 'TY')
    count2_sd1 = combine_columns(count2_sd1, 'SS_1', 'SS1', 'SS')
    count2_sd2 = combine_columns(count2_sd2, 'SS_1', 'SS1', 'SS')


    
    count2_sd2 = count2_sd2.groupby(['권역', '지역']).sum().reset_index()
    
    
    count2_sd1 = pd.merge(count2_sd1, sd_loc, on='권역')
    count2_sd2 = pd.merge(count2_sd2, sd_locp, on='지역')
    
    count2_sd1['지역'] = np.nan
    
    
    
    count2_sd2 = count2_sd2.drop('권역_y', axis=1)
    count2_sd2 = count2_sd2.rename(columns={'권역_x':'권역'})
    SD_new_order1 = ['권역', '지역','기온점수count','풍속점수count','날씨점수count', '태풍&강수count','폭풍해일&강수count','폭우&강수count','강수량count','WW','TY','SR','SS','횟수']
    count2_sd1 = count2_sd1.reindex(columns=SD_new_order1)
    count2_sd3 = pd.concat([count2_sd1, count2_sd2]).reset_index(drop=True)
    count2_sd3.sort_values(by=['권역','지역'], inplace=True)
    count2_sd3 = count2_sd3.reindex(columns=SD_new_order1)
    
    
    
    count2_sd3['권역'] = pd.Categorical(count2_sd3['권역'], categories=SD_new_order3, ordered=True)
    count2_sd3 = count2_sd3.sort_values(['권역','지역']).reset_index(drop=True)
    
    
    
    count2_sd3 = count2_sd3.fillna('A')
    
    sd_row_sum = count2_sd2["횟수"].sum()
    
    print('SD 총통계')
    sd_sum_all = count2_sd1.sum()
    sd_sum_all = pd.DataFrame(sd_sum_all, columns=['변경'])
    sd_sum_all = sd_sum_all.drop('권역', axis=0)
    sd_sum_all = sd_sum_all.rename(index={'횟수': '총예보지수변경'})
    print(sd_sum_all)
    sd_sum_all.to_csv('갈라짐_요약.csv', encoding='euc-kr', index=True)
    print('바다갈라짐 총예보건수', SD_row)
    
    
    def calculate_percentages(df, row_sum):
        df['기온%'] = round(df['기온점수count'] / row_sum * 100, 2)
        df['풍속%'] = round(df['풍속점수count'] / row_sum * 100, 2)
        df['날씨%'] = round(df['날씨점수count'] / row_sum * 100, 2)
        df['강수량%'] = round(df['강수량count'] / row_sum * 100, 2)
        df['WW%'] = round(df['WW'] / row_sum * 100, 2)
        df['TY%'] = round(df['TY'] / row_sum * 100, 2)
        df['SS%'] = round(df['SS'] / row_sum * 100, 2)
        df['SR%'] = round(df['SR'] / row_sum * 100, 2)
        df['횟수%'] = round(df['횟수'] / row_sum * 100, 2)
        df['태풍&강수%'] = round(df['태풍&강수count'] / row_sum * 100, 2)
        df['폭풍해일&강수%'] = round(df['폭풍해일&강수count'] / row_sum * 100, 2)
        df['폭우&강수%'] = round(df['폭우&강수count'] / row_sum * 100, 2)
        return df
    
    def calculate_percentages1(df, row_sum):
        df['기온%'] = round(df['기온점수count'] / row_sum['총 예보건수'] * 100, 2)
        df['풍속%'] = round(df['풍속점수count'] / row_sum['총 예보건수'] * 100, 2)
        df['날씨%'] = round(df['날씨점수count'] / row_sum['총 예보건수'] * 100, 2)
        df['강수량%'] = round(df['강수량count'] / row_sum['총 예보건수'] * 100, 2)
        df['WW%'] = round(df['WW'] / row_sum['총 예보건수'] * 100, 2)
        df['TY%'] = round(df['TY'] / row_sum['총 예보건수'] * 100, 2)
        df['SS%'] = round(df['SS'] / row_sum['총 예보건수'] * 100, 2)
        df['SR%'] = round(df['SR'] / row_sum['총 예보건수'] * 100, 2)
        df['횟수%'] = round(df['횟수'] / row_sum['총 예보건수'] * 100, 2)
        df['태풍&강수%'] = round(df['태풍&강수count'] / row_sum['총 예보건수'] * 100, 2)
        df['폭풍해일&강수%'] = round(df['폭풍해일&강수count'] / row_sum['총 예보건수'] * 100, 2)
        df['폭우&강수%'] = round(df['폭우&강수count'] / row_sum['총 예보건수'] * 100, 2)
        return df
    
    def calculate_percentages2(df):
        df['기온%'] = df['기온%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['풍속%'] = df['풍속%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['날씨%'] = df['날씨%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['강수량%'] = df['강수량%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['WW%'] = df['WW%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['TY%'] = df['TY%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['SS%'] = df['SS%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['SR%'] = df['SR%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['횟수%'] = df['횟수%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['태풍&강수%'] = df['태풍&강수%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['폭풍해일&강수%'] = df['폭풍해일&강수%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['폭우&강수%'] = df['폭우&강수%'].apply(lambda x: "{:.1f}".format(float(x)))
        return df 
    
    count2_sd3 = pd.merge(SD_loc_row, count2_sd3, on=['권역','지역'], how= 'inner')
    
    count2_sd1 = calculate_percentages(count2_sd1, sd_row_sum)
    count2_sd2 = calculate_percentages(count2_sd2, sd_row_sum)
    count2_sd3 = calculate_percentages1(count2_sd3, count2_sd3)
    count2_sd1 = calculate_percentages2(count2_sd1)
    count2_sd2 = calculate_percentages2(count2_sd2)
    count2_sd3 = calculate_percentages2(count2_sd3)
    
    count2_sd3.replace('A', np.nan, inplace=True)
    
    
    SD_new_order = ['권역', '횟수','횟수%', 'TY','TY%', 'SS','SS%', 'SR','SR%', '강수량count','강수량%', '태풍&강수count','태풍&강수%', '폭풍해일&강수count','폭풍해일&강수%', '폭우&강수count','폭우&강수%']
    count2_sd1 = count2_sd1.reindex(columns=SD_new_order)
    SD_new_order2 = ['권역', '지역','횟수','횟수%', 'TY','TY%', 'SS','SS%', 'SR','SR%', '강수량count','강수량%','태풍&강수count','태풍&강수%', '폭풍해일&강수count','폭풍해일&강수%', '폭우&강수count','폭우&강수%']
    count2_sd2 = count2_sd2.reindex(columns=SD_new_order2)
    SD_new_order5 = ['권역', '지역', '총 예보건수','횟수','횟수%', 'TY','TY%', 'SS','SS%', 'SR','SR%', '강수량count','강수량%','태풍&강수count','태풍&강수%', '폭풍해일&강수count','폭풍해일&강수%', '폭우&강수count','폭우&강수%']
    count2_sd3 = count2_sd3.reindex(columns=SD_new_order5)
    
    
    # 구분열 안의 요소들을 서해, 남해, 동해 순으로 배열
    SD_new_order3 = ['황해중부', '황해남부', '제주도','남해서부','남해동부','동해남부','동해중부']
    count2_sd1['권역'] = pd.Categorical(count2_sd1['권역'], categories=SD_new_order3, ordered=True)
    count2_sd1 = count2_sd1.sort_values('권역').reset_index(drop=True)
    count2_sd2['권역'] = pd.Categorical(count2_sd2['권역'], categories=SD_new_order3, ordered=True)
    count2_sd2 = count2_sd2.sort_values(['권역','지역']).reset_index(drop=True)
    count2_sd3['권역'] = pd.Categorical(count2_sd3['권역'], categories=SD_new_order3, ordered=True)
    count2_sd3 = count2_sd3.sort_values(['권역','지역']).reset_index(drop=True)
    
    count2_sd3.to_excel('갈라짐_지역_사유.xlsx', encoding='euc-kr', float_format='%.1f', index=False)



##################################################################
##################################################################
##################################################################
##################################################################


print()
print()

mod_file = 'tlmod.xlsx'
org_file = 'tlorg.xlsx'

if not os.path.exists(mod_file) or not os.path.exists(org_file):
    print('TL자료가 없습니다')
else:
    tlm = pd.read_excel('tlmod.xlsx')
    tlo = pd.read_excel('tlorg.xlsx')
    
    TL_row = tlm.shape[0]
    
    # 같은 요소의 개수와 같은 권역의 개수를 세는 작업
    grouped = tlm.groupby(['권역', '지역']).size().reset_index(name='총 예보건수')
    
    # 권역 요소별 총합 계산
    grouped_sum = grouped.groupby('권역')['총 예보건수'].sum().reset_index(name='총 예보건수')
    
    
    # 권역 요소 아래에 총합 행 추가
    result = pd.concat([grouped, grouped_sum])
    
    TL_new_order3 = ['황해중부', '황해남부','남해서부','남해동부']
    result['권역'] = pd.Categorical(result['권역'], categories=TL_new_order3, ordered=True)
    result = result.sort_values(['권역','지역']).reset_index(drop=True)
    
    # 권역 열의 맨 아래에 총합 위치
    result.loc[result['지역'] == '총합', '권역'] = np.nan
    result = result.fillna('A')
    TL_loc_row = result
    
    
    tlo['해상특보']=''
    tlo['육상특보']=''
    tlo['특보점수']=''
    
    tlm1 = tlm[["생산일","권역","지역","기온점수","풍속점수","날씨점수","해상특보","육상특보","특보점수","예보지수"]]
    tlo1 = tlo[["생산일","권역","지역","기온점수","풍속점수","날씨점수","해상특보","육상특보","특보점수","예보지수"]]
    
    compare = tlm1['예보지수'] == tlo1['예보지수']
    ctlm = tlm1[~compare]
    ctlo = tlo1[~compare]
    
    ctlm_c = ctlm.copy()
    
    ctlm_c['강수량']=tlm["강수량"]
    ctlm_c['강수점수']=tlm["강수점수"]
    
    ctlm_c = ctlm_c.sort_values(by=['권역','지역'], ascending=[True, True])
    ctlo = ctlo.sort_values(by=['권역','지역'], ascending=[True, True])
    
    ctlm_c.rename(columns={'기온점수':'기온점수m'},inplace=True)
    ctlo.rename(columns={'기온점수':'기온점수o'},inplace=True)
    ctlm_c.rename(columns={'풍속점수':'풍속점수m'},inplace=True)
    ctlo.rename(columns={'풍속점수':'풍속점수o'},inplace=True)
    ctlm_c.rename(columns={'날씨점수':'날씨점수m'},inplace=True)
    ctlo.rename(columns={'날씨점수':'날씨점수o'},inplace=True)
    ctlm_c.rename(columns={'예보지수':'예보지수m'},inplace=True)
    ctlo.rename(columns={'예보지수':'예보지수o'},inplace=True)
    
    tl_result = pd.concat([ctlm_c,ctlo],axis=1)
    
    # 중복된 열을 제거하여 유일한 값을 가지도록 만듦
    tl_result = tl_result.loc[:, ~tl_result.columns.duplicated(keep='first')]
    
    # 컬럼 순서 변경
    tl_result = tl_result[['생산일', '권역', '지역', '기온점수m','기온점수o','풍속점수m','풍속점수o','날씨점수m','날씨점수o','강수량','강수점수','해상특보','육상특보','특보점수','예보지수m','예보지수o']]
    tl_result = tl_result.reset_index(drop=True)
    tl_result.index = tl_result.index + 1
    
    # 셀 색칠 함수
    def highlight_diff(x, color):
        style = 'background-color: {}'.format(color)
        if x[0] != x[1]:
            return [style, style]
        else:
            return ['', '']
    
    def highlight_special_R(row):
        if row.name == '강수량':
            return ['background-color: orange' if x != '-' else '' for x in row]
        else:
            return [''] * len(row)
    
    def highlight_special_sea(row):
        if row.name == '해상특보':
            return ['background-color: green' if x != '-' else '' for x in row]
        else:
            return [''] * len(row)
    def highlight_special_land(row):
        if row.name == '육상특보':
            return ['background-color: cyan' if x != '-' else '' for x in row]
        else:
            return [''] * len(row) 
    
    # 열 비교하여 값이 다른 경우 해당 셀 색칠
    tl_html = tl_result.style.apply(highlight_diff, color='yellow', axis=1, subset=['기온점수m', '기온점수o']) \
                  .apply(highlight_diff, color='blue', axis=1, subset=['풍속점수m', '풍속점수o']) \
                  .apply(highlight_diff, color='red', axis=1, subset=['날씨점수m', '날씨점수o']) \
                  .apply(lambda x: highlight_special_R(x), axis=0) \
                  .apply(lambda x: highlight_special_sea(x), axis=0) \
                  .apply(lambda x: highlight_special_land(x), axis=0) \
                  .set_properties(**{'border': '1px solid black'})
    
    # 스타일이 적용된 데이터프레임을 HTML 파일로 저장
    with open('갯벌.html', 'w') as f:
        f.write(tl_html.to_html())
        
    # 스타일이 적용된 데이터프레임을 xlsx 파일로 저장
    tl_html.to_excel('갯벌.xlsx', index=True)
    
    #각 권역의 갯수, 각 지역의 갯수, 각 변경요인 갯수
    tl_loc = tl_result['권역'].value_counts().sort_index().to_frame(name='횟수').reset_index().rename(columns={'index': '권역'})
    tl_locp = tl_result.groupby(['권역', '지역'])['지역'].count().reset_index(name='횟수')
    
    #각 권역의 각각의 변경요인 갯수
    #각 지역의 각각의 변경요인 갯수
    def count_changes_TL1(df, groupby_col, sea_warn_col='해상특보', land_warn_col='육상특보', rain_col='강수량'):
        count = df.groupby(groupby_col).apply(lambda x: pd.Series({'기온점수count': (x['기온점수m'] != x['기온점수o']).sum(),
                                                                      '풍속점수count': (x['풍속점수m'] != x['풍속점수o']).sum(),
                                                                      '날씨점수count': (x['날씨점수m'] != x['날씨점수o']).sum(),
                                                                      '태풍&강수count': ((x[sea_warn_col].isin(['TY2', 'TY3', 'TY1'])) & (x[rain_col] != '-')).sum(),
                                                                      '폭우&강수count': ((x[land_warn_col].isin(['SR2', 'SR3', 'SR1'])) & (x[rain_col] != '-')).sum(),
                                                                      '폭풍해일&강수count': ((x[land_warn_col].isin(['SS2', 'SS3', 'SS1'])) & (x[rain_col] != '-')).sum(),})).reset_index()
        # 해상 특보와 육상 특보에 대한 필터링 및 경고 횟수 계산
        sea_warn = df[df[sea_warn_col] != '-'].groupby(groupby_col + [sea_warn_col]).size().reset_index(name=sea_warn_col+'count')
        land_warn = df[df[land_warn_col].isin(['SR2', 'SR3','SS2', 'SS3'])].groupby(groupby_col + [land_warn_col]).size().reset_index(name=land_warn_col+'count')
        # 피벗 테이블 생성
        sea_pivot = sea_warn.pivot_table(index=groupby_col, columns=sea_warn_col, values=sea_warn_col+'count', fill_value=0).reset_index()
        land_pivot = land_warn.pivot_table(index=groupby_col, columns=land_warn_col, values=land_warn_col+'count', fill_value=0).reset_index()
        # 경고 횟수 데이터를 count DataFrame에 추가
        count = count.merge(sea_pivot, on=groupby_col, how='left').fillna(0)
        count = count.merge(land_pivot, on=groupby_col, how='left').fillna(0)
        
        rain = df[df[rain_col].astype(int) > 0].groupby(groupby_col + [rain_col]).size().reset_index(name=rain_col+'count')
        rain_pivot = rain.pivot_table(index=groupby_col, columns=rain_col, values=rain_col+'count', fill_value=0).reset_index()
        rain_pivot[rain_col+'count'] = rain_pivot[rain_pivot.columns[1:]].sum(axis=1)
        rain_pivot = rain_pivot.drop(columns=rain_pivot.columns[1:-1])
        
        count = count.merge(rain_pivot, on=groupby_col, how='left').fillna(0)
        
        return count
    
    def count_changes_TL2(df, groupby_col, sea_warn_col='해상특보', land_warn_col='육상특보', rain_col='강수량'):
        count = df.groupby(groupby_col).apply(lambda x: pd.Series({'기온점수count': (x['기온점수m'] != x['기온점수o']).sum(),
                                                                      '풍속점수count': (x['풍속점수m'] != x['풍속점수o']).sum(),
                                                                      '날씨점수count': (x['날씨점수m'] != x['날씨점수o']).sum(),
                                                                      '태풍&강수count': ((x[sea_warn_col].isin(['TY2', 'TY3', 'TY1'])) & (x[rain_col] != '-')).sum(),
                                                                      '폭우&강수count': ((x[land_warn_col].isin(['SR2', 'SR3', 'SR1'])) & (x[rain_col] != '-')).sum(),
                                                                      '폭풍해일&강수count': ((x[land_warn_col].isin(['SS2', 'SS3', 'SS1'])) & (x[rain_col] != '-')).sum(),})).reset_index()
        # 해상 특보와 육상 특보에 대한 필터링 및 경고 횟수 계산
        sea_warn = df[df[sea_warn_col] != '-'].groupby(groupby_col + [sea_warn_col]).size().reset_index(name=sea_warn_col+'count')
        land_warn = df[df[land_warn_col].isin(['SR2', 'SR3','SS2', 'SS3'])].groupby(groupby_col + [land_warn_col]).size().reset_index(name=land_warn_col+'count')
        # 피벗 테이블 생성
        sea_pivot = sea_warn.pivot_table(index=groupby_col, columns=sea_warn_col, values=sea_warn_col+'count', fill_value=0).reset_index()
        land_pivot = land_warn.pivot_table(index=groupby_col, columns=land_warn_col, values=land_warn_col+'count', fill_value=0).reset_index()
        # 경고 횟수 데이터를 count DataFrame에 추가
        count = count.merge(sea_pivot, on=groupby_col, how='left').fillna(0)
        count = count.merge(land_pivot, on=groupby_col, how='left').fillna(0)
        
        rain = df[df[rain_col].astype(int) > 0].groupby(groupby_col + [rain_col]).size().reset_index(name=rain_col+'count')
        rain_pivot = rain.pivot_table(index=groupby_col, columns=rain_col, values=rain_col+'count', fill_value=0).reset_index()
        rain_pivot[rain_col+'count'] = rain_pivot[rain_pivot.columns[1:]].sum(axis=1)
        rain_pivot = rain_pivot.drop(columns=rain_pivot.columns[2:-1])
        
        count = count.merge(rain_pivot, on=groupby_col, how='left').fillna(0)
        
        return count
    
    
    count2_tl1 = count_changes_TL1(tl_result, ['권역'])
    count2_tl1 = count2_tl1.groupby('권역').agg('sum').reset_index()
    count2_tl2 = count_changes_TL2(tl_result, ['권역', '지역'])
    
    # WW2와 WW3열이 모두 존재하는 경우에만 WW2와 WW3열을 합쳐서 WW열로 만듦
    # TY2와 TY3열이 모두 존재하는 경우에만 TY2와 TY3열을 합쳐서 TY열로 만듦
    def combine_columns(df, col1, col2, new_col):
        if col1 in df.columns and col2 in df.columns:
            df[new_col] = df[col1] + df[col2]
            df.drop([col1, col2], axis=1, inplace=True)
        elif col1 in df.columns:
            df[new_col] = df[col1]
            df.drop([col1], axis=1, inplace=True)
        elif col2 in df.columns:
            df[new_col] = df[col2]
            df.drop([col2], axis=1, inplace=True)
        else:
            df[new_col] = 0
        return df
    
    count2_tl1 = combine_columns(count2_tl1, 'WW2', 'WW3', 'WW_1')
    count2_tl2 = combine_columns(count2_tl2, 'WW2', 'WW3', 'WW_1')
    count2_tl1 = combine_columns(count2_tl1, 'TY2', 'TY3', 'TY_1')
    count2_tl2 = combine_columns(count2_tl2, 'TY2', 'TY3', 'TY_1')
    count2_tl1 = combine_columns(count2_tl1, 'SS2', 'SS3', 'SS_1')
    count2_tl2 = combine_columns(count2_tl2, 'SS2', 'SS3', 'SS_1')
    count2_tl1 = combine_columns(count2_tl1, 'SR2', 'SR3', 'SR_1')
    count2_tl2 = combine_columns(count2_tl2, 'SR2', 'SR3', 'SR_1')



    count2_tl1 = combine_columns(count2_tl1, 'WW_1', 'WW1', 'WW')
    count2_tl2 = combine_columns(count2_tl2, 'WW_1', 'WW1', 'WW')
    count2_tl1 = combine_columns(count2_tl1, 'TY_1', 'TY1', 'TY')
    count2_tl2 = combine_columns(count2_tl2, 'TY_1', 'TY1', 'TY')
    count2_tl1 = combine_columns(count2_tl1, 'SS_1', 'SS1', 'SS')
    count2_tl2 = combine_columns(count2_tl2, 'SS_1', 'SS1', 'SS')
    count2_tl1 = combine_columns(count2_tl1, 'SR_1', 'SR1', 'SR')
    count2_tl2 = combine_columns(count2_tl2, 'SR_1', 'SR1', 'SR')



    
    count2_tl2 = count2_tl2.groupby(['권역', '지역']).sum().reset_index()
    
    
    count2_tl1 = pd.merge(count2_tl1, tl_loc, on='권역')
    count2_tl2 = pd.merge(count2_tl2, tl_locp, on='지역')
    
    count2_tl1['지역'] = np.nan
    
    
    
    count2_tl2 = count2_tl2.drop('권역_y', axis=1)
    count2_tl2 = count2_tl2.rename(columns={'권역_x':'권역'})
    TL_new_order1 = ['권역', '지역','기온점수count','풍속점수count','날씨점수count', '태풍&강수count','강수량','강수량count','폭풍해일&강수count','폭우&강수count','WW','TY','SR','SS','횟수']
    count2_tl1 = count2_tl1.reindex(columns=TL_new_order1)
    count2_tl3 = pd.concat([count2_tl1, count2_tl2]).reset_index(drop=True)
    count2_tl3.sort_values(by=['권역','지역'], inplace=True)
    count2_tl3 = count2_tl3.reindex(columns=TL_new_order1)
    
    
    
    count2_tl3['권역'] = pd.Categorical(count2_tl3['권역'], categories=TL_new_order3, ordered=True)
    count2_tl3 = count2_tl3.sort_values(['권역','지역']).reset_index(drop=True)
    
    
    
    count2_tl3 = count2_tl3.fillna('A')
    
    tl_row_sum = count2_tl2["횟수"].sum()
    print()
    print('TL 총통계')
    tl_sum_all = count2_tl1.sum()
    tl_sum_all = pd.DataFrame(tl_sum_all, columns=['변경'])
    tl_sum_all = tl_sum_all.drop('권역', axis=0)
    tl_sum_all = tl_sum_all.rename(index={'횟수': '총예보지수변경'})
    print(tl_sum_all)
    tl_sum_all.to_csv('갯벌_요약.csv', encoding='euc-kr', index=True)
    print('갯벌 총예보건수', TL_row)
    
    
    def calculate_percentages(df, row_sum):
        df['기온%'] = round(df['기온점수count'] / row_sum * 100, 2)
        df['풍속%'] = round(df['풍속점수count'] / row_sum * 100, 2)
        df['날씨%'] = round(df['날씨점수count'] / row_sum * 100, 2)
        df['강수량%'] = round(df['강수량count'] / row_sum * 100, 2)
        df['WW%'] = round(df['WW'] / row_sum * 100, 2)
        df['TY%'] = round(df['TY'] / row_sum * 100, 2)
        df['SS%'] = round(df['SS'] / row_sum * 100, 2)
        df['SR%'] = round(df['SR'] / row_sum * 100, 2)
        df['횟수%'] = round(df['횟수'] / row_sum * 100, 2)
        df['태풍&강수%'] = round(df['태풍&강수count'] / row_sum * 100, 2)
        df['폭풍해일&강수%'] = round(df['폭풍해일&강수count'] / row_sum * 100, 2)
        df['폭우&강수%'] = round(df['폭우&강수count'] / row_sum * 100, 2)
        return df
    
    def calculate_percentages1(df, row_sum):
        df['기온%'] = round(df['기온점수count'] / row_sum['총 예보건수'] * 100, 2)
        df['풍속%'] = round(df['풍속점수count'] / row_sum['총 예보건수'] * 100, 2)
        df['날씨%'] = round(df['날씨점수count'] / row_sum['총 예보건수'] * 100, 2)
        df['강수량%'] = round(df['강수량count'] / row_sum['총 예보건수'] * 100, 2)
        df['WW%'] = round(df['WW'] / row_sum['총 예보건수'] * 100, 2)
        df['TY%'] = round(df['TY'] / row_sum['총 예보건수'] * 100, 2)
        df['SS%'] = round(df['SS'] / row_sum['총 예보건수'] * 100, 2)
        df['SR%'] = round(df['SR'] / row_sum['총 예보건수'] * 100, 2)
        df['횟수%'] = round(df['횟수'] / row_sum['총 예보건수'] * 100, 2)
        df['태풍&강수%'] = round(df['태풍&강수count'] / row_sum['총 예보건수'] * 100, 2)
        df['폭풍해일&강수%'] = round(df['폭풍해일&강수count'] / row_sum['총 예보건수'] * 100, 2)
        df['폭우&강수%'] = round(df['폭우&강수count'] / row_sum['총 예보건수'] * 100, 2)
        return df
    
    def calculate_percentages2(df):
        df['기온%'] = df['기온%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['풍속%'] = df['풍속%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['날씨%'] = df['날씨%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['강수량%'] = df['강수량%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['WW%'] = df['WW%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['TY%'] = df['TY%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['SS%'] = df['SS%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['SR%'] = df['SR%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['횟수%'] = df['횟수%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['태풍&강수%'] = df['태풍&강수%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['폭풍해일&강수%'] = df['폭풍해일&강수%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['폭우&강수%'] = df['폭우&강수%'].apply(lambda x: "{:.1f}".format(float(x)))
        return df 
    
    count2_tl3 = pd.merge(TL_loc_row, count2_tl3, on=['권역','지역'], how= 'inner')
    
    count2_tl1 = calculate_percentages(count2_tl1, tl_row_sum)
    count2_tl2 = calculate_percentages(count2_tl2, tl_row_sum)
    count2_tl3 = calculate_percentages1(count2_tl3, count2_tl3)
    count2_tl1 = calculate_percentages2(count2_tl1)
    count2_tl2 = calculate_percentages2(count2_tl2)
    count2_tl3 = calculate_percentages2(count2_tl3)
    
    count2_tl3.replace('A', np.nan, inplace=True)
    
    
    TL_new_order = ['권역', '횟수','횟수%', 'TY','TY%', 'SS','SS%', 'SR','SR%', '강수량count','강수량%', '태풍&강수count','태풍&강수%', '폭풍해일&강수count','폭풍해일&강수%', '폭우&강수count','폭우&강수%']
    count2_tl1 = count2_tl1.reindex(columns=TL_new_order)
    TL_new_order2 = ['권역', '지역','횟수','횟수%', 'TY','TY%', 'SS','SS%', 'SR','SR%', '강수량count','강수량%','태풍&강수count','태풍&강수%', '폭풍해일&강수count','폭풍해일&강수%', '폭우&강수count','폭우&강수%']
    count2_tl2 = count2_tl2.reindex(columns=TL_new_order2)
    TL_new_order5 = ['권역', '지역', '총 예보건수','횟수','횟수%', 'TY','TY%', 'SS','SS%', 'SR','SR%', '강수량count','강수량%','태풍&강수count','태풍&강수%', '폭풍해일&강수count','폭풍해일&강수%', '폭우&강수count','폭우&강수%']
    count2_tl3 = count2_tl3.reindex(columns=TL_new_order5)
    
    
    # 구분열 안의 요소들을 서해, 남해, 동해 순으로 배열
    TL_new_order3 = ['황해중부', '황해남부', '남해서부','남해동부']
    count2_tl1['권역'] = pd.Categorical(count2_tl1['권역'], categories=TL_new_order3, ordered=True)
    count2_tl1 = count2_tl1.sort_values('권역').reset_index(drop=True)
    count2_tl2['권역'] = pd.Categorical(count2_tl2['권역'], categories=TL_new_order3, ordered=True)
    count2_tl2 = count2_tl2.sort_values(['권역','지역']).reset_index(drop=True)
    count2_tl3['권역'] = pd.Categorical(count2_tl3['권역'], categories=TL_new_order3, ordered=True)
    count2_tl3 = count2_tl3.sort_values(['권역','지역']).reset_index(drop=True)
    
    count2_tl3.to_excel('갯벌_지역_사유.xlsx', encoding='euc-kr', float_format='%.1f', index=False)



##################################################################
##################################################################
##################################################################
##################################################################

print()
print()

mod_file = 'sfmod.xlsx'
org_file = 'sforg.xlsx'

if not os.path.exists(mod_file) or not os.path.exists(org_file):
    print('SF자료가 없습니다')
else:
    sfm = pd.read_excel('sfmod.xlsx')
    sfo = pd.read_excel('sforg.xlsx')

    
    # 행의 갯수
    SF_row = sfm.shape[0]
    
    sfo['해상특보']=''
    sfo['육상특보']=''
    sfo['특보점수']=''
    
    sfm1 = sfm[["생산일","권역","지역","예보지수"]]
    sfo1 = sfo[["생산일","권역","지역","예보지수"]]
    
    compare = sfm1['예보지수'] == sfo1['예보지수']
    csfm = sfm1[~compare]
    csfo = sfo1[~compare]
    
    csfm_c = csfm.copy()
    
    csfm_c = csfm_c.sort_values(by=['권역','지역'], ascending=[True, True])
    csfo = csfo.sort_values(by=['권역','지역'], ascending=[True, True])
    
    csfm_c.rename(columns={'예보지수':'예보지수m'},inplace=True)
    csfo.rename(columns={'예보지수':'예보지수o'},inplace=True)
    
    sf_result = pd.concat([csfm_c,csfo],axis=1)
    
    sf_re_row = sf_result.shape[0]
    
    
    print()
    print('SF 총통계')
    print('총예보지수변경', sf_re_row)
    print('바다낚시 총예보건수', SF_row)
    print()
    
    
    
    
##################################################################
##################################################################
##################################################################
##################################################################
    
print()
print()

mod_file = 'skmod.xlsx'
org_file = 'skorg.xlsx'

if not os.path.exists(mod_file) or not os.path.exists(org_file):
    print('SK자료가 없습니다')
else:
    skm = pd.read_excel('skmod.xlsx')
    sko = pd.read_excel('skorg.xlsx')
    
    # 행의 갯수
    SK_row = skm.shape[0]
    
    sko['특보']=''
    sko['특보점수']=''
    
    skm1 = skm[["생산일","항로명","선박명","예보지수"]]
    sko1 = sko[["생산일","항로명","선박명","예보지수"]]
    
    compare = skm1['예보지수'] == sko1['예보지수']
    cskm = skm1[~compare]
    csko = sko1[~compare]
    
    cskm_c = cskm.copy()
    
    cskm_c = cskm_c.sort_values(by=['항로명','선박명'], ascending=[True, True])
    csko = csko.sort_values(by=['항로명','선박명'], ascending=[True, True])
    
    cskm_c.rename(columns={'예보지수':'예보지수m'},inplace=True)
    csko.rename(columns={'예보지수':'예보지수o'},inplace=True)
    
    sk_result = pd.concat([cskm_c,csko],axis=1)
    
    sk_re_row = sk_result.shape[0]
    
    
    print()
    print('SK 총통계')
    print('총예보지수변경', sk_re_row)
    print('뱃멀미 총예보건수', SK_row)
    print()
    
    
    
    
##################################################################
##################################################################
##################################################################
##################################################################
    
    
print()
print()
    
mod_file = 'srmod.xlsx'
org_file = 'srorg.xlsx'

if not os.path.exists(mod_file) or not os.path.exists(org_file):
    print('SR자료가 없습니다')
else:
    srm = pd.read_excel('srmod.xlsx')
    sro = pd.read_excel('srorg.xlsx')
    
    # 행의 갯수
    SR_row = srm.shape[0]
    
    sro['해상특보']=''
    sro['육상특보']=''
    sro['특보점수']=''
    
    srm1 = srm[["생산일","구분","지역","예보지수"]]
    sro1 = sro[["생산일","구분","지역","예보지수"]]
    
    compare = srm1['예보지수'] == sro1['예보지수']
    csrm = srm1[~compare]
    csro = sro1[~compare]
    
    csrm_c = csrm.copy()
    
    csrm_c = csrm_c.sort_values(by=['구분','지역'], ascending=[True, True])
    csro = csro.sort_values(by=['구분','지역'], ascending=[True, True])
    
    csrm_c.rename(columns={'예보지수':'예보지수m'},inplace=True)
    csro.rename(columns={'예보지수':'예보지수o'},inplace=True)
    
    sr_result = pd.concat([csrm_c,csro],axis=1)
    
    sr_re_row = sr_result.shape[0]
    
    
    print()
    print('SR 총통계')
    print('총예보지수변경', sr_re_row)
    print('서핑 총예보건수', SR_row)
    print()
    
    
##################################################################
##################################################################
##################################################################
##################################################################
    
   
print()
print()
    
mod_file = 'spmod.xlsx'
org_file = 'sporg.xlsx'

if not os.path.exists(mod_file) or not os.path.exists(org_file):
    print('SP자료가 없습니다')
else:
    spm = pd.read_excel('spmod.xlsx')
    spo = pd.read_excel('sporg.xlsx')
    
    # 행의 갯수
    SP_row = spm.shape[0]
    
    spo['해상특보']=''
    spo['육상특보']=''
    spo['특보점수']=''
    
    spm1 = spm[["생산일","권역","해수욕장","예보지수"]]
    spo1 = spo[["생산일","권역","해수욕장","예보지수"]]
    
    compare = spm1['예보지수'] == spo1['예보지수']
    cspm = spm1[~compare]
    cspo = spo1[~compare]
    
    different_rows = (spm1['예보지수'] != spo1['예보지수']).sum()
    
    
    print()
    print('SP 총통계')
    print('총예보지수변경', different_rows)
    print('해수욕 총예보건수', SP_row)
    print()
    
    
##################################################################
##################################################################
##################################################################
##################################################################
    
    
print()
print()
    
mod_file = 'ssmod.xlsx'
org_file = 'ssorg.xlsx'

if not os.path.exists(mod_file) or not os.path.exists(org_file):
    print('SS자료가 없습니다')
else:
    ssm = pd.read_excel('ssmod.xlsx')
    sso = pd.read_excel('ssorg.xlsx')
    
    # 행의 갯수
    SS_row = ssm.shape[0]
    
    sso['해상특보']=''
    sso['육상특보']=''
    sso['특보점수']=''
    
    ssm1 = ssm[["생산일","권역","지역","예보지수"]]
    sso1 = sso[["생산일","권역","지역","예보지수"]]
    
    compare = ssm1['예보지수'] == sso1['예보지수']
    cssm = ssm1[~compare]
    csso = sso1[~compare]
    
    cssm_c = cssm.copy()
    
    cssm_c = cssm_c.sort_values(by=['권역','지역'], ascending=[True, True])
    csso = csso.sort_values(by=['권역','지역'], ascending=[True, True])
    
    cssm_c.rename(columns={'예보지수':'예보지수m'},inplace=True)
    csso.rename(columns={'예보지수':'예보지수o'},inplace=True)
    
    ss_result = pd.concat([cssm_c,csso],axis=1)
    
    ss_re_row = ss_result.shape[0]
    
    
    print()
    print('SS 총통계')
    print('총예보지수변경', ss_re_row)
    print('스킨스쿠버 총예보건수', SS_row)
    print()