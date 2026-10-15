# -*- coding: utf-8 -*-
"""
Created on Mon Auh 26 14:33:03 2024

@author: sang
"""


'''
mod=서비스
org=예측
'''
import pandas as pd
import numpy as np
import os
import warnings
# 경고창 숨기기
warnings.filterwarnings('ignore') 
# 경고창 다시 나타내기
#warnings.filterwarnings('default')

# 바다낚시
# 파일 경로
mod_file = 'sfmod.xlsx'
org_file = 'sforg.xlsx'
print()
print()
# 파일 존재 여부 확인
if not os.path.exists(mod_file) or not os.path.exists(org_file):
    print('SF자료가 없습니다')
else:
    sfm = pd.read_excel('sfmod.xlsx')
    sfo = pd.read_excel('sforg.xlsx')
    
    # 행의 갯수
    SF_row = sfm.shape[0]
    
    
    # 같은 요소의 개수와 같은 권역의 개수를 세는 작업
    grouped = sfm.groupby(['권역', '지역']).size().reset_index(name='총 예보건수')
    
    # 권역 요소별 총합 계산
    grouped_sum = grouped.groupby('권역')['총 예보건수'].sum().reset_index(name='총 예보건수')
    
    
    # 권역 요소 아래에 총합 행 추가
    result = pd.concat([grouped, grouped_sum])
    
    SF_new_order3 = ['황해중부', '황해남부', '제주도','남해서부','남해동부','동해남부','동해중부']
    result['권역'] = pd.Categorical(result['권역'], categories=SF_new_order3, ordered=True)
    result = result.sort_values(['권역','지역']).reset_index(drop=True)
    
    # 권역 열의 맨 아래에 총합 위치
    result.loc[result['지역'] == '총합', '권역'] = np.nan
    result = result.fillna('A')
    SF_loc_row = result
    
    
    sfo['해상특보']=''
    sfo['육상특보']=''
    sfo['특보점수']=''
    
    sfm1 = sfm[["생산일","권역","지역","해상특보","육상특보","특보점수","예보지수"]]
    
    sfo1 = sfo[["생산일","권역","지역","해상특보","육상특보","특보점수","예보지수"]]
    
    sfo1['특보점수'] = 100
    
    
    compare = sfm1['특보점수'] == sfo1['특보점수']
    csfm1 = sfm1[~compare]
    csfo1 = sfo1[~compare]
    
    compare = csfm1['예보지수'] == csfo1['예보지수']
    csfm = csfm1[~compare]
    csfo = csfo1[~compare]
    
    
    csfm_c = csfm.copy()
    
    csfm_c = csfm_c.sort_values(by=['권역','지역'], ascending=[True, True])
    csfo = csfo.sort_values(by=['권역','지역'], ascending=[True, True])
    
    csfm_c.rename(columns={'예보지수':'예보지수m'},inplace=True)
    csfo.rename(columns={'예보지수':'예보지수o'},inplace=True)
    
    sf_result = pd.concat([csfm_c,csfo],axis=1)
    
    # 중복된 열을 제거하여 유일한 값을 가지도록 만듦
    sf_result = sf_result.loc[:, ~sf_result.columns.duplicated(keep='first')]
    
    # 컬럼 순서 변경
    sf_result = sf_result[['생산일', '권역', '지역','해상특보','육상특보','특보점수','예보지수m','예보지수o']]
    sf_result = sf_result.reset_index(drop=True)
    sf_result.index = sf_result.index + 1
    
    # 셀 색칠 함수
    def highlight_diff(x, color):
        style = 'background-color: {}'.format(color)
        if x[0] != x[1]:
            return [style, style]
        else:
            return ['', '']
    
    def highlight_special_sea(row):
        if row.name == '해상특보':
            return ['background-color: orange' if x != '-' else '' for x in row]
        else:
            return [''] * len(row)
    def highlight_special_land(row):
        if row.name == '육상특보':
            return ['background-color: cyan' if x != '-' else '' for x in row]
        else:
            return [''] * len(row)   
    
    # 열 비교하여 값이 다른 경우 해당 셀 색칠
    sf_html = sf_result.style.apply(lambda x: highlight_special_sea(x), axis=0) \
                  .apply(lambda x: highlight_special_land(x), axis=0) \
                  .set_properties(**{'border': '1px solid black'})
    
    
    # 스타일이 적용된 데이터프레임을 HTML 파일로 저장
    with open('바다낚시1_특보.html', 'w') as f:
        f.write(sf_html.to_html())
    
    # 스타일이 적용된 데이터프레임을 xlsx 파일로 저장
    sf_html.to_excel('바다낚시1_특보.xlsx', index=True)
    
    #각 권역의 갯수, 각 지역의 갯수, 각 변경요인 갯수
    sf_loc = sf_result['권역'].value_counts().sort_index().to_frame(name='횟수').reset_index().rename(columns={'index': '권역'})
    sf_locp = sf_result.groupby(['권역', '지역'])['지역'].count().reset_index(name='횟수')
    
    #각 권역의 각각의 변경요인 갯수
    #각 지역의 각각의 변경요인 갯수
    def count_changes_SF(df, groupby_col, sea_warn_col='해상특보', land_warn_col='육상특보'):
        count = df.groupby(groupby_col).apply(lambda x: pd.Series({
            '지수count': (x['예보지수m'] != x['예보지수o']).sum(),
            'WW&SRcount': ((x[sea_warn_col].isin(['WW2', 'WW3' ,'WW1'])) & (x[land_warn_col].isin(['SR2', 'SR3', 'SR1']))).sum(),
            'WW&SScount': ((x[sea_warn_col].isin(['WW2', 'WW3','WW1'])) & (x[land_warn_col].isin(['SS2', 'SS3', 'SS1']))).sum(),
            'TY&SRcount': ((x[sea_warn_col].isin(['TY2', 'TY3', 'TY1'])) & (x[land_warn_col].isin(['SR2', 'SR3', 'SR1']))).sum(),
            'TY&SScount': ((x[sea_warn_col].isin(['TY2', 'TY3', 'TY1'])) & (x[land_warn_col].isin(['SS2', 'SS3', 'SS1']))).sum()
        })).reset_index()
        
        
        
        # 해상 특보와 육상 특보에 대한 필터링 및 경고 횟수 계산
        sea_warn = df[df[sea_warn_col] != '-'].groupby(groupby_col + [sea_warn_col]).size().reset_index(name=sea_warn_col+'count')
        land_warn = df[df[land_warn_col] != '-'].groupby(groupby_col + [land_warn_col]).size().reset_index(name=land_warn_col+'count')
        # 피벗 테이블 생성
        sea_pivot = sea_warn.pivot_table(index=groupby_col, columns=sea_warn_col, values=sea_warn_col+'count', fill_value=0).reset_index()
        land_pivot = land_warn.pivot_table(index=groupby_col, columns=land_warn_col, values=land_warn_col+'count', fill_value=0).reset_index()
        # 경고 횟수 데이터를 count DataFrame에 추가
        count = count.merge(sea_pivot, on=groupby_col, how='left').fillna(0)
        count = count.merge(land_pivot, on=groupby_col, how='left').fillna(0)
        return count
    
    count_sf1 = count_changes_SF(sf_result, ['권역'])
    count_sf2 = count_changes_SF(sf_result, ['권역', '지역'])
    
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
    
    count_sf1 = combine_columns(count_sf1, 'WW2', 'WW3', 'WW_1')
    count_sf2 = combine_columns(count_sf2, 'WW2', 'WW3', 'WW_1')
    count_sf1 = combine_columns(count_sf1, 'WW_1', 'WW1', 'WW')
    count_sf2 = combine_columns(count_sf2, 'WW_1', 'WW1', 'WW')
    
    count_sf1 = combine_columns(count_sf1, 'SR2', 'SR3', 'SR_1')
    count_sf1 = combine_columns(count_sf1, 'SR_1', 'SR1', 'SR')
    count_sf2 = combine_columns(count_sf2, 'SR2', 'SR3', 'SR_1')
    count_sf2 = combine_columns(count_sf2, 'SR_1', 'SR1', 'SR')
    
    count_sf1 = combine_columns(count_sf1, 'SS2', 'SS3', 'SS_1')
    count_sf2 = combine_columns(count_sf2, 'SS2', 'SS3', 'SS_1')
    count_sf1 = combine_columns(count_sf1, 'SS_1', 'SS1', 'SS')
    count_sf2 = combine_columns(count_sf2, 'SS_1', 'SS1', 'SS')
    
    count_sf1 = combine_columns(count_sf1, 'TY1_x', 'TY2_x', 'TY_x')
    count_sf1 = combine_columns(count_sf1, 'TY1_y', 'TY2_y', 'TY_y')
    count_sf1 = combine_columns(count_sf1, 'TY_x', 'TY_y', 'TY_1')
    count_sf1 = combine_columns(count_sf1, 'TY_1', 'TY3', 'TY')
    count_sf2 = combine_columns(count_sf2, 'TY1_x', 'TY2_x', 'TY_x')
    count_sf2 = combine_columns(count_sf2, 'TY1_y', 'TY2_y', 'TY_y')
    count_sf2 = combine_columns(count_sf2, 'TY_x', 'TY_y', 'TY_1')
    count_sf2 = combine_columns(count_sf2, 'TY_1', 'TY3', 'TY')
    
    
    count_sf1 = pd.merge(count_sf1, sf_loc, on='권역')
    count_sf2 = pd.merge(count_sf2, sf_locp, on='지역')
    
    count_sf1['지역'] = np.nan
    count_sf2 = count_sf2.drop('권역_y', axis=1)
    count_sf2 = count_sf2.rename(columns={'권역_x':'권역'})
    SF_new_order1 = ['권역', '지역','지수count','WW','TY','SS','SR','WW&SRcount','WW&SScount','TY&SRcount','TY&SScount','횟수']
    count_sf3 = pd.concat([count_sf1, count_sf2], ignore_index=True)
    count_sf3 = count_sf3.reindex(columns=SF_new_order1)
    
    count_sf3['권역'] = pd.Categorical(count_sf3['권역'], categories=SF_new_order3, ordered=True)
    count_sf3 = count_sf3.sort_values(['권역','지역']).reset_index(drop=True)
    
    # 권역 열의 맨 아래에 총합 위치
    count_sf3.loc[result['지역'] == '총합', '권역'] = np.nan
    count_sf3 = count_sf3.fillna('A')
    
    
    sf_row_sum = count_sf1["횟수"].sum()
    
    print()
    print('SF 총통계')
    sf_sum_all = count_sf1.sum()
    sf_sum_all = pd.DataFrame(sf_sum_all, columns=['변경'])
    sf_sum_all = sf_sum_all.drop('권역', axis=0)
    sf_sum_all = sf_sum_all.rename(index={'횟수': '총예보지수변경'})
    print(sf_sum_all)
    sf_sum_all.to_csv('바다낚시2_요약_특보.csv', encoding='euc-kr', index=True)
    
    def calculate_percentages(df, row_sum):
        df['WW%'] = round(df['WW'] / row_sum * 100, 1)
        df['TY%'] = round(df['TY'] / row_sum * 100, 1)
        df['SS%'] = round(df['SS'] / row_sum * 100, 2)
        df['SR%'] = round(df['SR'] / row_sum * 100, 2)
        df['횟수%'] = round(df['횟수'] / row_sum * 100, 1)
        df['WW&SR%'] = round(df['WW&SRcount'] / row_sum * 100, 1)
        df['WW&SS%'] = round(df['WW&SScount'] / row_sum * 100, 1)
        df['TY&SR%'] = round(df['TY&SRcount'] / row_sum * 100, 1)
        df['TY&SS%'] = round(df['TY&SScount'] / row_sum * 100, 1)
        return df
    
    def calculate_percentages1(df, row_sum):
        df['WW%'] = round(df['WW'] / row_sum['총 예보건수'] * 100, 1)
        df['TY%'] = round(df['TY'] / row_sum['총 예보건수'] * 100, 1)
        df['SS%'] = round(df['SS'] / row_sum['총 예보건수'] * 100, 2)
        df['SR%'] = round(df['SR'] / row_sum['총 예보건수'] * 100, 2)
        df['횟수%'] = round(df['횟수'] / row_sum['총 예보건수'] * 100, 2)
        df['WW&SR%'] = round(df['WW&SRcount'] / row_sum['총 예보건수'] * 100, 2)
        df['WW&SS%'] = round(df['WW&SScount'] / row_sum['총 예보건수'] * 100, 2)
        df['TY&SR%'] = round(df['TY&SRcount'] / row_sum['총 예보건수'] * 100, 2)
        df['TY&SS%'] = round(df['TY&SScount'] / row_sum['총 예보건수'] * 100, 2)
        return df
    
    def calculate_percentages2(df):
        df['WW%'] = df['WW%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['TY%'] = df['TY%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['SS%'] = df['SS%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['SR%'] = df['SR%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['횟수%'] = df['횟수%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['WW&SR%'] = df['WW&SR%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['WW&SS%'] = df['WW&SS%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['TY&SR%'] = df['TY&SR%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['TY&SS%'] = df['TY&SS%'].apply(lambda x: "{:.1f}".format(float(x)))    
        return df 
    
    count_sf3 = pd.merge(SF_loc_row, count_sf3, on=['권역','지역'], how= 'inner')
    
    count_sf1 = calculate_percentages(count_sf1, sf_row_sum)
    count_sf2 = calculate_percentages(count_sf2, sf_row_sum)
    count_sf3 = calculate_percentages1(count_sf3, count_sf3)
    count_sf1 = calculate_percentages2(count_sf1)
    count_sf2 = calculate_percentages2(count_sf2)
    count_sf3 = calculate_percentages2(count_sf3)
    
    count_sf3.replace('A', np.nan, inplace=True)
    

    count_sf2 = count_sf2.rename(columns={'권역_x':'권역'})
    
    SF_new_order = ['권역', '횟수','횟수%','TY','TY%','WW','WW%','SS','SS%','SR','SR%','WW&SRcount','WW&SR%','WW&SScount','WW&SS%','TY&SRcount','TY&SR%','TY&SScount','TY&SS%']
    count_sf1 = count_sf1.reindex(columns=SF_new_order)
    SF_new_order2 = ['권역', '지역','횟수','횟수%','TY','TY%','WW','WW%','SS','SS%','SR','SR%','WW&SRcount','WW&SR%','WW&SScount','WW&SS%','TY&SRcount','TY&SR%','TY&SScount','TY&SS%']
    count_sf2 = count_sf2.reindex(columns=SF_new_order2)
    SF_new_order5 = ['권역', '지역', '총 예보건수', '횟수','횟수%','TY','TY%','WW','WW%','SS','SS%','SR','SR%','WW&SRcount','WW&SR%','WW&SScount','WW&SS%','TY&SRcount','TY&SR%','TY&SScount','TY&SS%']
    count_sf3 = count_sf3.reindex(columns=SF_new_order5)
    
    # 구분열 안의 요소들을 서해, 남해, 동해 순으로 배열
    SF_new_order3 = ['황해중부', '황해남부', '제주도','남해서부','남해동부','동해남부','동해중부']
    count_sf1['권역'] = pd.Categorical(count_sf1['권역'], categories=SF_new_order3, ordered=True)
    count_sf1 = count_sf1.sort_values('권역').reset_index(drop=True)
    count_sf2['권역'] = pd.Categorical(count_sf2['권역'], categories=SF_new_order3, ordered=True)
    count_sf2 = count_sf2.sort_values(['권역','지역']).reset_index(drop=True)
    count_sf3['권역'] = pd.Categorical(count_sf3['권역'], categories=SF_new_order3, ordered=True)
    count_sf3 = count_sf3.sort_values(['권역','지역']).reset_index(drop=True)
    
    
    count_sf3.to_excel('바다낚시3_지역_특보.xlsx', encoding='euc-kr', float_format='%.1f', index=False)
    
    ##################################################################
    ##################################################################
 
# 뱃멀미
# 파일 경로
mod_file = 'skmod.xlsx'
org_file = 'skorg.xlsx'
print()
print()
# 파일 존재 여부 확인
if not os.path.exists(mod_file) or not os.path.exists(org_file):
    print('SK자료가 없습니다')
else:
    skm = pd.read_excel('skmod.xlsx')
    sko = pd.read_excel('skorg.xlsx')
    
    # 행의 갯수
    SK_row = skm.shape[0]
    
    # 같은 요소의 개수와 같은 권역의 개수를 세는 작업
    grouped = skm.groupby(['항로명', '선박명']).size().reset_index(name='총 예보건수')
    
    # 권역 요소별 총합 계산
    grouped_sum = grouped.groupby('항로명')['총 예보건수'].sum().reset_index(name='총 예보건수')
    
    
    # 권역 요소 아래에 총합 행 추가
    result = pd.concat([grouped, grouped_sum])
    
    result['항로명'] = pd.Categorical(result['항로명'], ordered=True)
    result = result.sort_values(['항로명','선박명']).reset_index(drop=True)
    
    # 권역 열의 맨 아래에 총합 위치
    result.loc[result['선박명'] == '총합', '항로명'] = np.nan
    result = result.fillna('A')
    SK_loc_row = result
    
    
    sko['특보']=''
    sko['특보점수']=''
    
    skm1 = skm[["생산일","항로명","선박명","특보","특보점수","예보지수"]]
    sko1 = sko[["생산일","항로명","선박명","특보","특보점수","예보지수"]]
    
    sko1['특보점수'] = 100
    
    compare = skm1['특보점수'] == sko1['특보점수']
    cskm1 = skm1[~compare]
    csko1 = sko1[~compare]
    
    compare = cskm1['예보지수'] == csko1['예보지수']
    cskm = cskm1[~compare]
    csko = csko1[~compare]
    
    cskm_c = cskm.copy()
    
    cskm_c = cskm_c.sort_values(by=['항로명','선박명'], ascending=[True, True])
    csko = csko.sort_values(by=['항로명','선박명'], ascending=[True, True])
    
    
    cskm_c.rename(columns={'예보지수':'예보지수m'},inplace=True)
    csko.rename(columns={'예보지수':'예보지수o'},inplace=True)
    
    sk_result = pd.concat([cskm_c,csko],axis=1)
    
    # 중복된 열을 제거하여 유일한 값을 가지도록 만듦
    sk_result = sk_result.loc[:, ~sk_result.columns.duplicated(keep='first')]
    
    # 컬럼 순서 변경
    sk_result = sk_result[['생산일', '항로명', '선박명','특보','특보점수','예보지수m','예보지수o']]
    sk_result = sk_result.reset_index(drop=True)
    sk_result.index = sk_result.index + 1
    
    # 셀 색칠 함수
    def highlight_diff(x, color):
        style = 'background-color: {}'.format(color)
        if x[0] != x[1]:
            return [style, style]
        else:
            return ['', '']
    
    def highlight_special(row):
        if row.name == '특보':
            return ['background-color: orange' if x != '-' else '' for x in row]
        else:
            return [''] * len(row)
    
    # 열 비교하여 값이 다른 경우 해당 셀 색칠
    sk_html = sk_result.style.apply(lambda x: highlight_special(x), axis=0) \
                  .set_properties(**{'border': '1px solid black'})
    
    # 스타일이 적용된 데이터프레임을 HTML 파일로 저장
    with open('뱃멀미1_특보.html', 'w') as f:
        f.write(sk_html.to_html())
    
    # 스타일이 적용된 데이터프레임을 xlsx 파일로 저장
    sk_html.to_excel('뱃멀미1_특보.xlsx', index=True)
    
    #각 권역의 갯수, 각 지역의 갯수, 각 변경요인 갯수
    sk_loc = sk_result['항로명'].value_counts().sort_index().to_frame(name='횟수').reset_index().rename(columns={'index': '항로명'})
    sk_locp = sk_result.groupby(['항로명', '선박명'])['선박명'].count().reset_index(name='횟수')
    
    #각 권역의 각각의 변경요인 갯수
    #각 지역의 각각의 변경요인 갯수
    def count_changes_SK(df, groupby_col, warn_col='특보'):
        count = df.groupby(groupby_col).apply(lambda x: pd.Series({'지수count': (x['예보지수m'] != x['예보지수o']).sum(),
            'WW&SScount': ((x[warn_col].isin(['WW2', 'WW3', 'WW1'])) & (x[warn_col].isin(['SS2', 'SS3', 'SS1']))).sum(),
            'TY&SScount': ((x[warn_col].isin(['TY2', 'TY3', 'TY1'])) & (x[warn_col].isin(['SS2', 'SS3', 'SS1']))).sum()})).reset_index()
        
        warn = df[df[warn_col] != '-'].groupby(groupby_col + [warn_col]).size().reset_index(name=warn_col+'count')
        pivot = warn.pivot_table(index=groupby_col, columns=warn_col, values=warn_col+'count', fill_value=0).reset_index()
        count = count.merge(pivot, on=groupby_col, how='left').fillna(0)
        return count
    
    count_sk1 = count_changes_SK(sk_result, ['항로명'])
    count_sk2 = count_changes_SK(sk_result, ['항로명', '선박명'])
    
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
    
    count_sk1 = combine_columns(count_sk1, 'WW2', 'WW3', 'WW_1')
    count_sk2 = combine_columns(count_sk2, 'WW2', 'WW3', 'WW_1')
    count_sk1 = combine_columns(count_sk1, 'WW_1', 'WW1', 'WW')
    count_sk2 = combine_columns(count_sk2, 'WW_1', 'WW1', 'WW')
    
    count_sk1 = combine_columns(count_sk1, 'TY1_x', 'TY2_x', 'TY_x')
    count_sk1 = combine_columns(count_sk1, 'TY1_y', 'TY2_y', 'TY_y')
    count_sk1 = combine_columns(count_sk1, 'TY_x', 'TY_y', 'TY_1')
    count_sk1 = combine_columns(count_sk1, 'TY_1', 'TY3', 'TY')
    count_sk2 = combine_columns(count_sk2, 'TY1_x', 'TY2_x', 'TY_x')
    count_sk2 = combine_columns(count_sk2, 'TY1_y', 'TY2_y', 'TY_y')
    count_sk2 = combine_columns(count_sk2, 'TY_x', 'TY_y', 'TY_1')
    count_sk2 = combine_columns(count_sk2, 'TY_1', 'TY3', 'TY')
    
    count_sk1 = combine_columns(count_sk1, 'SS2', 'SS3', 'SS_1')
    count_sk2 = combine_columns(count_sk2, 'SS2', 'SS3', 'SS_1')
    count_sk1 = combine_columns(count_sk1, 'SS_1', 'SS1', 'SS')
    count_sk2 = combine_columns(count_sk2, 'SS_1', 'SS1', 'SS')
    
    
    count_sk1 = pd.merge(count_sk1, sk_loc, on='항로명')
    count_sk2 = pd.merge(count_sk2, sk_locp, on='선박명')
    
    count_sk1['선박명'] = np.nan
    count_sk2 = count_sk2.drop('항로명_y', axis=1)
    count_sk2 = count_sk2.rename(columns={'항로명_x':'항로명'})
    SK_new_order1 = ['항로명', '선박명','지수count', 'WW','TY','SS','WW&SScount','TY&SScount','횟수']
    count_sk3 = pd.concat([count_sk1, count_sk2], ignore_index=True)
    count_sk3 = count_sk3.reindex(columns=SK_new_order1)
    
    count_sk3['항로명'] = pd.Categorical(count_sk3['항로명'], ordered=True)
    count_sk3 = count_sk3.sort_values(['항로명','선박명']).reset_index(drop=True)
    
    # 권역 열의 맨 아래에 총합 위치
    count_sk3.loc[result['선박명'] == '총합', '항로명'] = np.nan
    count_sk3 = count_sk3.fillna('A')
    
    sk_row_sum = count_sk1["횟수"].sum()
    
    print()
    print('SK 총통계')
    sk_sum_all = count_sk1.sum()
    sk_sum_all = pd.DataFrame(sk_sum_all, columns=['변경'])
    sk_sum_all = sk_sum_all.drop('항로명', axis=0)
    sk_sum_all = sk_sum_all.rename(index={'횟수': '총예보지수변경'})
    print(sk_sum_all)
    sk_sum_all.to_csv('뱃멀미2_요약_특보.csv', encoding='euc-kr', index=True)
    
    def calculate_percentages(df, row_sum):
        df['WW%'] = round(df['WW'] / row_sum * 100, 2)
        df['TY%'] = round(df['TY'] / row_sum * 100, 2)
        df['횟수%'] = round(df['횟수'] / row_sum * 100, 2)
        df['WW&SS%'] = round(df['WW&SScount'] / row_sum * 100, 1)
        df['TY&SS%'] = round(df['TY&SScount'] / row_sum * 100, 1)
        return df
    
    def calculate_percentages1(df, row_sum):
        df['WW%'] = round(df['WW'] / row_sum['총 예보건수'] * 100, 2)
        df['TY%'] = round(df['TY'] / row_sum['총 예보건수'] * 100, 2)
        df['횟수%'] = round(df['횟수'] / row_sum['총 예보건수'] * 100, 2)
        df['WW&SS%'] = round(df['WW&SScount'] / row_sum['총 예보건수'] * 100, 2)
        df['TY&SS%'] = round(df['TY&SScount'] / row_sum['총 예보건수'] * 100, 2)
        return df
    
    def calculate_percentages2(df):
        df['WW%'] = df['WW%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['TY%'] = df['TY%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['횟수%'] = df['횟수%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['WW&SS%'] = df['WW&SS%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['TY&SS%'] = df['TY&SS%'].apply(lambda x: "{:.1f}".format(float(x)))  
        return df
    
    count_sk3 = pd.merge(SK_loc_row, count_sk3, on=['항로명','선박명'], how= 'inner')
    
    count_sk1 = calculate_percentages(count_sk1, sk_row_sum)
    count_sk2 = calculate_percentages(count_sk2, sk_row_sum)
    count_sk3 = calculate_percentages1(count_sk3, count_sk3)
    count_sk1 = calculate_percentages2(count_sk1)
    count_sk2 = calculate_percentages2(count_sk2)
    count_sk3 = calculate_percentages2(count_sk3)
    
    count_sk3.replace('A', np.nan, inplace=True)
    
    
    
    SK_new_order = ['항로명', '횟수','횟수%','TY','TY%','WW','WW%','WW&SScount','WW&SS%','TY&SScount','TY&SS%']
    count_sk1 = count_sk1.reindex(columns=SK_new_order)
    SK_new_order2 = ['항로명', '선박명','횟수','횟수%','TY','TY%','WW','WW%','WW&SScount','WW&SS%','TY&SScount','TY&SS%']
    count_sk2 = count_sk2.reindex(columns=SK_new_order2)
    SK_new_order5 = ['항로명', '선박명', '총 예보건수', '횟수','횟수%','TY','TY%','WW','WW%','WW&SScount','WW&SS%','TY&SScount','TY&SS%']
    count_sk3 = count_sk3.reindex(columns=SK_new_order5)
    
    
    count_sk3.to_excel('뱃멀미3_선박_특보.xlsx', encoding='euc-kr', float_format='%.1f', index=False)
    
    ##################################################################
    ##################################################################
    
# 서핑
# 파일 경로
mod_file = 'srmod.xlsx'
org_file = 'srorg.xlsx'
print()
print()
# 파일 존재 여부 확인
if not os.path.exists(mod_file) or not os.path.exists(org_file):
    print('SR자료가 없습니다')
else: 
    srm = pd.read_excel('srmod.xlsx')
    sro = pd.read_excel('srorg.xlsx')
    
    # 행의 갯수
    SR_row = srm.shape[0]
    
    # 같은 요소의 개수와 같은 권역의 개수를 세는 작업
    grouped = srm.groupby(['구분', '지역']).size().reset_index(name='총 예보건수')
    
    # 권역 요소별 총합 계산
    grouped_sum = grouped.groupby('구분')['총 예보건수'].sum().reset_index(name='총 예보건수')
    
    
    # 권역 요소 아래에 총합 행 추가
    result = pd.concat([grouped, grouped_sum])
    
    SR_new_order3 = ['황해중부', '제주도', '남해서부', '남해동부','동해남부','동해중부']
    result['구분'] = pd.Categorical(result['구분'], categories=SR_new_order3, ordered=True)
    result = result.sort_values(['구분','지역']).reset_index(drop=True)
    
    # 권역 열의 맨 아래에 총합 위치
    result.loc[result['지역'] == '총합', '구분'] = np.nan
    result = result.fillna('A')
    SR_loc_row = result
    
    sro['해상특보']=''
    sro['육상특보']=''
    sro['특보점수']=''
    
    srm1 = srm[["생산일","구분","지역","해상특보","육상특보","특보점수","예보지수"]]
    sro1 = sro[["생산일","구분","지역","해상특보","육상특보","특보점수","예보지수"]]
    
    sro1['특보점수'] = 100
    compare = srm1['특보점수'] == sro1['특보점수']
    csrm1 = srm1[~compare]
    csro1 = sro1[~compare]
    
    compare = csrm1['예보지수'] == csro1['예보지수']
    csrm = csrm1[~compare]
    csro = csro1[~compare]
    
    csrm_c = csrm.copy()
    
    csrm_c = csrm_c.sort_values(by=['구분','지역'], ascending=[True, True])
    csro = csro.sort_values(by=['구분','지역'], ascending=[True, True])
    
    
    csrm_c.rename(columns={'예보지수':'예보지수m'},inplace=True)
    csro.rename(columns={'예보지수':'예보지수o'},inplace=True)
    
    sr_result = pd.concat([csrm_c,csro],axis=1)
    
    # 중복된 열을 제거하여 유일한 값을 가지도록 만듦
    sr_result = sr_result.loc[:, ~sr_result.columns.duplicated(keep='first')]
    
    # 컬럼 순서 변경
    sr_result = sr_result[['생산일', '구분', '지역','해상특보','육상특보','특보점수','예보지수m','예보지수o']]
    
    sr_result = sr_result.reset_index(drop=True)
    sr_result.index = sr_result.index + 1
    
    # 셀 색칠 함수
    def highlight_diff(x, color):
        style = 'background-color: {}'.format(color)
        if x[0] != x[1]:
            return [style, style]
        else:
            return ['', '']
    def highlight_special_sea(row):
        if row.name == '해상특보':
            return ['background-color: orange' if x != '-' else '' for x in row]
        else:
            return [''] * len(row)
    def highlight_special_land(row):
        if row.name == '육상특보':
            return ['background-color: cyan' if x != '-' else '' for x in row]
        else:
            return [''] * len(row)     
    
    # 열 비교하여 값이 다른 경우 해당 셀 색칠
    sr_html = sr_result.style.apply(lambda x: highlight_special_sea(x), axis=0) \
                  .apply(lambda x: highlight_special_land(x), axis=0) \
                  .set_properties(**{'border': '1px solid black'})
    
    
    # 스타일이 적용된 데이터프레임을 HTML 파일로 저장
    with open('서핑1_특보.html', 'w') as f:
        f.write(sr_html.to_html())
    
    # 스타일이 적용된 데이터프레임을 xlsx 파일로 저장
    sr_html.to_excel('서핑1_특보.xlsx', index=True)
    
    #각 권역의 갯수, 각 지역의 갯수, 각 변경요인 갯수
    sr_loc = sr_result['구분'].value_counts().sort_index().to_frame(name='횟수').reset_index().rename(columns={'index': '구분'})
    sr_locp = sr_result.groupby(['구분', '지역'])['지역'].count().reset_index(name='횟수')
    
    #각 권역의 각각의 변경요인 갯수
    #각 지역의 각각의 변경요인 갯수
    def count_changes_SR(df, groupby_col, sea_warn_col='해상특보', land_warn_col='육상특보'):
        count = df.groupby(groupby_col).apply(lambda x: pd.Series({'지수count': (x['예보지수m'] != x['예보지수o']).sum(),
                                                                   'WW&SRcount': ((x[sea_warn_col].isin(['WW2', 'WW3', 'WW1'])) & (x[land_warn_col].isin(['SR2', 'SR3' 'SR1']))).sum(),
    'WW&SScount': ((x[sea_warn_col].isin(['WW2', 'WW3', 'WW1'])) & (x[land_warn_col].isin(['SS2', 'SS3', 'SS1']))).sum(),
    'TY&SRcount': ((x[sea_warn_col].isin(['TY2', 'TY3', 'TY1'])) & (x[land_warn_col].isin(['SR2', 'SR3', 'SR1']))).sum(),
    'TY&SScount': ((x[sea_warn_col].isin(['TY2', 'TY3', 'TY1'])) & (x[land_warn_col].isin(['SS2', 'SS3', 'SS1']))).sum()})).reset_index()
        
        # 해상 특보와 육상 특보에 대한 필터링 및 경고 횟수 계산
        sea_warn = df[df[sea_warn_col] != '-'].groupby(groupby_col + [sea_warn_col]).size().reset_index(name=sea_warn_col+'count')
        land_warn = df[df[land_warn_col] != '-'].groupby(groupby_col + [land_warn_col]).size().reset_index(name=land_warn_col+'count')
        # 피벗 테이블 생성
        sea_pivot = sea_warn.pivot_table(index=groupby_col, columns=sea_warn_col, values=sea_warn_col+'count', fill_value=0).reset_index()
        land_pivot = land_warn.pivot_table(index=groupby_col, columns=land_warn_col, values=land_warn_col+'count', fill_value=0).reset_index()
        # 경고 횟수 데이터를 count DataFrame에 추가
        count = count.merge(sea_pivot, on=groupby_col, how='left').fillna(0)
        count = count.merge(land_pivot, on=groupby_col, how='left').fillna(0)
        return count
    
    count_sr1 = count_changes_SR(sr_result, ['구분'])
    count_sr2 = count_changes_SR(sr_result, ['구분', '지역'])
    
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
    
    count_sr1 = combine_columns(count_sr1, 'WW2', 'WW3', 'WW_1')
    count_sr2 = combine_columns(count_sr2, 'WW2', 'WW3', 'WW_1')
    count_sr1 = combine_columns(count_sr1, 'WW_1', 'WW1', 'WW')
    count_sr2 = combine_columns(count_sr2, 'WW_1', 'WW1', 'WW')
    
    count_sr1 = combine_columns(count_sr1, 'SR2', 'SR3', 'SR_1')
    count_sr2 = combine_columns(count_sr2, 'SR2', 'SR3', 'SR_1')
    count_sr1 = combine_columns(count_sr1, 'SR_1', 'SR1', 'SR')
    count_sr2 = combine_columns(count_sr2, 'SR_1', 'SR1', 'SR')
    
    count_sr1 = combine_columns(count_sr1, 'SS2', 'SS3', 'SS_1')
    count_sr2 = combine_columns(count_sr2, 'SS2', 'SS3', 'SS_1')
    count_sr1 = combine_columns(count_sr1, 'SS_1', 'SS1', 'SS')
    count_sr2 = combine_columns(count_sr2, 'SS_1', 'SS1', 'SS')
    
    count_sr1 = combine_columns(count_sr1, 'TY1_x', 'TY2_x', 'TY_x')
    count_sr1 = combine_columns(count_sr1, 'TY1_y', 'TY2_y', 'TY_y')
    count_sr1 = combine_columns(count_sr1, 'TY_x', 'TY_y', 'TY_1')
    count_sr1 = combine_columns(count_sr1, 'TY_1', 'TY3', 'TY')
    count_sr2 = combine_columns(count_sr2, 'TY1_x', 'TY2_x', 'TY_x')
    count_sr2 = combine_columns(count_sr2, 'TY1_y', 'TY2_y', 'TY_y')
    count_sr2 = combine_columns(count_sr2, 'TY_x', 'TY_y', 'TY_1')
    count_sr2 = combine_columns(count_sr2, 'TY_1', 'TY3', 'TY')
    
    
    
    count_sr1 = pd.merge(count_sr1, sr_loc, on='구분')
    count_sr2 = pd.merge(count_sr2, sr_locp, on='지역')
    
    count_sr1['지역'] = np.nan
    count_sr2 = count_sr2.drop('구분_y', axis=1)
    count_sr2 = count_sr2.rename(columns={'구분_x':'구분'})
    SR_new_order1 = ['구분', '지역', '지수count','WW','TY','SS','SR', 'WW&SRcount','WW&SScount','TY&SRcount','TY&SScount','횟수']
    count_sr3 = pd.concat([count_sr1, count_sr2], ignore_index=True)
    count_sr3 = count_sr3.reindex(columns=SR_new_order1)
    
    count_sr3['구분'] = pd.Categorical(count_sr3['구분'], ordered=True)
    count_sr3 = count_sr3.sort_values(['구분','지역']).reset_index(drop=True)
    
    # 권역 열의 맨 아래에 총합 위치
    count_sr3.loc[result['지역'] == '총합', '구분'] = np.nan
    count_sr3 = count_sr3.fillna('A')
    
    sr_row_sum = count_sr1["횟수"].sum()
    
    print()
    print('SR 총통계')
    sr_sum_all = count_sr1.sum()
    sr_sum_all = pd.DataFrame(sr_sum_all, columns=['변경'])
    sr_sum_all = sr_sum_all.drop('구분', axis=0)
    sr_sum_all = sr_sum_all.rename(index={'횟수': '총예보지수변경'})
    print(sr_sum_all)
    sr_sum_all.to_csv('서핑2_요약_특보.csv', encoding='euc-kr', index=True)
    
    def calculate_percentages(df, row_sum):
        df['WW%'] = round(df['WW'] / row_sum * 100, 2)
        df['TY%'] = round(df['TY'] / row_sum * 100, 2)
        df['SS%'] = round(df['SS'] / row_sum * 100, 2)
        df['SR%'] = round(df['SR'] / row_sum * 100, 2)
        df['횟수%'] = round(df['횟수'] / row_sum * 100, 2)
        df['WW&SR%'] = round(df['WW&SRcount'] / row_sum * 100, 1)
        df['WW&SS%'] = round(df['WW&SScount'] / row_sum * 100, 1)
        df['TY&SR%'] = round(df['TY&SRcount'] / row_sum * 100, 1)
        df['TY&SS%'] = round(df['TY&SScount'] / row_sum * 100, 1)
        return df
    
    def calculate_percentages1(df, row_sum):
        df['WW%'] = round(df['WW'] / row_sum['총 예보건수'] * 100, 2)
        df['TY%'] = round(df['TY'] / row_sum['총 예보건수'] * 100, 2)
        df['SS%'] = round(df['SS'] / row_sum['총 예보건수'] * 100, 2)
        df['SR%'] = round(df['SR'] / row_sum['총 예보건수'] * 100, 2)
        df['횟수%'] = round(df['횟수'] / row_sum['총 예보건수'] * 100, 2)
        df['WW&SR%'] = round(df['WW&SRcount'] / row_sum['총 예보건수'] * 100, 2)
        df['WW&SS%'] = round(df['WW&SScount'] / row_sum['총 예보건수'] * 100, 2)
        df['TY&SR%'] = round(df['TY&SRcount'] / row_sum['총 예보건수'] * 100, 2)
        df['TY&SS%'] = round(df['TY&SScount'] / row_sum['총 예보건수'] * 100, 2)
        return df
    
    def calculate_percentages2(df):
        df['WW%'] = df['WW%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['TY%'] = df['TY%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['SS%'] = df['SS%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['SR%'] = df['SR%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['횟수%'] = df['횟수%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['WW&SR%'] = df['WW&SR%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['WW&SS%'] = df['WW&SS%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['TY&SR%'] = df['TY&SR%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['TY&SS%'] = df['TY&SS%'].apply(lambda x: "{:.1f}".format(float(x)))  
        return df
    
    count_sr3 = pd.merge(SR_loc_row, count_sr3, on=['구분','지역'], how= 'inner')
    
    count_sr1 = calculate_percentages(count_sr1, sr_row_sum)
    count_sr2 = calculate_percentages(count_sr2, sr_row_sum)
    count_sr3 = calculate_percentages1(count_sr3, count_sr3)
    count_sr1 = calculate_percentages2(count_sr1)
    count_sr2 = calculate_percentages2(count_sr2)
    count_sr3 = calculate_percentages2(count_sr3)
    
    count_sr3.replace('A', np.nan, inplace=True)
    
    
    SR_new_order = ['구분', '횟수','횟수%','TY','TY%','WW','WW%','SS','SS%','SR','SR%','WW&SRcount','WW&SR%','WW&SScount','WW&SS%','TY&SRcount','TY&SR%','TY&SScount','TY&SS%']
    count_sr1 = count_sr1.reindex(columns=SR_new_order)
    SR_new_order2 = ['구분', '지역','횟수','횟수%','TY','TY%','WW','WW%','SS','SS%','SR','SR%','WW&SRcount','WW&SR%','WW&SScount','WW&SS%','TY&SRcount','TY&SR%','TY&SScount','TY&SS%']
    count_sr2 = count_sr2.reindex(columns=SR_new_order2)
    SR_new_order5 = ['구분', '지역', '총 예보건수','횟수','횟수%','TY','TY%','WW','WW%','SS','SS%','SR','SR%','WW&SRcount','WW&SR%','WW&SScount','WW&SS%','TY&SRcount','TY&SR%','TY&SScount','TY&SS%']
    count_sr3 = count_sr3.reindex(columns=SR_new_order5)
    
    # 구분열 안의 요소들을 서해, 남해, 동해 순으로 배열
    SR_new_order3 = ['황해중부', '제주도', '남해서부', '남해동부','동해남부','동해중부']
    count_sr1['구분'] = pd.Categorical(count_sr1['구분'], categories=SR_new_order3, ordered=True)
    count_sr1 = count_sr1.sort_values('구분').reset_index(drop=True)
    count_sr2['구분'] = pd.Categorical(count_sr2['구분'], categories=SR_new_order3, ordered=True)
    count_sr2 = count_sr2.sort_values(['구분','지역']).reset_index(drop=True)
    count_sr3['구분'] = pd.Categorical(count_sr3['구분'], categories=SR_new_order3, ordered=True)
    count_sr3 = count_sr3.sort_values(['구분','지역']).reset_index(drop=True)
    
    
    count_sr3.to_excel('서핑3_지역_특보.xlsx', encoding='euc-kr', float_format='%.1f', index=False)
    
    ##################################################################
    ##################################################################
    
# 해수욕
# 파일 경로
mod_file = 'spmod.xlsx'
org_file = 'sporg.xlsx'
print()
print()
# 파일 존재 여부 확인
if not os.path.exists(mod_file) or not os.path.exists(org_file):
    print('SP자료가 없습니다')
else:     
    spm = pd.read_excel('spmod.xlsx')
    spo = pd.read_excel('sporg.xlsx')
    
    SP_row = spm.shape[0]
    
    # 같은 요소의 개수와 같은 권역의 개수를 세는 작업
    grouped = spm.groupby(['권역', '해수욕장']).size().reset_index(name='총 예보건수')
    
    # 권역 요소별 총합 계산
    grouped_sum = grouped.groupby('권역')['총 예보건수'].sum().reset_index(name='총 예보건수')
    
    
    # 권역 요소 아래에 총합 행 추가
    result = pd.concat([grouped, grouped_sum])
    
    SP_new_order3 = ['황해중부', '황해남부', '남해서부','남해동부', '제주도', '동해남부', '동해중부']
    result['권역'] = pd.Categorical(result['권역'], categories=SP_new_order3, ordered=True)
    result = result.sort_values(['권역','해수욕장']).reset_index(drop=True)
    
    # 권역 열의 맨 아래에 총합 위치
    result.loc[result['해수욕장'] == '총합', '권역'] = np.nan
    result = result.fillna('A')
    SP_loc_row = result
    
    
    spo['해상특보']=''
    spo['육상특보']=''
    spo['특보점수']=''
    spo['강수량점수']=''
    
    spm1 = spm[["생산일","권역","해수욕장","해상특보","육상특보","특보점수","강수량점수","예보지수"]]
    spo1 = spo[["생산일","권역","해수욕장","해상특보","육상특보","특보점수","강수량점수","예보지수"]]
    
    spo1['특보점수'] = 100
    spo1['강수량점수'] = 100
    
    compare = spm1['예보지수'] == spo1['예보지수']
    cspm1 = spm1[~compare]
    cspo1 = spo1[~compare]
    
    compare = (cspm1['특보점수'] != cspo1['특보점수']) | (cspm1['강수량점수'] != cspo1['강수량점수'])
    cspm = cspm1[compare]
    cspo = cspo1[compare]
    
    
    cspm_c = cspm.copy()
    
    #cspm_c['강수량']=spm["강수량"]
    cspm_c['강수량점수']=spm["강수량점수"]
    
    cspm_c = cspm_c.sort_values(by=['권역','해수욕장'], ascending=[True, True])
    cspo = cspo.sort_values(by=['권역','해수욕장'], ascending=[True, True])
    
    
    cspm_c.rename(columns={'예보지수':'예보지수m'},inplace=True)
    cspo.rename(columns={'예보지수':'예보지수o'},inplace=True)
    
    sp_result = pd.concat([cspm_c,cspo],axis=1)
    
    # 중복된 열을 제거하여 유일한 값을 가지도록 만듦
    sp_result = sp_result.loc[:, ~sp_result.columns.duplicated(keep='first')]
    
    # 컬럼 순서 변경
    sp_result = sp_result[['생산일', '권역', '해수욕장', '강수량점수','해상특보','육상특보','특보점수','예보지수m','예보지수o']]
    sp_result = sp_result.reset_index(drop=True)
    sp_result.index = sp_result.index + 1
    
    # 셀 색칠 함수
    def highlight_diff(x, color):
        style = 'background-color: {}'.format(color)
        if x[0] != x[1]:
            return [style, style]
        else:
            return ['', '']
    
    def highlight_special_R(row):
        if row.name == '강수량점수':
            return ['background-color: orange' if x != 100 else '' for x in row]
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
    sp_html = sp_result.style.apply(lambda x: highlight_special_R(x), axis=0) \
                  .apply(lambda x: highlight_special_sea(x), axis=0) \
                  .apply(lambda x: highlight_special_land(x), axis=0) \
                  .set_properties(**{'border': '1px solid black'})
    
    # 스타일이 적용된 데이터프레임을 HTML 파일로 저장
    with open('해수욕1_특보.html', 'w') as f:
        f.write(sp_html.to_html())
        
    # 스타일이 적용된 데이터프레임을 xlsx 파일로 저장
    sp_html.to_excel('해수욕1_특보.xlsx', index=True)
    
    #각 권역의 갯수, 각 지역의 갯수, 각 변경요인 갯수
    sp_loc = sp_result['권역'].value_counts().sort_index().to_frame(name='횟수').reset_index().rename(columns={'index': '권역'})
    sp_locp = sp_result.groupby(['권역', '해수욕장'])['해수욕장'].count().reset_index(name='횟수')
    
    #각 권역의 각각의 변경요인 갯수
    #각 지역의 각각의 변경요인 갯수
    def count_changes_sp1(df, groupby_col, sea_warn_col='해상특보', land_warn_col='육상특보', rain_col='강수량점수'):
        count = df.groupby(groupby_col).apply(lambda x: pd.Series({'TY&RAINcount': ((x[sea_warn_col].isin(['TY2', 'TY3', 'TY1'])) & (x[rain_col] != 100)).sum(),
                                                                      'WW&RAINcount': ((x[sea_warn_col].isin(['WW2', 'WW3', 'WW1'])) & (x[rain_col] != 100)).sum(),
                                                                      'SR&RAINcount': ((x[land_warn_col].isin(['SR2', 'SR3', 'SR1'])) & (x[rain_col] != 100)).sum(),
                                                                      'SS&RAINcount': ((x[land_warn_col].isin(['SS2', 'SS3', 'SS1'])) & (x[rain_col] != 100)).sum(),
                                                                      'WW&SRcount': ((x[sea_warn_col].isin(['WW2', 'WW3', 'WW1'])) & (x[land_warn_col].isin(['SR2', 'SR3', 'SR1']))).sum(),
    'WW&SScount': ((x[sea_warn_col].isin(['WW2', 'WW3', 'WW1'])) & (x[land_warn_col].isin(['SS2', 'SS3', 'SS1']))).sum(),
    'TY&SRcount': ((x[sea_warn_col].isin(['TY2', 'TY3', 'TY1'])) & (x[land_warn_col].isin(['SR2', 'SR3', 'SR1']))).sum(),
    'TY&SScount': ((x[sea_warn_col].isin(['TY2', 'TY3', 'TY1'])) & (x[land_warn_col].isin(['SS2', 'SS3', 'SS1']))).sum(),
    'WW&SR&RAINcount': ((x[sea_warn_col].isin(['WW2', 'WW3', 'WW1'])) & (x[land_warn_col].isin(['SR2', 'SR3', 'SR1'])) & (x[rain_col] != 100)).sum(),
    'WW&SS&RAINcount': ((x[sea_warn_col].isin(['WW2', 'WW3', 'WW1'])) & (x[land_warn_col].isin(['SS2', 'SS3', 'SS1'])) & (x[rain_col] != 100)).sum(),
    'TY&SR&RAINcount': ((x[sea_warn_col].isin(['TY2', 'TY3', 'TY1'])) & (x[land_warn_col].isin(['SR2', 'SR3', 'SR1'])) & (x[rain_col] != 100)).sum(),
    'TY&SS&RAINcount': ((x[sea_warn_col].isin(['TY2', 'TY3', 'TY1'])) & (x[land_warn_col].isin(['SS2', 'SS3', 'SS1'])) & (x[rain_col] != 100)).sum()})).reset_index()
    
    
    
        # 해상 특보와 육상 특보에 대한 필터링 및 경고 횟수 계산
        sea_warn = df[df[sea_warn_col] != '-'].groupby(groupby_col + [sea_warn_col]).size().reset_index(name=sea_warn_col+'count')
        land_warn = df[df[land_warn_col].isin(['SR2', 'SR3', 'SS2', 'SS3'])].groupby(groupby_col + [land_warn_col]).size().reset_index(name=land_warn_col+'count')
        # 피벗 테이블 생성
        sea_pivot = sea_warn.pivot_table(index=groupby_col, columns=sea_warn_col, values=sea_warn_col+'count', fill_value=0).reset_index()
        land_pivot = land_warn.pivot_table(index=groupby_col, columns=land_warn_col, values=land_warn_col+'count', fill_value=0).reset_index()
        # 경고 횟수 데이터를 count DataFrame에 추가
        count = count.merge(sea_pivot, on=groupby_col, how='left').fillna(0)
        count = count.merge(land_pivot, on=groupby_col, how='left').fillna(0)
        
        rain = df[df[rain_col] != 100].groupby(groupby_col + [rain_col]).size().reset_index(name=rain_col+'count')
        rain_pivot = rain.pivot_table(index=groupby_col, columns=rain_col, values=rain_col+'count', fill_value=0).reset_index()
        rain_pivot[rain_col+'count'] = rain_pivot[rain_pivot.columns[1:]].sum(axis=1)
        rain_pivot = rain_pivot.drop(columns=rain_pivot.columns[1:-1])
        
        count = count.merge(rain_pivot, on=groupby_col, how='left').fillna(0)
        
        return count
    
    def count_changes_sp2(df, groupby_col, sea_warn_col='해상특보', land_warn_col='육상특보', rain_col='강수량점수'):
        count = df.groupby(groupby_col).apply(lambda x: pd.Series({'TY&RAINcount': ((x[sea_warn_col].isin(['TY2', 'TY3', 'TY1'])) & (x[rain_col] != 100)).sum(),
                                                                      'WW&RAINcount': ((x[sea_warn_col].isin(['WW2', 'WW3', 'WW1'])) & (x[rain_col] != 100)).sum(),
                                                                      'SR&RAINcount': ((x[land_warn_col].isin(['SR2', 'SR3', 'SR1'])) & (x[rain_col] != 100)).sum(),
                                                                      'SS&RAINcount': ((x[land_warn_col].isin(['SS2', 'SS3', 'SS1'])) & (x[rain_col] != 100)).sum(),
                                                                      'WW&SRcount': ((x[sea_warn_col].isin(['WW2', 'WW3', 'WW1'])) & (x[land_warn_col].isin(['SR2', 'SR3', 'SR1']))).sum(),
    'WW&SScount': ((x[sea_warn_col].isin(['WW2', 'WW3', 'WW1'])) & (x[land_warn_col].isin(['SS2', 'SS3', 'SS1']))).sum(),
    'TY&SRcount': ((x[sea_warn_col].isin(['TY2', 'TY3', 'TY1'])) & (x[land_warn_col].isin(['SR2', 'SR3', 'SR1']))).sum(),
    'TY&SScount': ((x[sea_warn_col].isin(['TY2', 'TY3', 'TY1'])) & (x[land_warn_col].isin(['SS2', 'SS3', 'SS1']))).sum(),
    'WW&SR&RAINcount': ((x[sea_warn_col].isin(['WW2', 'WW3', 'WW1'])) & (x[land_warn_col].isin(['SR2', 'SR3', 'SR1'])) & (x[rain_col] != 100)).sum(),
    'WW&SS&RAINcount': ((x[sea_warn_col].isin(['WW2', 'WW3', 'WW1'])) & (x[land_warn_col].isin(['SS2', 'SS3', 'SS1'])) & (x[rain_col] != 100)).sum(),
    'TY&SR&RAINcount': ((x[sea_warn_col].isin(['TY2', 'TY3', 'TY1'])) & (x[land_warn_col].isin(['SR2', 'SR3', 'SR1'])) & (x[rain_col] != 100)).sum(),
    'TY&SS&RAINcount': ((x[sea_warn_col].isin(['TY2', 'TY3', 'TY1'])) & (x[land_warn_col].isin(['SS2', 'SS3', 'SS1'])) & (x[rain_col] != 100)).sum()})).reset_index()
        
        
        # 해상 특보와 육상 특보에 대한 필터링 및 경고 횟수 계산
        sea_warn = df[df[sea_warn_col] != '-'].groupby(groupby_col + [sea_warn_col]).size().reset_index(name=sea_warn_col+'count')
        land_warn = df[df[land_warn_col].isin(['SR2', 'SR3', 'SS2', 'SS3'])].groupby(groupby_col + [land_warn_col]).size().reset_index(name=land_warn_col+'count')
        # 피벗 테이블 생성
        sea_pivot = sea_warn.pivot_table(index=groupby_col, columns=sea_warn_col, values=sea_warn_col+'count', fill_value=0).reset_index()
        land_pivot = land_warn.pivot_table(index=groupby_col, columns=land_warn_col, values=land_warn_col+'count', fill_value=0).reset_index()
        # 경고 횟수 데이터를 count DataFrame에 추가
        count = count.merge(sea_pivot, on=groupby_col, how='left').fillna(0)
        count = count.merge(land_pivot, on=groupby_col, how='left').fillna(0)
        
        rain = df[df[rain_col] != 100].groupby(groupby_col + [rain_col]).size().reset_index(name=rain_col+'count')
        rain_pivot = rain.pivot_table(index=groupby_col, columns=rain_col, values=rain_col+'count', fill_value=0).reset_index()
        rain_pivot[rain_col+'count'] = rain_pivot[rain_pivot.columns[1:]].sum(axis=1)
        rain_pivot = rain_pivot.drop(columns=rain_pivot.columns[2:-1])
        
        count = count.merge(rain_pivot, on=groupby_col, how='left').fillna(0)
        
        return count
    
    
    count2_sp1 = count_changes_sp1(sp_result, ['권역'])
    count2_sp1 = count2_sp1.groupby('권역').agg('sum').reset_index()
    count2_sp2 = count_changes_sp2(sp_result, ['권역', '해수욕장'])
    
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
    
    count2_sp1 = combine_columns(count2_sp1, 'WW2', 'WW3', 'WW_1')
    count2_sp2 = combine_columns(count2_sp2, 'WW2', 'WW3', 'WW_1')
    count2_sp1 = combine_columns(count2_sp1, 'WW_1', 'WW1', 'WW')
    count2_sp2 = combine_columns(count2_sp2, 'WW_1', 'WW1', 'WW')
    
    count2_sp1 = combine_columns(count2_sp1, 'TY1_x', 'TY2_x', 'TY_x')
    count2_sp1 = combine_columns(count2_sp1, 'TY1_y', 'TY2_y', 'TY_y')
    count2_sp1 = combine_columns(count2_sp1, 'TY_x', 'TY_y', 'TY_1')
    count2_sp1 = combine_columns(count2_sp1, 'TY_1', 'TY3', 'TY')
    count2_sp2 = combine_columns(count2_sp2, 'TY1_x', 'TY2_x', 'TY_x')
    count2_sp2 = combine_columns(count2_sp2, 'TY1_y', 'TY2_y', 'TY_y')
    count2_sp2 = combine_columns(count2_sp2, 'TY_x', 'TY_y', 'TY_1')
    count2_sp2 = combine_columns(count2_sp2, 'TY_1', 'TY3', 'TY')
    
    count2_sp1 = combine_columns(count2_sp1, 'SS2', 'SS3', 'SS_1')
    count2_sp2 = combine_columns(count2_sp2, 'SS2', 'SS3', 'SS_1')
    count2_sp1 = combine_columns(count2_sp1, 'SS_1', 'SS1', 'SS')
    count2_sp2 = combine_columns(count2_sp2, 'SS_1', 'SS1', 'SS')
    
    count2_sp1 = combine_columns(count2_sp1, 'SR2', 'SR3', 'SR_1')
    count2_sp2 = combine_columns(count2_sp2, 'SR2', 'SR3', 'SR_1')
    count2_sp1 = combine_columns(count2_sp1, 'SR_1', 'SR1', 'SR')
    count2_sp2 = combine_columns(count2_sp2, 'SR_1', 'SR1', 'SR')
    
 
    count2_sp2 = count2_sp2.groupby(['권역', '해수욕장']).sum().reset_index()
    
    
    count2_sp1 = pd.merge(count2_sp1, sp_loc, on='권역')
    count2_sp2 = pd.merge(count2_sp2, sp_locp, on='해수욕장')
    
    count2_sp1['해수욕장'] = np.nan
    
    
    
    count2_sp2 = count2_sp2.drop('권역_y', axis=1)
    count2_sp2 = count2_sp2.rename(columns={'권역_x':'권역'})
    sp_new_order1 = ['권역', '해수욕장','WW','TY','SR','SS','강수량점수','강수량점수count','TY&RAINcount','WW&RAINcount','SS&RAINcount','SR&RAINcount','WW&SRcount','WW&SScount','TY&SRcount','TY&SScount','WW&SR&RAINcount','WW&SS&RAINcount','TY&SR&RAINcount','TY&SS&RAINcount','횟수']
    count2_sp1 = count2_sp1.reindex(columns=sp_new_order1)
    count2_sp3 = pd.concat([count2_sp1, count2_sp2]).reset_index(drop=True)
    count2_sp3.sort_values(by=['권역','해수욕장'], inplace=True)
    count2_sp3 = count2_sp3.reindex(columns=sp_new_order1)
    
    
    
    count2_sp3['권역'] = pd.Categorical(count2_sp3['권역'], categories=SP_new_order3, ordered=True)
    count2_sp3 = count2_sp3.sort_values(['권역','해수욕장']).reset_index(drop=True)
    
    
    
    count2_sp3 = count2_sp3.fillna('A')
    
    sp_row_sum = count2_sp2["횟수"].sum()
    print()
    print('sp_특보_총통계')
    sp_sum_all = count2_sp1.sum()
    sp_sum_all = pd.DataFrame(sp_sum_all, columns=['변경'])
    sp_sum_all = sp_sum_all.drop('권역', axis=0)
    sp_sum_all = sp_sum_all.rename(index={'횟수': '총예보지수변경'})
    print(sp_sum_all)
    sp_sum_all.to_csv('해수욕2_특보_요약.csv', encoding='euc-kr', index=True)
    print('해수욕_특보 총예보건수', SP_row)
    
    
    def calculate_percentages(df, row_sum):
        df['강수량점수%'] = round(df['강수량점수count'] / row_sum * 100, 2)
        df['WW%'] = round(df['WW'] / row_sum * 100, 2)
        df['TY%'] = round(df['TY'] / row_sum * 100, 2)
        df['SS%'] = round(df['SS'] / row_sum * 100, 2)
        df['SR%'] = round(df['SR'] / row_sum * 100, 2)
        df['횟수%'] = round(df['횟수'] / row_sum * 100, 2)
        df['TY&RAIN%'] = round(df['TY&RAINcount'] / row_sum * 100, 2)
        df['WW&RAIN%'] = round(df['WW&RAINcount'] / row_sum * 100, 2)
        df['SS&RAIN%'] = round(df['SS&RAINcount'] / row_sum * 100, 2)
        df['SR&RAIN%'] = round(df['SR&RAINcount'] / row_sum * 100, 2)
        df['WW&SR%'] = round(df['WW&SRcount'] / row_sum * 100, 1)
        df['WW&SS%'] = round(df['WW&SScount'] / row_sum * 100, 1)
        df['TY&SR%'] = round(df['TY&SRcount'] / row_sum * 100, 1)
        df['TY&SS%'] = round(df['TY&SScount'] / row_sum * 100, 1)
        df['WW&SR&RAIN%'] = round(df['WW&SR&RAINcount'] / row_sum * 100, 1)
        df['WW&SS&RAIN%'] = round(df['WW&SS&RAINcount'] / row_sum * 100, 1)
        df['TY&SR&RAIN%'] = round(df['TY&SR&RAINcount'] / row_sum * 100, 1)
        df['TY&SS&RAIN%'] = round(df['TY&SS&RAINcount'] / row_sum * 100, 1)
        return df
    
    def calculate_percentages1(df, row_sum):
        df['강수량점수%'] = round(df['강수량점수count'] / row_sum['총 예보건수'] * 100, 2)
        df['WW%'] = round(df['WW'] / row_sum['총 예보건수'] * 100, 2)
        df['TY%'] = round(df['TY'] / row_sum['총 예보건수'] * 100, 2)
        df['SS%'] = round(df['SS'] / row_sum['총 예보건수'] * 100, 2)
        df['SR%'] = round(df['SR'] / row_sum['총 예보건수'] * 100, 2)
        df['횟수%'] = round(df['횟수'] / row_sum['총 예보건수'] * 100, 2)
        df['TY&RAIN%'] = round(df['TY&RAINcount'] / row_sum['총 예보건수'] * 100, 2)
        df['WW&RAIN%'] = round(df['WW&RAINcount'] / row_sum['총 예보건수'] * 100, 2)
        df['SS&RAIN%'] = round(df['SS&RAINcount'] / row_sum['총 예보건수'] * 100, 2)
        df['SR&RAIN%'] = round(df['SR&RAINcount'] / row_sum['총 예보건수'] * 100, 2)
        df['WW&SR%'] = round(df['WW&SRcount'] / row_sum['총 예보건수'] * 100, 2)
        df['WW&SS%'] = round(df['WW&SScount'] / row_sum['총 예보건수'] * 100, 2)
        df['TY&SR%'] = round(df['TY&SRcount'] / row_sum['총 예보건수'] * 100, 2)
        df['TY&SS%'] = round(df['TY&SScount'] / row_sum['총 예보건수'] * 100, 2)
        df['WW&SR&RAIN%'] = round(df['WW&SR&RAINcount'] / row_sum['총 예보건수'] * 100, 2)
        df['WW&SS&RAIN%'] = round(df['WW&SS&RAINcount'] / row_sum['총 예보건수'] * 100, 2)
        df['TY&SR&RAIN%'] = round(df['TY&SR&RAINcount'] / row_sum['총 예보건수'] * 100, 2)
        df['TY&SS&RAIN%'] = round(df['TY&SS&RAINcount'] / row_sum['총 예보건수'] * 100, 2)
        return df
    
    def calculate_percentages2(df):
        df['강수량점수%'] = df['강수량점수%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['WW%'] = df['WW%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['TY%'] = df['TY%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['SS%'] = df['SS%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['SR%'] = df['SR%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['횟수%'] = df['횟수%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['TY&RAIN%'] = df['TY&RAIN%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['WW&RAIN%'] = df['WW&RAIN%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['SS&RAIN%'] = df['SS&RAIN%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['SR&RAIN%'] = df['SR&RAIN%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['WW&SR%'] = df['WW&SR%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['WW&SS%'] = df['WW&SS%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['TY&SR%'] = df['TY&SR%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['TY&SS%'] = df['TY&SS%'].apply(lambda x: "{:.1f}".format(float(x)))  
        df['WW&SR&RAIN%'] = df['WW&SR&RAIN%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['WW&SS&RAIN%'] = df['WW&SS&RAIN%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['TY&SR&RAIN%'] = df['TY&SR&RAIN%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['TY&SS&RAIN%'] = df['TY&SS&RAIN%'].apply(lambda x: "{:.1f}".format(float(x)))    
        return df 
    
    count2_sp3 = pd.merge(SP_loc_row, count2_sp3, on=['권역','해수욕장'], how= 'inner')
    
    count2_sp1 = calculate_percentages(count2_sp1, sp_row_sum)
    count2_sp2 = calculate_percentages(count2_sp2, sp_row_sum)
    count2_sp3 = calculate_percentages1(count2_sp3, count2_sp3)
    count2_sp1 = calculate_percentages2(count2_sp1)
    count2_sp2 = calculate_percentages2(count2_sp2)
    count2_sp3 = calculate_percentages2(count2_sp3)
    
    count2_sp3.replace('A', np.nan, inplace=True)
    
    
    sp_new_order = ['권역', '횟수','횟수%', 'TY','TY%','WW','WW%', 'SS','SS%', 'SR','SR%', '강수량점수count','강수량점수%', 'TY&RAINcount','TY&RAIN%', 'WW&RAINcount','WW&RAIN%', 'SS&RAINcount','SS&RAIN%', 'SR&RAINcount','SR&RAIN%','WW&SRcount','WW&SR%','WW&SScount','WW&SS%','TY&SRcount','TY&SR%','TY&SScount','TY&SS%','WW&SR&RAINcount','WW&SR&RAIN%','WW&SS&RAINcount','WW&SS&RAIN%','TY&SR&RAINcount','TY&SR&RAIN%','TY&SS&RAINcount','TY&SS&RAIN%']
    count2_sp1 = count2_sp1.reindex(columns=sp_new_order)
    sp_new_order2 = ['권역', '해수욕장','횟수','횟수%', 'TY','TY%','WW','WW%', 'SS','SS%', 'SR','SR%', '강수량점수count','강수량점수%','TY&RAINcount','TY&RAIN%', 'WW&RAINcount','WW&RAIN%', 'SS&RAINcount','SS&RAIN%', 'SR&RAINcount','SR&RAIN%','WW&SRcount','WW&SR%','WW&SScount','WW&SS%','TY&SRcount','TY&SR%','TY&SScount','TY&SS%','WW&SR&RAINcount','WW&SR&RAIN%','WW&SS&RAINcount','WW&SS&RAIN%','TY&SR&RAINcount','TY&SR&RAIN%','TY&SS&RAINcount','TY&SS&RAIN%']
    count2_sp2 = count2_sp2.reindex(columns=sp_new_order2)
    sp_new_order5 = ['권역', '해수욕장', '총 예보건수','횟수','횟수%', 'TY','TY%','WW','WW%', 'SS','SS%', 'SR','SR%', '강수량점수count','강수량점수%','TY&RAINcount','TY&RAIN%', 'WW&RAINcount','WW&RAIN%', 'SS&RAINcount','SS&RAIN%', 'SR&RAINcount','SR&RAIN%','WW&SRcount','WW&SR%','WW&SScount','WW&SS%','TY&SRcount','TY&SR%','TY&SScount','TY&SS%','WW&SR&RAINcount','WW&SR&RAIN%','WW&SS&RAINcount','WW&SS&RAIN%','TY&SR&RAINcount','TY&SR&RAIN%','TY&SS&RAINcount','TY&SS&RAIN%']
    count2_sp3 = count2_sp3.reindex(columns=sp_new_order5)
    
    
    # 구분열 안의 요소들을 서해, 남해, 동해 순으로 배열
    sp_new_order3 = ['황해중부', '황해남부', '남해서부','남해동부', '제주도', '동해남부', '동해중부']
    count2_sp1['권역'] = pd.Categorical(count2_sp1['권역'], categories=sp_new_order3, ordered=True)
    count2_sp1 = count2_sp1.sort_values('권역').reset_index(drop=True)
    count2_sp2['권역'] = pd.Categorical(count2_sp2['권역'], categories=sp_new_order3, ordered=True)
    count2_sp2 = count2_sp2.sort_values(['권역','해수욕장']).reset_index(drop=True)
    count2_sp3['권역'] = pd.Categorical(count2_sp3['권역'], categories=sp_new_order3, ordered=True)
    count2_sp3 = count2_sp3.sort_values(['권역','해수욕장']).reset_index(drop=True)
    
    count2_sp3.to_excel('해수욕3_지역_특보.xlsx', encoding='euc-kr', float_format='%.1f', index=False)
    
    ##################################################################
    ##################################################################
    
# 스킨스쿠버
# 파일 경로
mod_file = 'ssmod.xlsx'
org_file = 'ssorg.xlsx'
print()
print()
# 파일 존재 여부 확인
if not os.path.exists(mod_file) or not os.path.exists(org_file):
    print('SS자료가 없습니다')
else:     
    ssm = pd.read_excel('ssmod.xlsx')
    sso = pd.read_excel('ssorg.xlsx')
    
    # 행의 갯수
    SS_row = ssm.shape[0]
    
    # 같은 요소의 개수와 같은 권역의 개수를 세는 작업
    grouped = ssm.groupby(['권역', '지역']).size().reset_index(name='총 예보건수')
    
    # 권역 요소별 총합 계산
    grouped_sum = grouped.groupby('권역')['총 예보건수'].sum().reset_index(name='총 예보건수')
    
    
    # 권역 요소 아래에 총합 행 추가
    result = pd.concat([grouped, grouped_sum])
    
    SS_new_order3 = ['황해중부', '황해남부', '남해서부', '남해동부', '제주도', '동해남부', '동해중부']
    result['권역'] = pd.Categorical(result['권역'], categories=SS_new_order3, ordered=True)
    result = result.sort_values(['권역','지역']).reset_index(drop=True)
    
    # 권역 열의 맨 아래에 총합 위치
    result.loc[result['지역'] == '총합', '권역'] = np.nan
    result = result.fillna('A')
    SS_loc_row = result
    
    sso['해상특보']=''
    sso['육상특보']=''
    sso['특보점수']=''
    
    ssm1 = ssm[["생산일","권역","지역","해상특보","육상특보","특보점수","예보지수"]]
    sso1 = sso[["생산일","권역","지역","해상특보","육상특보","특보점수","예보지수"]]
    
    sso1['특보점수'] = 100
    compare = ssm1['특보점수'] == sso1['특보점수']
    cssm1 = ssm1[~compare]
    csso1 = sso1[~compare]
    
    compare = cssm1['예보지수'] == csso1['예보지수']
    cssm = cssm1[~compare]
    csso = csso1[~compare]
    
    cssm_c = cssm.copy()
    
    cssm_c = cssm_c.sort_values(by=['권역','지역'], ascending=[True, True])
    csso = csso.sort_values(by=['권역','지역'], ascending=[True, True])
    
    
    cssm_c.rename(columns={'예보지수':'예보지수m'},inplace=True)
    csso.rename(columns={'예보지수':'예보지수o'},inplace=True)
    
    ss_result = pd.concat([cssm_c,csso],axis=1)
    
    # 중복된 열을 제거하여 유일한 값을 가지도록 만듦
    ss_result = ss_result.loc[:, ~ss_result.columns.duplicated(keep='first')]
    
    # 컬럼 순서 변경
    ss_result = ss_result[['생산일', '권역', '지역','해상특보','육상특보','특보점수','예보지수m','예보지수o']]
    
    ss_result = ss_result.reset_index(drop=True)
    ss_result.index = ss_result.index + 1
    
    # 셀 색칠 함수
    def highlight_diff(x, color):
        style = 'background-color: {}'.format(color)
        if x[0] != x[1]:
            return [style, style]
        else:
            return ['', '']
    def highlight_special_sea(row):
        if row.name == '해상특보':
            return ['background-color: orange' if x != '-' else '' for x in row]
        else:
            return [''] * len(row)
    def highlight_special_land(row):
        if row.name == '육상특보':
            return ['background-color: cyan' if x != '-' else '' for x in row]
        else:
            return [''] * len(row)     
    
    # 열 비교하여 값이 다른 경우 해당 셀 색칠
    ss_html = ss_result.style.apply(lambda x: highlight_special_sea(x), axis=0) \
                  .apply(lambda x: highlight_special_land(x), axis=0) \
                  .set_properties(**{'border': '1px solid black'})
    
    
    # 스타일이 적용된 데이터프레임을 HTML 파일로 저장
    with open('스킨스쿠버1_특보.html', 'w') as f:
        f.write(ss_html.to_html())
    
    # 스타일이 적용된 데이터프레임을 xlsx 파일로 저장
    ss_html.to_excel('스킨스쿠버1_특보.xlsx', index=True)
    
    #각 권역의 갯수, 각 지역의 갯수, 각 변경요인 갯수
    ss_loc = ss_result['권역'].value_counts().sort_index().to_frame(name='횟수').reset_index().rename(columns={'index': '권역'})
    ss_locp = ss_result.groupby(['권역', '지역'])['지역'].count().reset_index(name='횟수')
    
    #각 권역의 각각의 변경요인 갯수
    #각 지역의 각각의 변경요인 갯수
    def count_changes_SS(df, groupby_col, sea_warn_col='해상특보', land_warn_col='육상특보'):
        count = df.groupby(groupby_col).apply(lambda x: pd.Series({'지수count': (x['예보지수m'] != x['예보지수o']).sum(),
                                                                   'WW&SRcount': ((x[sea_warn_col].isin(['WW2', 'WW3','WW1'])) & (x[land_warn_col].isin(['SR2', 'SR3', 'SR1']))).sum(),
    'WW&SScount': ((x[sea_warn_col].isin(['WW2', 'WW3','WW1'])) & (x[land_warn_col].isin(['SS2', 'SS3', 'SS1']))).sum(),
    'TY&SRcount': ((x[sea_warn_col].isin(['TY2', 'TY3', 'TY1'])) & (x[land_warn_col].isin(['SR2', 'SR3', 'SR1']))).sum(),
    'TY&SScount': ((x[sea_warn_col].isin(['TY2', 'TY3', 'TY1'])) & (x[land_warn_col].isin(['SS2', 'SS3' 'SS1']))).sum()})).reset_index()
        
        # 해상 특보와 육상 특보에 대한 필터링 및 경고 횟수 계산
        sea_warn = df[df[sea_warn_col] != '-'].groupby(groupby_col + [sea_warn_col]).size().reset_index(name=sea_warn_col+'count')
        land_warn = df[df[land_warn_col] != '-'].groupby(groupby_col + [land_warn_col]).size().reset_index(name=land_warn_col+'count')
        # 피벗 테이블 생성
        sea_pivot = sea_warn.pivot_table(index=groupby_col, columns=sea_warn_col, values=sea_warn_col+'count', fill_value=0).reset_index()
        land_pivot = land_warn.pivot_table(index=groupby_col, columns=land_warn_col, values=land_warn_col+'count', fill_value=0).reset_index()
        # 경고 횟수 데이터를 count DataFrame에 추가
        count = count.merge(sea_pivot, on=groupby_col, how='left').fillna(0)
        count = count.merge(land_pivot, on=groupby_col, how='left').fillna(0)
        return count
    
    count_ss1 = count_changes_SS(ss_result, ['권역'])
    count_ss2 = count_changes_SS(ss_result, ['권역', '지역'])
    
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
    
    
    
    count_ss1 = combine_columns(count_ss1, 'WW2', 'WW3', 'WW_1')
    count_ss2 = combine_columns(count_ss2, 'WW2', 'WW3', 'WW_1')
    count_ss1 = combine_columns(count_ss1, 'WW_1', 'WW1', 'WW')
    count_ss2 = combine_columns(count_ss2, 'WW_1', 'WW1', 'WW')
    
    
    count_ss1 = combine_columns(count_ss1, 'SR2', 'SR3', 'SR_1')
    count_ss2 = combine_columns(count_ss2, 'SR2', 'SR3', 'SR_1')
    count_ss1 = combine_columns(count_ss1, 'SR_1', 'SR1', 'SR')
    count_ss2 = combine_columns(count_ss2, 'SR_1', 'SR1', 'SR')
    
    count_ss1 = combine_columns(count_ss1, 'SS2', 'SS3', 'SS_1')
    count_ss2 = combine_columns(count_ss2, 'SS2', 'SS3', 'SS_1')
    count_ss1 = combine_columns(count_ss1, 'SS_1', 'SS1', 'SS')
    count_ss2 = combine_columns(count_ss2, 'SS_1', 'SS1', 'SS')
    
    count_ss1 = combine_columns(count_ss1, 'TY1_x', 'TY2_x', 'TY_x1')
    count_ss1 = combine_columns(count_ss1, 'TY_x1', 'TY3_x', 'TY_x')
    count_ss1 = combine_columns(count_ss1, 'TY1_y', 'TY2_y', 'TY_y1')
    count_ss1 = combine_columns(count_ss1, 'TY_y1', 'TY3_y', 'TY_y')
    count_ss1 = combine_columns(count_ss1, 'TY_x', 'TY_y', 'TY')
    count_ss2 = combine_columns(count_ss2, 'TY1_x', 'TY2_x', 'TY_x1')
    count_ss2 = combine_columns(count_ss2, 'TY_x1', 'TY3_x', 'TY_x')
    count_ss2 = combine_columns(count_ss2, 'TY1_y', 'TY2_y', 'TY_y1')
    count_ss2 = combine_columns(count_ss2, 'TY_y1', 'TY3_y', 'TY_y')
    count_ss2 = combine_columns(count_ss2, 'TY_x', 'TY_y', 'TY')
    

    
    count_ss1 = pd.merge(count_ss1, ss_loc, on='권역')
    count_ss2 = pd.merge(count_ss2, ss_locp, on='지역')
    
    count_ss1['지역'] = np.nan
    count_ss2 = count_ss2.drop('권역_y', axis=1)
    count_ss2 = count_ss2.rename(columns={'권역_x':'권역'})
    SS_new_order1 = ['권역', '지역', '지수count', 'WW','TY','SS','SR','WW&SRcount','WW&SScount','TY&SRcount','TY&SScount','횟수']
    count_ss3 = pd.concat([count_ss1, count_ss2], ignore_index=True)
    count_ss3 = count_ss3.reindex(columns=SS_new_order1)
    
    count_ss3['권역'] = pd.Categorical(count_ss3['권역'], ordered=True)
    count_ss3 = count_ss3.sort_values(['권역','지역']).reset_index(drop=True)
    
    # 권역 열의 맨 아래에 총합 위치
    count_ss3.loc[result['지역'] == '총합', '권역'] = np.nan
    count_ss3 = count_ss3.fillna('A')
    
    ss_row_sum = count_ss1["횟수"].sum()
    
    print()
    print('SS 총통계')
    ss_sum_all = count_ss1.sum()
    ss_sum_all = pd.DataFrame(ss_sum_all, columns=['변경'])
    ss_sum_all = ss_sum_all.drop('권역', axis=0)
    ss_sum_all = ss_sum_all.rename(index={'횟수': '총예보지수변경'})
    print(ss_sum_all)
    ss_sum_all.to_csv('스킨스쿠버2_요약_특보.csv', encoding='euc-kr', index=True)
    
    def calculate_percentages(df, row_sum):
        df['WW%'] = round(df['WW'] / row_sum * 100, 2)
        df['TY%'] = round(df['TY'] / row_sum * 100, 2)
        df['SS%'] = round(df['SS'] / row_sum * 100, 2)
        df['SR%'] = round(df['SR'] / row_sum * 100, 2)
        df['횟수%'] = round(df['횟수'] / row_sum * 100, 2)
        df['WW&SR%'] = round(df['WW&SRcount'] / row_sum * 100, 1)
        df['WW&SS%'] = round(df['WW&SScount'] / row_sum * 100, 1)
        df['TY&SR%'] = round(df['TY&SRcount'] / row_sum * 100, 1)
        df['TY&SS%'] = round(df['TY&SScount'] / row_sum * 100, 1)
        return df
    
    def calculate_percentages1(df, row_sum):
        df['WW%'] = round(df['WW'] / row_sum['총 예보건수'] * 100, 2)
        df['TY%'] = round(df['TY'] / row_sum['총 예보건수'] * 100, 2)
        df['SS%'] = round(df['SS'] / row_sum['총 예보건수'] * 100, 2)
        df['SR%'] = round(df['SR'] / row_sum['총 예보건수'] * 100, 2)
        df['횟수%'] = round(df['횟수'] / row_sum['총 예보건수'] * 100, 2)
        df['WW&SR%'] = round(df['WW&SRcount'] / row_sum['총 예보건수'] * 100, 2)
        df['WW&SS%'] = round(df['WW&SScount'] / row_sum['총 예보건수'] * 100, 2)
        df['TY&SR%'] = round(df['TY&SRcount'] / row_sum['총 예보건수'] * 100, 2)
        df['TY&SS%'] = round(df['TY&SScount'] / row_sum['총 예보건수'] * 100, 2)
        return df
    
    def calculate_percentages2(df):
        df['WW%'] = df['WW%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['TY%'] = df['TY%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['SS%'] = df['SS%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['SR%'] = df['SR%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['횟수%'] = df['횟수%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['WW&SR%'] = df['WW&SR%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['WW&SS%'] = df['WW&SS%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['TY&SR%'] = df['TY&SR%'].apply(lambda x: "{:.1f}".format(float(x)))
        df['TY&SS%'] = df['TY&SS%'].apply(lambda x: "{:.1f}".format(float(x)))  
        return df
    
    count_ss3 = pd.merge(SS_loc_row, count_ss3, on=['권역','지역'], how= 'inner')
    
    count_ss1 = calculate_percentages(count_ss1, ss_row_sum)
    count_ss2 = calculate_percentages(count_ss2, ss_row_sum)
    count_ss3 = calculate_percentages1(count_ss3, count_ss3)
    count_ss1 = calculate_percentages2(count_ss1)
    count_ss2 = calculate_percentages2(count_ss2)
    count_ss3 = calculate_percentages2(count_ss3)
    
    count_ss3.replace('A', np.nan, inplace=True)
    
    
    SS_new_order = ['권역', '횟수','횟수%','TY','TY%','WW','WW%','SS','SS%','SR','SR%','WW&SRcount','WW&SR%','WW&SScount','WW&SS%','TY&SRcount','TY&SR%','TY&SScount','TY&SS%']
    count_ss1 = count_ss1.reindex(columns=SS_new_order)
    SS_new_order2 = ['권역', '지역','횟수','횟수%','TY','TY%','WW','WW%','SS','SS%','SR','SR%','WW&SRcount','WW&SR%','WW&SScount','WW&SS%','TY&SRcount','TY&SR%','TY&SScount','TY&SS%']
    count_ss2 = count_ss2.reindex(columns=SS_new_order2)
    SS_new_order5 = ['권역', '지역', '총 예보건수','횟수','횟수%','TY','TY%','WW','WW%','SS','SS%','SR','SR%','WW&SRcount','WW&SR%','WW&SScount','WW&SS%','TY&SRcount','TY&SR%','TY&SScount','TY&SS%']
    count_ss3 = count_ss3.reindex(columns=SS_new_order5)
    
    # 권역열 안의 요소들을 서해, 남해, 동해 순으로 배열
    SS_new_order3 = ['황해중부', '황해남부', '남해서부', '남해동부', '제주도', '동해남부', '동해중부']
    count_ss1['권역'] = pd.Categorical(count_ss1['권역'], categories=SS_new_order3, ordered=True)
    count_ss1 = count_ss1.sort_values('권역').reset_index(drop=True)
    count_ss2['권역'] = pd.Categorical(count_ss2['권역'], categories=SS_new_order3, ordered=True)
    count_ss2 = count_ss2.sort_values(['권역','지역']).reset_index(drop=True)
    count_ss3['권역'] = pd.Categorical(count_ss3['권역'], categories=SS_new_order3, ordered=True)
    count_ss3 = count_ss3.sort_values(['권역','지역']).reset_index(drop=True)
    
    
    count_ss3.to_excel('스킨스쿠버3_지역_특보.xlsx', encoding='euc-kr', float_format='%.1f', index=False)
