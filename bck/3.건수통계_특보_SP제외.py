# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 18:48:01 2023

@author: sang
"""


'''
mod=서비스
org=예측
'''
import pandas as pd
import numpy as np
'''
# 갈라짐
file_path = r'C:\2023\python test\지역별통계내기\2211\sdmod.xlsx'
file_path2 = r'C:\2023\python test\지역별통계내기\2211\sdorg.xlsx'
sdm = pd.read_excel(file_path)
sdo = pd.read_excel(file_path2)

SD_row = sdm.shape[0]

sdo['해상특보']=''
sdo['육상특보']=''
sdo['특보점수']=''

sdm1 = sdm[["생산일","권역","지역","기온점수","풍속점수","날씨점수","해상특보","육상특보","특보점수","예보지수"]]
sdo1 = sdo[["생산일","권역","지역","기온점수","풍속점수","날씨점수","해상특보","육상특보","특보점수","예보지수"]]

compare = sdm1['예보지수'] == sdo1['예보지수']
csdm = sdm1[~compare]
csdo = sdo1[~compare]

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

def highlight_special_W(row):
    if row.name == '해상특보':
        return ['background-color: green' if x != '-' else '' for x in row]
    else:
        return [''] * len(row)

# 열 비교하여 값이 다른 경우 해당 셀 색칠
sd_html = sd_result.style.apply(highlight_diff, color='yellow', axis=1, subset=['기온점수m', '기온점수o']) \
              .apply(highlight_diff, color='blue', axis=1, subset=['풍속점수m', '풍속점수o']) \
              .apply(highlight_diff, color='red', axis=1, subset=['날씨점수m', '날씨점수o']) \
              .apply(lambda x: highlight_special_R(x), axis=0) \
              .apply(lambda x: highlight_special_W(x), axis=0) \
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
def count_changes_SD(df, groupby_col, warn_col='해상특보', rain_col='강수량'):
    count = df.groupby(groupby_col).apply(lambda x: pd.Series({'기온점수count': (x['기온점수m'] != x['기온점수o']).sum(),
                                                                  '풍속점수count': (x['풍속점수m'] != x['풍속점수o']).sum(),
                                                                  '날씨점수count': (x['날씨점수m'] != x['날씨점수o']).sum()})).reset_index()
    warn = df[df[warn_col] != '-'].groupby(groupby_col + [warn_col]).size().reset_index(name=warn_col+'count')
    pivot = warn.pivot_table(index=groupby_col, columns=warn_col, values=warn_col+'count', fill_value=0).reset_index()
    count = count.merge(pivot, on=groupby_col, how='left').fillna(0)
    rain = df[df[rain_col].astype(int) > 0].groupby(groupby_col + [rain_col]).size().reset_index(name=rain_col+'count')
    count = count.merge(rain, on=groupby_col, how='left').fillna(0)
    return count

count2_sd1 = count_changes_SD(sd_result, ['권역'])
count2_sd2 = count_changes_SD(sd_result, ['권역', '지역'])

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

count2_sd1 = combine_columns(count2_sd1, 'WW2', 'WW3', 'WW')
count2_sd2 = combine_columns(count2_sd2, 'WW2', 'WW3', 'WW')
count2_sd1 = combine_columns(count2_sd1, 'TY2', 'TY3', 'TY')
count2_sd2 = combine_columns(count2_sd2, 'TY2', 'TY3', 'TY')

count2_sd1 = pd.merge(count2_sd1, sd_loc, on='권역')
count2_sd2 = pd.merge(count2_sd2, sd_locp, on='지역')

sd_row_sum = count2_sd2["횟수"].sum()

print('SD 총통계')
sd_sum_all = count2_sd1.sum()
sd_sum_all = pd.DataFrame(sd_sum_all, columns=['변경'])
sd_sum_all = sd_sum_all.drop('권역', axis=0)
sd_sum_all = sd_sum_all.rename(index={'횟수': '총예보지수변경'})
print(sd_sum_all)
sd_sum_all.to_csv('갈라짐_요약.csv', encoding='euc-kr', index=True)

def calculate_percentages(df, row_sum):
    df['기온%'] = round(df['기온점수count'] / row_sum * 100, 1)
    df['풍속%'] = round(df['풍속점수count'] / row_sum * 100, 1)
    df['날씨%'] = round(df['날씨점수count'] / row_sum * 100, 1)
    df['강수량%'] = round(df['강수량count'] / row_sum * 100, 1)
    df['WW%'] = round(df['WW'] / row_sum * 100, 1)
    df['TY%'] = round(df['TY'] / row_sum * 100, 1)
    df['횟수%'] = round(df['횟수'] / row_sum * 100, 1)
    return df

count2_sd1 = calculate_percentages(count2_sd1, sd_row_sum)
count2_sd2 = calculate_percentages(count2_sd2, sd_row_sum)

count2_sd2 = count2_sd2.drop('권역_y', axis=1)
count2_sd2 = count2_sd2.rename(columns={'권역_x':'권역'})

SD_new_order = ['권역', '횟수','횟수%', '강수량count','강수량%','TY','TY%']
count2_sd1 = count2_sd1.reindex(columns=SD_new_order)
SD_new_order2 = ['권역', '지역','횟수','횟수%', '강수량count','강수량%','TY','TY%']
count2_sd2 = count2_sd2.reindex(columns=SD_new_order2)

# 구분열 안의 요소들을 서해, 남해, 동해 순으로 배열
SD_new_order3 = ['황해중부', '황해남부', '제주도','남해서부','남해동부','동해남부','동해중부']
count2_sd1['권역'] = pd.Categorical(count2_sd1['권역'], categories=SD_new_order3, ordered=True)
count2_sd1 = count2_sd1.sort_values('권역').reset_index(drop=True)
count2_sd2['권역'] = pd.Categorical(count2_sd2['권역'], categories=SD_new_order3, ordered=True)
count2_sd2 = count2_sd2.sort_values('권역').reset_index(drop=True)

count2_sd1.to_csv('갈라짐_권역_사유.csv', encoding='euc-kr', index=False)
count2_sd2.to_csv('갈라짐_지역_사유.csv', encoding='euc-kr', index=False)
'''
##################################################################
##################################################################
##################################################################
##################################################################

#바다낚시
file_path3 = r'C:\Users\sang\Desktop\통계요약본\2310\sfmod.xlsx'
file_path4 = r'C:\Users\sang\Desktop\통계요약본\2310\sforg.xlsx'
sfm = pd.read_excel(file_path3)
sfo = pd.read_excel(file_path4)

# 행의 갯수
SF_row = sfm.shape[0]


# 같은 요소의 개수와 같은 권역의 개수를 세는 작업
grouped = sfm.groupby(['권역', '지역']).size().reset_index(name='총 예보건수')

# 권역 요소별 총합 계산
grouped_sum = grouped.groupby('권역')['총 예보건수'].sum().reset_index(name='총 예보건수')


# 권역 요소 아래에 총합 행 추가
#result = pd.concat([grouped, grouped_sum.assign(지역='총합')])
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

#print(type(sfo1['특보점수']))

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
with open('바다낚시_특보.html', 'w') as f:
    f.write(sf_html.to_html())

# 스타일이 적용된 데이터프레임을 xlsx 파일로 저장
sf_html.to_excel('바다낚시_특보.xlsx', index=True)

#각 권역의 갯수, 각 지역의 갯수, 각 변경요인 갯수
sf_loc = sf_result['권역'].value_counts().sort_index().to_frame(name='횟수').reset_index().rename(columns={'index': '권역'})
sf_locp = sf_result.groupby(['권역', '지역'])['지역'].count().reset_index(name='횟수')

#각 권역의 각각의 변경요인 갯수
#각 지역의 각각의 변경요인 갯수
def count_changes_SF(df, groupby_col, sea_warn_col='해상특보', land_warn_col='육상특보'):
    count = df.groupby(groupby_col).apply(lambda x: pd.Series({'지수count': (x['예보지수m'] != x['예보지수o']).sum()})).reset_index()
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
count_sf1 = combine_columns(count_sf1, 'SS2', 'SS3', 'SS')
count_sf2 = combine_columns(count_sf2, 'SS2', 'SS3', 'SS')

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
SF_new_order1 = ['권역', '지역','지수count','WW','TY','SS','SR','횟수']
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
sf_sum_all.to_csv('바다낚시_요약_특보.csv', encoding='euc-kr', index=True)

def calculate_percentages(df, row_sum):
    df['WW%'] = round(df['WW'] / row_sum * 100, 1)
    df['TY%'] = round(df['TY'] / row_sum * 100, 1)
    df['SS%'] = round(df['SS'] / row_sum * 100, 2)
    df['SR%'] = round(df['SR'] / row_sum * 100, 2)
    df['횟수%'] = round(df['횟수'] / row_sum * 100, 1)
    return df

def calculate_percentages1(df, row_sum):
    df['WW%'] = round(df['WW'] / row_sum['총 예보건수'] * 100, 1)
    df['TY%'] = round(df['TY'] / row_sum['총 예보건수'] * 100, 1)
    df['SS%'] = round(df['SS'] / row_sum['총 예보건수'] * 100, 2)
    df['SR%'] = round(df['SR'] / row_sum['총 예보건수'] * 100, 2)
    df['횟수%'] = round(df['횟수'] / row_sum['총 예보건수'] * 100, 1)
    return df

def calculate_percentages2(df):
    df['WW%'] = df['WW%'].apply(lambda x: "{:.1f}".format(float(x)))
    df['TY%'] = df['TY%'].apply(lambda x: "{:.1f}".format(float(x)))
    df['SS%'] = df['SS%'].apply(lambda x: "{:.1f}".format(float(x)))
    df['SR%'] = df['SR%'].apply(lambda x: "{:.1f}".format(float(x)))
    df['횟수%'] = df['횟수%'].apply(lambda x: "{:.1f}".format(float(x)))
    return df 

count_sf3 = pd.merge(SF_loc_row, count_sf3, on=['권역','지역'], how= 'inner')

count_sf1 = calculate_percentages(count_sf1, sf_row_sum)
count_sf2 = calculate_percentages(count_sf2, sf_row_sum)
count_sf3 = calculate_percentages1(count_sf3, count_sf3)
count_sf1 = calculate_percentages2(count_sf1)
count_sf2 = calculate_percentages2(count_sf2)
count_sf3 = calculate_percentages2(count_sf3)

count_sf3.replace('A', np.nan, inplace=True)

#count_sf2 = count_sf2.drop('권역_y', axis=1)
#count_sf2 = count_sf2.rename(columns={'권역_x':'권역'})

SF_new_order = ['권역', '횟수','횟수%','TY','TY%','WW','WW%','SS','SS%','SR','SR%']
count_sf1 = count_sf1.reindex(columns=SF_new_order)
SF_new_order2 = ['권역', '지역','횟수','횟수%','TY','TY%','WW','WW%','SS','SS%','SR','SR%']
count_sf2 = count_sf2.reindex(columns=SF_new_order2)
SF_new_order5 = ['권역', '지역', '총 예보건수', '횟수','횟수%','TY','TY%','WW','WW%','SS','SS%','SR','SR%']
count_sf3 = count_sf3.reindex(columns=SF_new_order5)

# 구분열 안의 요소들을 서해, 남해, 동해 순으로 배열
SF_new_order3 = ['황해중부', '황해남부', '제주도','남해서부','남해동부','동해남부','동해중부']
count_sf1['권역'] = pd.Categorical(count_sf1['권역'], categories=SF_new_order3, ordered=True)
count_sf1 = count_sf1.sort_values('권역').reset_index(drop=True)
count_sf2['권역'] = pd.Categorical(count_sf2['권역'], categories=SF_new_order3, ordered=True)
count_sf2 = count_sf2.sort_values(['권역','지역']).reset_index(drop=True)
count_sf3['권역'] = pd.Categorical(count_sf3['권역'], categories=SF_new_order3, ordered=True)
count_sf3 = count_sf3.sort_values(['권역','지역']).reset_index(drop=True)

#count_sf1.to_csv('바다낚시_권역_특보.csv', encoding='euc-kr', index=False)
#count_sf2.to_csv('바다낚시_지역_특보.csv', encoding='euc-kr', index=False)
#count_sf1.to_excel('바다낚시_권역_특보.xlsx', encoding='euc-kr', float_format='%.1f', index=False)
#count_sf2.to_excel('바다낚시_지역_특보.xlsx', encoding='euc-kr', float_format='%.1f', index=False)
count_sf3.to_excel('바다낚시_지역_특보.xlsx', encoding='euc-kr', float_format='%.1f', index=False)

##################################################################
##################################################################
##################################################################
##################################################################

#뱃멀미
file_path5 = r'C:\Users\sang\Desktop\통계요약본\2310\skmod.xlsx'
file_path6 = r'C:\Users\sang\Desktop\통계요약본\2310\skorg.xlsx'
skm = pd.read_excel(file_path5)
sko = pd.read_excel(file_path6)

# 행의 갯수
SK_row = skm.shape[0]

# 같은 요소의 개수와 같은 권역의 개수를 세는 작업
grouped = skm.groupby(['항로명', '선박명']).size().reset_index(name='총 예보건수')

# 권역 요소별 총합 계산
grouped_sum = grouped.groupby('항로명')['총 예보건수'].sum().reset_index(name='총 예보건수')


# 권역 요소 아래에 총합 행 추가
#result = pd.concat([grouped, grouped_sum.assign(지역='총합')])
result = pd.concat([grouped, grouped_sum])

#SF_new_order3 = ['황해중부', '황해남부', '제주도','남해서부','남해동부','동해남부','동해중부']
#result['권역'] = pd.Categorical(result['권역'], categories=SF_new_order3, ordered=True)
result['항로명'] = pd.Categorical(result['항로명'], ordered=True)
result = result.sort_values(['항로명','선박명']).reset_index(drop=True)

# 권역 열의 맨 아래에 총합 위치
result.loc[result['선박명'] == '총합', '항로명'] = np.nan
result = result.fillna('A')
SK_loc_row = result



#sko['해상특보']=''
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
with open('뱃멀미_특보.html', 'w') as f:
    f.write(sk_html.to_html())

# 스타일이 적용된 데이터프레임을 xlsx 파일로 저장
sk_html.to_excel('뱃멀미_특보.xlsx', index=True)

#각 권역의 갯수, 각 지역의 갯수, 각 변경요인 갯수
sk_loc = sk_result['항로명'].value_counts().sort_index().to_frame(name='횟수').reset_index().rename(columns={'index': '항로명'})
sk_locp = sk_result.groupby(['항로명', '선박명'])['선박명'].count().reset_index(name='횟수')

#각 권역의 각각의 변경요인 갯수
#각 지역의 각각의 변경요인 갯수
def count_changes_SK(df, groupby_col, warn_col='특보'):
    count = df.groupby(groupby_col).apply(lambda x: pd.Series({'지수count': (x['예보지수m'] != x['예보지수o']).sum()})).reset_index()
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

count_sk1 = combine_columns(count_sk1, 'TY2', 'TY3', 'TY')
count_sk2 = combine_columns(count_sk2, 'TY2', 'TY3', 'TY')



count_sk1 = pd.merge(count_sk1, sk_loc, on='항로명')
count_sk2 = pd.merge(count_sk2, sk_locp, on='선박명')

count_sk1['선박명'] = np.nan
count_sk2 = count_sk2.drop('항로명_y', axis=1)
count_sk2 = count_sk2.rename(columns={'항로명_x':'항로명'})
SK_new_order1 = ['항로명', '선박명','지수count', 'WW','TY','횟수']
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
sk_sum_all.to_csv('뱃멀미_요약_특보.csv', encoding='euc-kr', index=True)

def calculate_percentages(df, row_sum):
    df['WW%'] = round(df['WW'] / row_sum * 100, 2)
    df['TY%'] = round(df['TY'] / row_sum * 100, 2)
    df['횟수%'] = round(df['횟수'] / row_sum * 100, 2)
    return df

def calculate_percentages1(df, row_sum):
    df['WW%'] = round(df['WW'] / row_sum['총 예보건수'] * 100, 2)
    df['TY%'] = round(df['TY'] / row_sum['총 예보건수'] * 100, 2)
    df['횟수%'] = round(df['횟수'] / row_sum['총 예보건수'] * 100, 2)
    return df

def calculate_percentages2(df):
    df['WW%'] = df['WW%'].apply(lambda x: "{:.1f}".format(float(x)))
    df['TY%'] = df['TY%'].apply(lambda x: "{:.1f}".format(float(x)))
    df['횟수%'] = df['횟수%'].apply(lambda x: "{:.1f}".format(float(x)))
    return df

count_sk3 = pd.merge(SK_loc_row, count_sk3, on=['항로명','선박명'], how= 'inner')

count_sk1 = calculate_percentages(count_sk1, sk_row_sum)
count_sk2 = calculate_percentages(count_sk2, sk_row_sum)
count_sk3 = calculate_percentages1(count_sk3, count_sk3)
count_sk1 = calculate_percentages2(count_sk1)
count_sk2 = calculate_percentages2(count_sk2)
count_sk3 = calculate_percentages2(count_sk3)

count_sk3.replace('A', np.nan, inplace=True)

#count_sk2 = count_sk2.drop('항로명_y', axis=1)
#count_sk2 = count_sk2.rename(columns={'항로명_x':'항로명'})

SK_new_order = ['항로명', '횟수','횟수%','TY','TY%','WW','WW%']
count_sk1 = count_sk1.reindex(columns=SK_new_order)
SK_new_order2 = ['항로명', '선박명','횟수','횟수%','TY','TY%','WW','WW%']
count_sk2 = count_sk2.reindex(columns=SK_new_order2)
SK_new_order5 = ['항로명', '선박명', '총 예보건수', '횟수','횟수%','TY','TY%','WW','WW%']
count_sk3 = count_sk3.reindex(columns=SK_new_order5)

#count_sk1.to_csv('뱃멀미_항로_특보.csv', encoding='euc-kr', index=False)
#count_sk2.to_csv('뱃멀미_선박_특보.csv', encoding='euc-kr', index=False)
#count_sk1.to_excel('뱃멀미_항로_특보.xlsx', encoding='euc-kr', float_format='%.1f', index=False)
#count_sk2.to_excel('뱃멀미_선박_특보.xlsx', encoding='euc-kr', float_format='%.1f', index=False)
count_sk3.to_excel('뱃멀미_선박_특보.xlsx', encoding='euc-kr', float_format='%.1f', index=False)

##################################################################
##################################################################
##################################################################
##################################################################

# 서핑
file_path7 = r'C:\Users\sang\Desktop\통계요약본\2310\srmod.xlsx'
file_path8 = r'C:\Users\sang\Desktop\통계요약본\2310\srorg.xlsx'
srm = pd.read_excel(file_path7)
sro = pd.read_excel(file_path8)

# 행의 갯수
SR_row = srm.shape[0]

# 같은 요소의 개수와 같은 권역의 개수를 세는 작업
grouped = srm.groupby(['구분', '지역']).size().reset_index(name='총 예보건수')

# 권역 요소별 총합 계산
grouped_sum = grouped.groupby('구분')['총 예보건수'].sum().reset_index(name='총 예보건수')


# 권역 요소 아래에 총합 행 추가
#result = pd.concat([grouped, grouped_sum.assign(지역='총합')])
result = pd.concat([grouped, grouped_sum])

SR_new_order3 = ['황해중부', '제주도', '남해동부','동해남부','동해중부']
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
with open('서핑_특보.html', 'w') as f:
    f.write(sr_html.to_html())

# 스타일이 적용된 데이터프레임을 xlsx 파일로 저장
sr_html.to_excel('서핑_특보.xlsx', index=True)

#각 권역의 갯수, 각 지역의 갯수, 각 변경요인 갯수
sr_loc = sr_result['구분'].value_counts().sort_index().to_frame(name='횟수').reset_index().rename(columns={'index': '구분'})
sr_locp = sr_result.groupby(['구분', '지역'])['지역'].count().reset_index(name='횟수')

#각 권역의 각각의 변경요인 갯수
#각 지역의 각각의 변경요인 갯수
def count_changes_SR(df, groupby_col, sea_warn_col='해상특보', land_warn_col='육상특보'):
    count = df.groupby(groupby_col).apply(lambda x: pd.Series({'지수count': (x['예보지수m'] != x['예보지수o']).sum()})).reset_index()
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

count_sr1 = combine_columns(count_sr1, 'WW2', 'WW3', 'WW')
count_sr2 = combine_columns(count_sr2, 'WW2', 'WW3', 'WW')
count_sr1 = combine_columns(count_sr1, 'SR2', 'SR3', 'SR_1')
count_sr2 = combine_columns(count_sr2, 'SR2', 'SR3', 'SR_1')

count_sr1 = combine_columns(count_sr1, 'SR_1', 'SR1', 'SR')
count_sr2 = combine_columns(count_sr2, 'SR_1', 'SR1', 'SR')

count_sr1 = combine_columns(count_sr1, 'SS2', 'SS3', 'SS')
count_sr2 = combine_columns(count_sr2, 'SS2', 'SS3', 'SS')

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
SR_new_order1 = ['구분', '지역', '지수count', 'WW','TY','SS','SR','횟수']
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
sr_sum_all.to_csv('서핑_요약_특보.csv', encoding='euc-kr', index=True)

def calculate_percentages(df, row_sum):
    df['WW%'] = round(df['WW'] / row_sum * 100, 2)
    df['TY%'] = round(df['TY'] / row_sum * 100, 2)
    df['SS%'] = round(df['SS'] / row_sum * 100, 2)
    df['SR%'] = round(df['SR'] / row_sum * 100, 2)
    df['횟수%'] = round(df['횟수'] / row_sum * 100, 2)
    return df

def calculate_percentages1(df, row_sum):
    df['WW%'] = round(df['WW'] / row_sum['총 예보건수'] * 100, 2)
    df['TY%'] = round(df['TY'] / row_sum['총 예보건수'] * 100, 2)
    df['SS%'] = round(df['SS'] / row_sum['총 예보건수'] * 100, 2)
    df['SR%'] = round(df['SR'] / row_sum['총 예보건수'] * 100, 2)
    df['횟수%'] = round(df['횟수'] / row_sum['총 예보건수'] * 100, 2)
    return df

def calculate_percentages2(df):
    df['WW%'] = df['WW%'].apply(lambda x: "{:.1f}".format(float(x)))
    df['TY%'] = df['TY%'].apply(lambda x: "{:.1f}".format(float(x)))
    df['SS%'] = df['SS%'].apply(lambda x: "{:.1f}".format(float(x)))
    df['SR%'] = df['SR%'].apply(lambda x: "{:.1f}".format(float(x)))
    df['횟수%'] = df['횟수%'].apply(lambda x: "{:.1f}".format(float(x)))
    return df

count_sr3 = pd.merge(SR_loc_row, count_sr3, on=['구분','지역'], how= 'inner')

count_sr1 = calculate_percentages(count_sr1, sr_row_sum)
count_sr2 = calculate_percentages(count_sr2, sr_row_sum)
count_sr3 = calculate_percentages1(count_sr3, count_sr3)
count_sr1 = calculate_percentages2(count_sr1)
count_sr2 = calculate_percentages2(count_sr2)
count_sr3 = calculate_percentages2(count_sr3)

count_sr3.replace('A', np.nan, inplace=True)

#count_sr2 = count_sr2.drop('구분_y', axis=1)
#count_sr2 = count_sr2.rename(columns={'구분_x':'구분'})

SR_new_order = ['구분', '횟수','횟수%','TY','TY%','WW','WW%','SS','SS%','SR','SR%']
count_sr1 = count_sr1.reindex(columns=SR_new_order)
SR_new_order2 = ['구분', '지역','횟수','횟수%','TY','TY%','WW','WW%','SS','SS%','SR','SR%']
count_sr2 = count_sr2.reindex(columns=SR_new_order2)
SR_new_order5 = ['구분', '지역', '총 예보건수','횟수','횟수%','TY','TY%','WW','WW%','SS','SS%','SR','SR%']
count_sr3 = count_sr3.reindex(columns=SR_new_order5)

# 구분열 안의 요소들을 서해, 남해, 동해 순으로 배열
SR_new_order3 = ['황해중부', '제주도', '남해동부','동해남부','동해중부']
count_sr1['구분'] = pd.Categorical(count_sr1['구분'], categories=SR_new_order3, ordered=True)
count_sr1 = count_sr1.sort_values('구분').reset_index(drop=True)
count_sr2['구분'] = pd.Categorical(count_sr2['구분'], categories=SR_new_order3, ordered=True)
count_sr2 = count_sr2.sort_values(['구분','지역']).reset_index(drop=True)
count_sr3['구분'] = pd.Categorical(count_sr3['구분'], categories=SR_new_order3, ordered=True)
count_sr3 = count_sr3.sort_values(['구분','지역']).reset_index(drop=True)

#print(count_sr2)
#count_sr1.to_csv('서핑_구분_특보.csv', encoding='euc-kr', index=False)
#count_sr2.to_csv('서핑_지역_특보.csv', encoding='euc-kr', index=False)
#count_sr1.to_excel('서핑_구분_특보.xlsx', encoding='euc-kr', float_format='%.1f', index=False)
#count_sr2.to_excel('서핑_지역_특보.xlsx', encoding='euc-kr', float_format='%.1f', index=False)
count_sr3.to_excel('서핑_지역_특보.xlsx', encoding='euc-kr', float_format='%.1f', index=False)


##################################################################
##################################################################
##################################################################
##################################################################

# #해수욕
# file_path9 = r'C:\Users\sang\Desktop\통계요약본\2310\spmod.xlsx'
# file_path10 = r'C:\Users\sang\Desktop\통계요약본\2310\sporg.xlsx'
# spm = pd.read_excel(file_path9)
# spo = pd.read_excel(file_path10)

# SP_row = spm.shape[0]

# # 같은 요소의 개수와 같은 권역의 개수를 세는 작업
# grouped = spm.groupby(['권역', '해수욕장']).size().reset_index(name='총 예보건수')

# # 권역 요소별 총합 계산
# grouped_sum = grouped.groupby('권역')['총 예보건수'].sum().reset_index(name='총 예보건수')


# # 권역 요소 아래에 총합 행 추가
# #result = pd.concat([grouped, grouped_sum.assign(지역='총합')])
# result = pd.concat([grouped, grouped_sum])

# SP_new_order3 = ['황해중부', '황해남부', '남해서부','남해동부', '제주도', '동해남부', '동해중부']
# result['권역'] = pd.Categorical(result['권역'], categories=SP_new_order3, ordered=True)
# result = result.sort_values(['권역','해수욕장']).reset_index(drop=True)

# # 권역 열의 맨 아래에 총합 위치
# result.loc[result['해수욕장'] == '총합', '권역'] = np.nan
# result = result.fillna('A')
# SP_loc_row = result


# spo['해상특보']=''
# spo['육상특보']=''
# spo['특보점수']=''
# spo['강수량점수']=''

# spm1 = spm[["생산일","권역","해수욕장","해상특보","육상특보","특보점수","강수량점수","예보지수"]]
# spo1 = spo[["생산일","권역","해수욕장","해상특보","육상특보","특보점수","강수량점수","예보지수"]]

# spo1['특보점수'] = 100
# spo1['강수량점수'] = 100

# compare = spm1['예보지수'] == spo1['예보지수']
# cspm1 = spm1[~compare]
# cspo1 = spo1[~compare]

# compare = (cspm1['특보점수'] != cspo1['특보점수']) | (cspm1['강수량점수'] != cspo1['강수량점수'])
# #compare = (cspm1['강수량점수'] == cspo1['강수량점수'])
# #compare = (cspm1['특보점수'] == cspo1['특보점수'])
# cspm = cspm1[compare]
# cspo = cspo1[compare]


# cspm_c = cspm.copy()

# #cspm_c['강수량']=spm["강수량"]
# cspm_c['강수량점수']=spm["강수량점수"]

# cspm_c = cspm_c.sort_values(by=['권역','해수욕장'], ascending=[True, True])
# cspo = cspo.sort_values(by=['권역','해수욕장'], ascending=[True, True])


# cspm_c.rename(columns={'예보지수':'예보지수m'},inplace=True)
# cspo.rename(columns={'예보지수':'예보지수o'},inplace=True)

# sp_result = pd.concat([cspm_c,cspo],axis=1)

# # 중복된 열을 제거하여 유일한 값을 가지도록 만듦
# sp_result = sp_result.loc[:, ~sp_result.columns.duplicated(keep='first')]

# # 컬럼 순서 변경
# sp_result = sp_result[['생산일', '권역', '해수욕장', '강수량점수','해상특보','육상특보','특보점수','예보지수m','예보지수o']]
# sp_result = sp_result.reset_index(drop=True)
# sp_result.index = sp_result.index + 1

# # 셀 색칠 함수
# def highlight_diff(x, color):
#     style = 'background-color: {}'.format(color)
#     if x[0] != x[1]:
#         return [style, style]
#     else:
#         return ['', '']

# def highlight_special_R(row):
#     if row.name == '강수량점수':
#         return ['background-color: orange' if x != 100 else '' for x in row]
#     else:
#         return [''] * len(row)

# def highlight_special_sea(row):
#     if row.name == '해상특보':
#         return ['background-color: green' if x != '-' else '' for x in row]
#     else:
#         return [''] * len(row)
# def highlight_special_land(row):
#     if row.name == '육상특보':
#         return ['background-color: cyan' if x != '-' else '' for x in row]
#     else:
#         return [''] * len(row) 

# # 열 비교하여 값이 다른 경우 해당 셀 색칠
# sp_html = sp_result.style.apply(lambda x: highlight_special_R(x), axis=0) \
#               .apply(lambda x: highlight_special_sea(x), axis=0) \
#               .apply(lambda x: highlight_special_land(x), axis=0) \
#               .set_properties(**{'border': '1px solid black'})

# # 스타일이 적용된 데이터프레임을 HTML 파일로 저장
# with open('해수욕_특보.html', 'w') as f:
#     f.write(sp_html.to_html())
    
# # 스타일이 적용된 데이터프레임을 xlsx 파일로 저장
# sp_html.to_excel('해수욕_특보.xlsx', index=True)

# #각 권역의 갯수, 각 지역의 갯수, 각 변경요인 갯수
# sp_loc = sp_result['권역'].value_counts().sort_index().to_frame(name='횟수').reset_index().rename(columns={'index': '권역'})
# sp_locp = sp_result.groupby(['권역', '해수욕장'])['해수욕장'].count().reset_index(name='횟수')

# #각 권역의 각각의 변경요인 갯수
# #각 지역의 각각의 변경요인 갯수
# def count_changes_sp1(df, groupby_col, sea_warn_col='해상특보', land_warn_col='육상특보', rain_col='강수량점수'):
#     count = df.groupby(groupby_col).apply(lambda x: pd.Series({'태풍&강수count': ((x[sea_warn_col].isin(['TY2', 'TY3'])) & (x[rain_col] != 100)).sum(),
#                                                                   '풍랑&강수count': ((x[sea_warn_col].isin(['WW2', 'WW3'])) & (x[rain_col] != 100)).sum(),
#                                                                   '호우&강수count': ((x[land_warn_col].isin(['SR2', 'SR3'])) & (x[rain_col] != 100)).sum(),
#                                                                   '폭풍해일&강수count': ((x[land_warn_col].isin(['SS2', 'SS3'])) & (x[rain_col] != 100)).sum(),})).reset_index()
#     # 해상 특보와 육상 특보에 대한 필터링 및 경고 횟수 계산
#     sea_warn = df[df[sea_warn_col] != '-'].groupby(groupby_col + [sea_warn_col]).size().reset_index(name=sea_warn_col+'count')
#     land_warn = df[df[land_warn_col].isin(['SR2', 'SR3', 'SS2', 'SS3'])].groupby(groupby_col + [land_warn_col]).size().reset_index(name=land_warn_col+'count')
#     # 피벗 테이블 생성
#     sea_pivot = sea_warn.pivot_table(index=groupby_col, columns=sea_warn_col, values=sea_warn_col+'count', fill_value=0).reset_index()
#     land_pivot = land_warn.pivot_table(index=groupby_col, columns=land_warn_col, values=land_warn_col+'count', fill_value=0).reset_index()
#     # 경고 횟수 데이터를 count DataFrame에 추가
#     count = count.merge(sea_pivot, on=groupby_col, how='left').fillna(0)
#     count = count.merge(land_pivot, on=groupby_col, how='left').fillna(0)
    
#     rain = df[df[rain_col] != 100].groupby(groupby_col + [rain_col]).size().reset_index(name=rain_col+'count')
#     rain_pivot = rain.pivot_table(index=groupby_col, columns=rain_col, values=rain_col+'count', fill_value=0).reset_index()
#     rain_pivot[rain_col+'count'] = rain_pivot[rain_pivot.columns[1:]].sum(axis=1)
#     rain_pivot = rain_pivot.drop(columns=rain_pivot.columns[1:-1])
    
#     count = count.merge(rain_pivot, on=groupby_col, how='left').fillna(0)
    
#     return count

# def count_changes_sp2(df, groupby_col, sea_warn_col='해상특보', land_warn_col='육상특보', rain_col='강수량점수'):
#     count = df.groupby(groupby_col).apply(lambda x: pd.Series({'태풍&강수count': ((x[sea_warn_col].isin(['TY2', 'TY3'])) & (x[rain_col] != 100)).sum(),
#                                                                   '풍랑&강수count': ((x[sea_warn_col].isin(['WW2', 'WW3'])) & (x[rain_col] != 100)).sum(),
#                                                                   '호우&강수count': ((x[land_warn_col].isin(['SR2', 'SR3'])) & (x[rain_col] != 100)).sum(),
#                                                                   '폭풍해일&강수count': ((x[land_warn_col].isin(['SS2', 'SS3'])) & (x[rain_col] != 100)).sum(),})).reset_index()
#     # 해상 특보와 육상 특보에 대한 필터링 및 경고 횟수 계산
#     sea_warn = df[df[sea_warn_col] != '-'].groupby(groupby_col + [sea_warn_col]).size().reset_index(name=sea_warn_col+'count')
#     land_warn = df[df[land_warn_col].isin(['SR2', 'SR3', 'SS2', 'SS3'])].groupby(groupby_col + [land_warn_col]).size().reset_index(name=land_warn_col+'count')
#     # 피벗 테이블 생성
#     sea_pivot = sea_warn.pivot_table(index=groupby_col, columns=sea_warn_col, values=sea_warn_col+'count', fill_value=0).reset_index()
#     land_pivot = land_warn.pivot_table(index=groupby_col, columns=land_warn_col, values=land_warn_col+'count', fill_value=0).reset_index()
#     # 경고 횟수 데이터를 count DataFrame에 추가
#     count = count.merge(sea_pivot, on=groupby_col, how='left').fillna(0)
#     count = count.merge(land_pivot, on=groupby_col, how='left').fillna(0)
    
#     rain = df[df[rain_col] != 100].groupby(groupby_col + [rain_col]).size().reset_index(name=rain_col+'count')
#     rain_pivot = rain.pivot_table(index=groupby_col, columns=rain_col, values=rain_col+'count', fill_value=0).reset_index()
#     rain_pivot[rain_col+'count'] = rain_pivot[rain_pivot.columns[1:]].sum(axis=1)
#     rain_pivot = rain_pivot.drop(columns=rain_pivot.columns[2:-1])
    
#     count = count.merge(rain_pivot, on=groupby_col, how='left').fillna(0)
    
#     return count


# count2_sp1 = count_changes_sp1(sp_result, ['권역'])
# count2_sp1 = count2_sp1.groupby('권역').agg('sum').reset_index()
# count2_sp2 = count_changes_sp2(sp_result, ['권역', '해수욕장'])

# # WW2와 WW3열이 모두 존재하는 경우에만 WW2와 WW3열을 합쳐서 WW열로 만듦
# # TY2와 TY3열이 모두 존재하는 경우에만 TY2와 TY3열을 합쳐서 TY열로 만듦
# def combine_columns(df, col1, col2, new_col):
#     if col1 in df.columns and col2 in df.columns:
#         df[new_col] = df[col1] + df[col2]
#         df.drop([col1, col2], axis=1, inplace=True)
#     elif col1 in df.columns:
#         df[new_col] = df[col1]
#         df.drop([col1], axis=1, inplace=True)
#     elif col2 in df.columns:
#         df[new_col] = df[col2]
#         df.drop([col2], axis=1, inplace=True)
#     else:
#         df[new_col] = 0
#     return df

# count2_sp1 = combine_columns(count2_sp1, 'WW2', 'WW3', 'WW')
# count2_sp2 = combine_columns(count2_sp2, 'WW2', 'WW3', 'WW')
# count2_sp1 = combine_columns(count2_sp1, 'TY2', 'TY3', 'TY')
# count2_sp2 = combine_columns(count2_sp2, 'TY2', 'TY3', 'TY')
# count2_sp1 = combine_columns(count2_sp1, 'SS2', 'SS3', 'SS')
# count2_sp2 = combine_columns(count2_sp2, 'SS2', 'SS3', 'SS')
# count2_sp1 = combine_columns(count2_sp1, 'SR2', 'SR3', 'SR')
# count2_sp2 = combine_columns(count2_sp2, 'SR2', 'SR3', 'SR')






# count2_sp2 = count2_sp2.groupby(['권역', '해수욕장']).sum().reset_index()


# count2_sp1 = pd.merge(count2_sp1, sp_loc, on='권역')
# count2_sp2 = pd.merge(count2_sp2, sp_locp, on='해수욕장')

# count2_sp1['해수욕장'] = np.nan



# count2_sp2 = count2_sp2.drop('권역_y', axis=1)
# count2_sp2 = count2_sp2.rename(columns={'권역_x':'권역'})
# sp_new_order1 = ['권역', '해수욕장','태풍&강수count','풍랑&강수count','강수량점수','강수량점수count','폭풍해일&강수count','호우&강수count','WW','TY','SR','SS','횟수']
# count2_sp1 = count2_sp1.reindex(columns=sp_new_order1)
# count2_sp3 = pd.concat([count2_sp1, count2_sp2]).reset_index(drop=True)
# count2_sp3.sort_values(by=['권역','해수욕장'], inplace=True)
# count2_sp3 = count2_sp3.reindex(columns=sp_new_order1)



# count2_sp3['권역'] = pd.Categorical(count2_sp3['권역'], categories=SP_new_order3, ordered=True)
# count2_sp3 = count2_sp3.sort_values(['권역','해수욕장']).reset_index(drop=True)



# count2_sp3 = count2_sp3.fillna('A')

# sp_row_sum = count2_sp2["횟수"].sum()
# print()
# print('sp_특보_총통계')
# sp_sum_all = count2_sp1.sum()
# sp_sum_all = pd.DataFrame(sp_sum_all, columns=['변경'])
# sp_sum_all = sp_sum_all.drop('권역', axis=0)
# sp_sum_all = sp_sum_all.rename(index={'횟수': '총예보지수변경'})
# print(sp_sum_all)
# sp_sum_all.to_csv('해수욕_특보_요약.csv', encoding='euc-kr', index=True)
# print('해수욕_특보 총예보건수', SP_row)


# def calculate_percentages(df, row_sum):
#     df['강수량점수%'] = round(df['강수량점수count'] / row_sum * 100, 2)
#     df['WW%'] = round(df['WW'] / row_sum * 100, 2)
#     df['TY%'] = round(df['TY'] / row_sum * 100, 2)
#     df['SS%'] = round(df['SS'] / row_sum * 100, 2)
#     df['SR%'] = round(df['SR'] / row_sum * 100, 2)
#     df['횟수%'] = round(df['횟수'] / row_sum * 100, 2)
#     df['태풍&강수%'] = round(df['태풍&강수count'] / row_sum * 100, 2)
#     df['풍랑&강수%'] = round(df['풍랑&강수count'] / row_sum * 100, 2)
#     df['폭풍해일&강수%'] = round(df['폭풍해일&강수count'] / row_sum * 100, 2)
#     df['호우&강수%'] = round(df['호우&강수count'] / row_sum * 100, 2)
#     return df

# def calculate_percentages1(df, row_sum):
#     df['강수량점수%'] = round(df['강수량점수count'] / row_sum['총 예보건수'] * 100, 2)
#     df['WW%'] = round(df['WW'] / row_sum['총 예보건수'] * 100, 2)
#     df['TY%'] = round(df['TY'] / row_sum['총 예보건수'] * 100, 2)
#     df['SS%'] = round(df['SS'] / row_sum['총 예보건수'] * 100, 2)
#     df['SR%'] = round(df['SR'] / row_sum['총 예보건수'] * 100, 2)
#     df['횟수%'] = round(df['횟수'] / row_sum['총 예보건수'] * 100, 2)
#     df['태풍&강수%'] = round(df['태풍&강수count'] / row_sum['총 예보건수'] * 100, 2)
#     df['풍랑&강수%'] = round(df['풍랑&강수count'] / row_sum['총 예보건수'] * 100, 2)
#     df['폭풍해일&강수%'] = round(df['폭풍해일&강수count'] / row_sum['총 예보건수'] * 100, 2)
#     df['호우&강수%'] = round(df['호우&강수count'] / row_sum['총 예보건수'] * 100, 2)
#     return df

# def calculate_percentages2(df):
#     df['강수량점수%'] = df['강수량점수%'].apply(lambda x: "{:.1f}".format(float(x)))
#     df['WW%'] = df['WW%'].apply(lambda x: "{:.1f}".format(float(x)))
#     df['TY%'] = df['TY%'].apply(lambda x: "{:.1f}".format(float(x)))
#     df['SS%'] = df['SS%'].apply(lambda x: "{:.1f}".format(float(x)))
#     df['SR%'] = df['SR%'].apply(lambda x: "{:.1f}".format(float(x)))
#     df['횟수%'] = df['횟수%'].apply(lambda x: "{:.1f}".format(float(x)))
#     df['태풍&강수%'] = df['태풍&강수%'].apply(lambda x: "{:.1f}".format(float(x)))
#     df['풍랑&강수%'] = df['풍랑&강수%'].apply(lambda x: "{:.1f}".format(float(x)))
#     df['폭풍해일&강수%'] = df['폭풍해일&강수%'].apply(lambda x: "{:.1f}".format(float(x)))
#     df['호우&강수%'] = df['호우&강수%'].apply(lambda x: "{:.1f}".format(float(x)))
#     return df 

# count2_sp3 = pd.merge(SP_loc_row, count2_sp3, on=['권역','해수욕장'], how= 'inner')

# count2_sp1 = calculate_percentages(count2_sp1, sp_row_sum)
# count2_sp2 = calculate_percentages(count2_sp2, sp_row_sum)
# count2_sp3 = calculate_percentages1(count2_sp3, count2_sp3)
# count2_sp1 = calculate_percentages2(count2_sp1)
# count2_sp2 = calculate_percentages2(count2_sp2)
# count2_sp3 = calculate_percentages2(count2_sp3)

# count2_sp3.replace('A', np.nan, inplace=True)

# #count2_sd2 = count2_sd2.drop('권역_y', axis=1)
# #count2_sd2 = count2_sd2.rename(columns={'권역_x':'권역'})

# sp_new_order = ['권역', '횟수','횟수%', 'TY','TY%','WW','WW%', 'SS','SS%', 'SR','SR%', '강수량점수count','강수량점수%', '태풍&강수count','태풍&강수%', '풍랑&강수count','풍랑&강수%', '폭풍해일&강수count','폭풍해일&강수%', '호우&강수count','호우&강수%']
# count2_sp1 = count2_sp1.reindex(columns=sp_new_order)
# sp_new_order2 = ['권역', '해수욕장','횟수','횟수%', 'TY','TY%','WW','WW%', 'SS','SS%', 'SR','SR%', '강수량점수count','강수량점수%','태풍&강수count','태풍&강수%', '풍랑&강수count','풍랑&강수%', '폭풍해일&강수count','폭풍해일&강수%', '호우&강수count','호우&강수%']
# count2_sp2 = count2_sp2.reindex(columns=sp_new_order2)
# sp_new_order5 = ['권역', '해수욕장', '총 예보건수','횟수','횟수%', 'TY','TY%','WW','WW%', 'SS','SS%', 'SR','SR%', '강수량점수count','강수량점수%','태풍&강수count','태풍&강수%', '풍랑&강수count','풍랑&강수%', '폭풍해일&강수count','폭풍해일&강수%', '호우&강수count','호우&강수%']
# count2_sp3 = count2_sp3.reindex(columns=sp_new_order5)


# # 구분열 안의 요소들을 서해, 남해, 동해 순으로 배열
# sp_new_order3 = ['황해중부', '황해남부', '남해서부','남해동부', '제주도', '동해남부', '동해중부']
# count2_sp1['권역'] = pd.Categorical(count2_sp1['권역'], categories=sp_new_order3, ordered=True)
# count2_sp1 = count2_sp1.sort_values('권역').reset_index(drop=True)
# count2_sp2['권역'] = pd.Categorical(count2_sp2['권역'], categories=sp_new_order3, ordered=True)
# count2_sp2 = count2_sp2.sort_values(['권역','해수욕장']).reset_index(drop=True)
# count2_sp3['권역'] = pd.Categorical(count2_sp3['권역'], categories=sp_new_order3, ordered=True)
# count2_sp3 = count2_sp3.sort_values(['권역','해수욕장']).reset_index(drop=True)

# count2_sp3.to_excel('해수욕_지역_특보.xlsx', encoding='euc-kr', float_format='%.1f', index=False)





##################################################################
##################################################################
##################################################################
##################################################################

# 스킨스쿠버
file_path11 = r'C:\Users\sang\Desktop\통계요약본\2310\ssmod.xlsx'
file_path12 = r'C:\Users\sang\Desktop\통계요약본\2310\ssorg.xlsx'
ssm = pd.read_excel(file_path11)
sso = pd.read_excel(file_path12)

# 행의 갯수
SS_row = ssm.shape[0]

# 같은 요소의 개수와 같은 권역의 개수를 세는 작업
grouped = ssm.groupby(['권역', '지역']).size().reset_index(name='총 예보건수')

# 권역 요소별 총합 계산
grouped_sum = grouped.groupby('권역')['총 예보건수'].sum().reset_index(name='총 예보건수')


# 권역 요소 아래에 총합 행 추가
#result = pd.concat([grouped, grouped_sum.assign(지역='총합')])
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
with open('스킨스쿠버_특보.html', 'w') as f:
    f.write(ss_html.to_html())

# 스타일이 적용된 데이터프레임을 xlsx 파일로 저장
ss_html.to_excel('스킨스쿠버_특보.xlsx', index=True)

#각 권역의 갯수, 각 지역의 갯수, 각 변경요인 갯수
ss_loc = ss_result['권역'].value_counts().sort_index().to_frame(name='횟수').reset_index().rename(columns={'index': '권역'})
ss_locp = ss_result.groupby(['권역', '지역'])['지역'].count().reset_index(name='횟수')

#각 권역의 각각의 변경요인 갯수
#각 지역의 각각의 변경요인 갯수
def count_changes_SS(df, groupby_col, sea_warn_col='해상특보', land_warn_col='육상특보'):
    count = df.groupby(groupby_col).apply(lambda x: pd.Series({'지수count': (x['예보지수m'] != x['예보지수o']).sum()})).reset_index()
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
count_ss1 = combine_columns(count_ss1, 'SS2', 'SS3', 'SS')
count_ss2 = combine_columns(count_ss2, 'SS2', 'SS3', 'SS')


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
SS_new_order1 = ['권역', '지역', '지수count', 'WW','TY','SS','SR','횟수']
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
ss_sum_all.to_csv('스킨스쿠버_요약_특보.csv', encoding='euc-kr', index=True)

def calculate_percentages(df, row_sum):
    df['WW%'] = round(df['WW'] / row_sum * 100, 2)
    df['TY%'] = round(df['TY'] / row_sum * 100, 2)
    df['SS%'] = round(df['SS'] / row_sum * 100, 2)
    df['SR%'] = round(df['SR'] / row_sum * 100, 2)
    df['횟수%'] = round(df['횟수'] / row_sum * 100, 2)
    return df

def calculate_percentages1(df, row_sum):
    df['WW%'] = round(df['WW'] / row_sum['총 예보건수'] * 100, 2)
    df['TY%'] = round(df['TY'] / row_sum['총 예보건수'] * 100, 2)
    df['SS%'] = round(df['SS'] / row_sum['총 예보건수'] * 100, 2)
    df['SR%'] = round(df['SR'] / row_sum['총 예보건수'] * 100, 2)
    df['횟수%'] = round(df['횟수'] / row_sum['총 예보건수'] * 100, 2)
    return df

def calculate_percentages2(df):
    df['WW%'] = df['WW%'].apply(lambda x: "{:.1f}".format(float(x)))
    df['TY%'] = df['TY%'].apply(lambda x: "{:.1f}".format(float(x)))
    df['SS%'] = df['SS%'].apply(lambda x: "{:.1f}".format(float(x)))
    df['SR%'] = df['SR%'].apply(lambda x: "{:.1f}".format(float(x)))
    df['횟수%'] = df['횟수%'].apply(lambda x: "{:.1f}".format(float(x)))
    return df

count_ss3 = pd.merge(SS_loc_row, count_ss3, on=['권역','지역'], how= 'inner')

count_ss1 = calculate_percentages(count_ss1, ss_row_sum)
count_ss2 = calculate_percentages(count_ss2, ss_row_sum)
count_ss3 = calculate_percentages1(count_ss3, count_ss3)
count_ss1 = calculate_percentages2(count_ss1)
count_ss2 = calculate_percentages2(count_ss2)
count_ss3 = calculate_percentages2(count_ss3)

count_ss3.replace('A', np.nan, inplace=True)

#count_sr2 = count_sr2.drop('권역_y', axis=1)
#count_sr2 = count_sr2.rename(columns={'권역_x':'권역'})

SS_new_order = ['권역', '횟수','횟수%','TY','TY%','WW','WW%','SS','SS%','SR','SR%']
count_ss1 = count_ss1.reindex(columns=SS_new_order)
SS_new_order2 = ['권역', '지역','횟수','횟수%','TY','TY%','WW','WW%','SS','SS%','SR','SR%']
count_ss2 = count_ss2.reindex(columns=SS_new_order2)
SS_new_order5 = ['권역', '지역', '총 예보건수','횟수','횟수%','TY','TY%','WW','WW%','SS','SS%','SR','SR%']
count_ss3 = count_ss3.reindex(columns=SS_new_order5)

# 권역열 안의 요소들을 서해, 남해, 동해 순으로 배열
SS_new_order3 = ['황해중부', '황해남부', '남해서부', '남해동부', '제주도', '동해남부', '동해중부']
count_ss1['권역'] = pd.Categorical(count_ss1['권역'], categories=SS_new_order3, ordered=True)
count_ss1 = count_ss1.sort_values('권역').reset_index(drop=True)
count_ss2['권역'] = pd.Categorical(count_ss2['권역'], categories=SS_new_order3, ordered=True)
count_ss2 = count_ss2.sort_values(['권역','지역']).reset_index(drop=True)
count_ss3['권역'] = pd.Categorical(count_ss3['권역'], categories=SS_new_order3, ordered=True)
count_ss3 = count_ss3.sort_values(['권역','지역']).reset_index(drop=True)

#print(count_sr2)
#count_sr1.to_csv('서핑_권역_특보.csv', encoding='euc-kr', index=False)
#count_sr2.to_csv('서핑_지역_특보.csv', encoding='euc-kr', index=False)
#count_sr1.to_excel('서핑_권역_특보.xlsx', encoding='euc-kr', float_format='%.1f', index=False)
#count_sr2.to_excel('서핑_지역_특보.xlsx', encoding='euc-kr', float_format='%.1f', index=False)
count_ss3.to_excel('스킨스쿠버_지역_특보.xlsx', encoding='euc-kr', float_format='%.1f', index=False)