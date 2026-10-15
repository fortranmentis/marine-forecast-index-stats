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
    
    sfm1 = sfm[["생산일","권역","지역","최대파고","평균수온","기온점수","풍속점수","해상특보","육상특보","특보점수","예보지수"]]
    sfo1 = sfo[["생산일","권역","지역","최대파고","평균수온","기온점수","풍속점수","해상특보","육상특보","특보점수","예보지수"]]
    
    compare = sfm1['예보지수'] == sfo1['예보지수']
    csfm1 = sfm1[~compare]
    csfo1 = sfo1[~compare]
    
    compare = (csfm1['평균수온'] == csfo1['평균수온']) & (csfm1['최대파고'] == csfo1['최대파고'])
    csfm = csfm1[~compare]
    csfo = csfo1[~compare]
    
    
    # 만약 모든 행에서 모델이 같다면
    if csfm.empty and csfo.empty:
        print()
        print()
        print("SF 모델차이 없음")
        print()
        print()
    else:
    
    
    
        csfm_c = csfm.copy()
        
        csfm_c = csfm_c.sort_values(by=['권역','지역'], ascending=[True, True])
        csfo = csfo.sort_values(by=['권역','지역'], ascending=[True, True])
        
        csfm_c.rename(columns={'최대파고':'최대파고m'},inplace=True)
        csfo.rename(columns={'최대파고':'최대파고o'},inplace=True)
        csfm_c.rename(columns={'평균수온':'평균수온m'},inplace=True)
        csfo.rename(columns={'평균수온':'평균수온o'},inplace=True)
        csfm_c.rename(columns={'기온점수':'기온점수m'},inplace=True)
        csfo.rename(columns={'기온점수':'기온점수o'},inplace=True)
        csfm_c.rename(columns={'풍속점수':'풍속점수m'},inplace=True)
        csfo.rename(columns={'풍속점수':'풍속점수o'},inplace=True)
        csfm_c.rename(columns={'예보지수':'예보지수m'},inplace=True)
        csfo.rename(columns={'예보지수':'예보지수o'},inplace=True)
        
        sf_result = pd.concat([csfm_c,csfo],axis=1)
        
        # 중복된 열을 제거하여 유일한 값을 가지도록 만듦
        sf_result = sf_result.loc[:, ~sf_result.columns.duplicated(keep='first')]
        
        # 컬럼 순서 변경
        sf_result = sf_result[['생산일', '권역', '지역', '최대파고m','최대파고o','평균수온m','평균수온o','기온점수m','기온점수o','풍속점수m','풍속점수o','해상특보','육상특보','특보점수','예보지수m','예보지수o']]
        sf_result = sf_result.reset_index(drop=True)
        sf_result.index = sf_result.index + 1
        
        # 셀 색칠 함수
        def highlight_diff(x, color):
            style = 'background-color: {}'.format(color)
            if x[0] != x[1]:
                return [style, style]
            else:
                return ['', '']
        
        def highlight_special(row):
            if row.name == '해상특보':
                return ['background-color: orange' if x != '-' else '' for x in row]
            else:
                return [''] * len(row)
        
        # 열 비교하여 값이 다른 경우 해당 셀 색칠
        sf_html = sf_result.style.apply(highlight_diff, color='yellow', axis=1, subset=['최대파고m', '최대파고o']) \
                      .apply(highlight_diff, color='blue', axis=1, subset=['평균수온m', '평균수온o']) \
                      .apply(highlight_diff, color='red', axis=1, subset=['기온점수m', '기온점수o']) \
                      .apply(highlight_diff, color='green', axis=1, subset=['풍속점수m', '풍속점수o']) \
                      .apply(lambda x: highlight_special(x), axis=0) \
                      .set_properties(**{'border': '1px solid black'})
        
        
        # 스타일이 적용된 데이터프레임을 HTML 파일로 저장
        with open('바다낚시1_모델.html', 'w') as f:
            f.write(sf_html.to_html())
        
        # 스타일이 적용된 데이터프레임을 xlsx 파일로 저장
        sf_html.to_excel('바다낚시1_모델.xlsx', index=True)
        
        #각 권역의 갯수, 각 지역의 갯수, 각 변경요인 갯수
        sf_loc = sf_result['권역'].value_counts().sort_index().to_frame(name='횟수').reset_index().rename(columns={'index': '권역'})
        sf_locp = sf_result.groupby(['권역', '지역'])['지역'].count().reset_index(name='횟수')
        
        #각 권역의 각각의 변경요인 갯수
        #각 지역의 각각의 변경요인 갯수
        def count_changes_SF(df, groupby_col, warn_col='해상특보'):
            count = df.groupby(groupby_col).apply(lambda x: pd.Series({'최대파고count': (x['최대파고m'] != x['최대파고o']).sum(),
                                                                          '평균수온count': (x['평균수온m'] != x['평균수온o']).sum(),
                                                                          '기온점수count': (x['기온점수m'] != x['기온점수o']).sum(),
                                                                          '풍속점수count': (x['풍속점수m'] != x['풍속점수o']).sum(),
                                                                          '파고&수온count': ((x['최대파고m'] != x['최대파고o']) & (x['평균수온m'] != x['평균수온o'])).sum()})).reset_index()
            warn = df[df[warn_col] != '-'].groupby(groupby_col + [warn_col]).size().reset_index(name=warn_col+'count')
            pivot = warn.pivot_table(index=groupby_col, columns=warn_col, values=warn_col+'count', fill_value=0).reset_index()
            count = count.merge(pivot, on=groupby_col, how='left').fillna(0)
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
        count_sf1 = combine_columns(count_sf1, 'TY2', 'TY3', 'TY_1')
        count_sf2 = combine_columns(count_sf2, 'TY2', 'TY3', 'TY_1')

        count_sf1 = combine_columns(count_sf1, 'WW_1', 'WW1', 'WW')
        count_sf2 = combine_columns(count_sf2, 'WW_1', 'WW1', 'WW')
        count_sf1 = combine_columns(count_sf1, 'TY_1', 'TY1', 'TY')
        count_sf2 = combine_columns(count_sf2, 'TY_1', 'TY1', 'TY')



        
        count_sf1 = pd.merge(count_sf1, sf_loc, on='권역')
        count_sf2 = pd.merge(count_sf2, sf_locp, on='지역')
        
        count_sf1['지역'] = np.nan
        count_sf2 = count_sf2.drop('권역_y', axis=1)
        count_sf2 = count_sf2.rename(columns={'권역_x':'권역'})
        SF_new_order1 = ['권역', '지역','최대파고count','평균수온count','기온점수count','풍속점수count','파고&수온count','WW','TY','횟수']
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
        sf_sum_all.to_csv('바다낚시2_요약_모델.csv', encoding='euc-kr', index=True)
        
    
        def calculate_percentages(df, row_sum):
            df['최대파고%'] = round(df['최대파고count'] / row_sum * 100, 2)
            df['평균수온%'] = round(df['평균수온count'] / row_sum * 100, 2)
            df['기온%'] = round(df['기온점수count'] / row_sum * 100, 2)
            df['풍속%'] = round(df['풍속점수count'] / row_sum * 100, 2)
            df['WW%'] = round(df['WW'] / row_sum * 100, 2)
            df['TY%'] = round(df['TY'] / row_sum * 100, 2)
            df['횟수%'] = round(df['횟수'] / row_sum * 100, 2)
            df['파고&수온%'] = round(df['파고&수온count'] / row_sum * 100, 2)
            return df
        
        def calculate_percentages1(df, row_sum):
            df['최대파고%'] = round(df['최대파고count'] / row_sum['총 예보건수'] * 100, 2)
            df['평균수온%'] = round(df['평균수온count'] / row_sum['총 예보건수'] * 100, 2)
            df['기온%'] = round(df['기온점수count'] / row_sum['총 예보건수'] * 100, 2)
            df['풍속%'] = round(df['풍속점수count'] / row_sum['총 예보건수'] * 100, 2)
            df['WW%'] = round(df['WW'] / row_sum['총 예보건수'] * 100, 2)
            df['TY%'] = round(df['TY'] / row_sum['총 예보건수'] * 100, 2)
            df['횟수%'] = round(df['횟수'] / row_sum['총 예보건수'] * 100, 2)
            df['파고&수온%'] = round(df['파고&수온count'] / row_sum['총 예보건수'] * 100, 2)
            return df
        
        def calculate_percentages2(df):
            df['최대파고%'] = df['최대파고%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['평균수온%'] = df['평균수온%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['기온%'] = df['기온%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['풍속%'] = df['풍속%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['WW%'] = df['WW%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['TY%'] = df['TY%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['횟수%'] = df['횟수%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['파고&수온%'] = df['파고&수온%'].apply(lambda x: "{:.1f}".format(float(x)))
            return df 
        
        count_sf3 = pd.merge(SF_loc_row, count_sf3, on=['권역','지역'], how= 'inner')
        
        
        count_sf1 = calculate_percentages(count_sf1, sf_row_sum)
        count_sf2 = calculate_percentages(count_sf2, sf_row_sum)
        count_sf3 = calculate_percentages1(count_sf3, count_sf3)
        count_sf1 = calculate_percentages2(count_sf1)
        count_sf2 = calculate_percentages2(count_sf2)
        count_sf3 = calculate_percentages2(count_sf3)
        
        count_sf3.replace('A', np.nan, inplace=True)
        
        SF_new_order = ['권역', '횟수','횟수%', '최대파고count', '최대파고%','평균수온count','평균수온%','파고&수온count','파고&수온%']
        count_sf1 = count_sf1.reindex(columns=SF_new_order)
        SF_new_order2 = ['권역', '지역','횟수','횟수%', '최대파고count', '최대파고%','평균수온count','평균수온%','파고&수온count','파고&수온%']
        count_sf2 = count_sf2.reindex(columns=SF_new_order2)
        SF_new_order5 = ['권역', '지역', '총 예보건수', '횟수','횟수%', '최대파고count', '최대파고%','평균수온count','평균수온%','파고&수온count','파고&수온%']
        count_sf3 = count_sf3.reindex(columns=SF_new_order5)
        
        
        
        # 구분열 안의 요소들을 서해, 남해, 동해 순으로 배열
        SF_new_order3 = ['황해중부', '황해남부', '제주도','남해서부','남해동부','동해남부','동해중부']
        count_sf1['권역'] = pd.Categorical(count_sf1['권역'], categories=SF_new_order3, ordered=True)
        count_sf1 = count_sf1.sort_values('권역').reset_index(drop=True)
        count_sf2['권역'] = pd.Categorical(count_sf2['권역'], categories=SF_new_order3, ordered=True)
        count_sf2 = count_sf2.sort_values(['권역','지역']).reset_index(drop=True)
        count_sf3['권역'] = pd.Categorical(count_sf3['권역'], categories=SF_new_order3, ordered=True)
        count_sf3 = count_sf3.sort_values(['권역','지역']).reset_index(drop=True)
        
    
        count_sf3.to_excel('바다낚시3_지역_모델.xlsx', encoding='euc-kr', float_format='%.1f', index=False)
    
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
    
    
    
    #sko['해상특보']=''
    sko['특보']=''
    sko['특보점수']=''
    
    skm1 = skm[["생산일","항로명","선박명","최대파고","풍속점수","특보","특보점수","예보지수"]]
    sko1 = sko[["생산일","항로명","선박명","최대파고","풍속점수","특보","특보점수","예보지수"]]
    
    compare = skm1['예보지수'] == sko1['예보지수']
    cskm1 = skm1[~compare]
    csko1 = sko1[~compare]
    
    
    compare = cskm1['최대파고'] == csko1['최대파고']
    cskm = cskm1[~compare]
    csko = csko1[~compare]
    
    
    # 만약 모든 행에서 모델이 같다면
    if cskm.empty and csko.empty:
        print()
        print()
        print("SK 모델차이 없음")
        print()
        print()
    else:
    
        cskm_c = cskm.copy()
        
        cskm_c = cskm_c.sort_values(by=['항로명','선박명'], ascending=[True, True])
        csko = csko.sort_values(by=['항로명','선박명'], ascending=[True, True])
        
        cskm_c.rename(columns={'최대파고':'최대파고m'},inplace=True)
        csko.rename(columns={'최대파고':'최대파고o'},inplace=True)
        cskm_c.rename(columns={'풍속점수':'풍속점수m'},inplace=True)
        csko.rename(columns={'풍속점수':'풍속점수o'},inplace=True)
        cskm_c.rename(columns={'예보지수':'예보지수m'},inplace=True)
        csko.rename(columns={'예보지수':'예보지수o'},inplace=True)
        
        sk_result = pd.concat([cskm_c,csko],axis=1)
        
        # 중복된 열을 제거하여 유일한 값을 가지도록 만듦
        sk_result = sk_result.loc[:, ~sk_result.columns.duplicated(keep='first')]
        
        # 컬럼 순서 변경
        sk_result = sk_result[['생산일', '항로명', '선박명', '최대파고m','최대파고o','풍속점수m','풍속점수o','특보','특보점수','예보지수m','예보지수o']]
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
        sk_html = sk_result.style.apply(highlight_diff, color='yellow', axis=1, subset=['최대파고m', '최대파고o']) \
                      .apply(highlight_diff, color='blue', axis=1, subset=['풍속점수m', '풍속점수o']) \
                      .apply(lambda x: highlight_special(x), axis=0) \
                      .set_properties(**{'border': '1px solid black'})
        
        # 스타일이 적용된 데이터프레임을 HTML 파일로 저장
        with open('뱃멀미1_모델.html', 'w') as f:
            f.write(sk_html.to_html())
        
        # 스타일이 적용된 데이터프레임을 xlsx 파일로 저장
        sk_html.to_excel('뱃멀미1_모델.xlsx', index=True)
        
        #각 권역의 갯수, 각 지역의 갯수, 각 변경요인 갯수
        sk_loc = sk_result['항로명'].value_counts().sort_index().to_frame(name='횟수').reset_index().rename(columns={'index': '항로명'})
        sk_locp = sk_result.groupby(['항로명', '선박명'])['선박명'].count().reset_index(name='횟수')
        
        #각 권역의 각각의 변경요인 갯수
        def count_changes_SK(df, groupby_col, warn_col='특보'):
            count = df.groupby(groupby_col).apply(lambda x: pd.Series({'최대파고count': (x['최대파고m'] != x['최대파고o']).sum(),
                                                                          '풍속점수count': (x['풍속점수m'] != x['풍속점수o']).sum()})).reset_index()
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
        
        count_sk1 = combine_columns(count_sk1, 'WW2', 'WW3', 'WW')
        count_sk2 = combine_columns(count_sk2, 'WW2', 'WW3', 'WW')
        count_sk1 = combine_columns(count_sk1, 'TY2', 'TY3', 'TY')
        count_sk2 = combine_columns(count_sk2, 'TY2', 'TY3', 'TY')
        
        count_sk1 = pd.merge(count_sk1, sk_loc, on='항로명')
        count_sk2 = pd.merge(count_sk2, sk_locp, on='선박명')
        
        count_sk1['선박명'] = np.nan
        count_sk2 = count_sk2.drop('항로명_y', axis=1)
        count_sk2 = count_sk2.rename(columns={'항로명_x':'항로명'})
        SK_new_order1 = ['항로명', '선박명','최대파고count','풍속점수count','WW','TY','횟수']
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
        sk_sum_all.to_csv('뱃멀미2_요약_모델.csv', encoding='euc-kr', index=True)
        
        def calculate_percentages(df, row_sum):
            df['최대파고%'] = round(df['최대파고count'] / row_sum * 100, 2)
            df['풍속%'] = round(df['풍속점수count'] / row_sum * 100, 2)
            df['WW%'] = round(df['WW'] / row_sum * 100, 2)
            df['TY%'] = round(df['TY'] / row_sum * 100, 2)
            df['횟수%'] = round(df['횟수'] / row_sum * 100, 2)
            return df
        
        def calculate_percentages1(df, row_sum):
            df['최대파고%'] = round(df['최대파고count'] / row_sum['총 예보건수'] * 100, 2)
            df['풍속%'] = round(df['풍속점수count'] / row_sum['총 예보건수'] * 100, 2)
            df['WW%'] = round(df['WW'] / row_sum['총 예보건수'] * 100, 2)
            df['TY%'] = round(df['TY'] / row_sum['총 예보건수'] * 100, 2)
            df['횟수%'] = round(df['횟수'] / row_sum['총 예보건수'] * 100, 2)
            return df
        
        def calculate_percentages2(df):
            df['최대파고%'] =df['최대파고%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['풍속%'] = df['풍속%'].apply(lambda x: "{:.1f}".format(float(x)))
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
        
        
        SK_new_order = ['항로명', '횟수','횟수%', '최대파고count', '최대파고%']
        count_sk1 = count_sk1.reindex(columns=SK_new_order)
        SK_new_order2 = ['항로명', '선박명','횟수','횟수%', '최대파고count', '최대파고%']
        count_sk2 = count_sk2.reindex(columns=SK_new_order2)
        SK_new_order5 = ['항로명', '선박명', '총 예보건수', '횟수','횟수%', '최대파고count', '최대파고%']
        count_sk3 = count_sk3.reindex(columns=SK_new_order5)
        
        
        count_sk3.to_excel('뱃멀미3_선박_모델.xlsx', encoding='euc-kr', float_format='%.1f', index=False)
    
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
    
    srm1 = srm[["생산일","구분","지역","유의파고","풍속점수","파향점수","파주기점수","수온점수","해상특보","육상특보","특보점수","예보지수"]]
    sro1 = sro[["생산일","구분","지역","유의파고","풍속점수","파향점수","파주기점수","수온점수","해상특보","육상특보","특보점수","예보지수"]]
    
    compare = srm1['예보지수'] == sro1['예보지수']
    csrm1 = srm1[~compare]
    csro1 = sro1[~compare]
    
    compare = (csrm1['유의파고'] == csro1['유의파고']) & (csrm1['파향점수'] == csro1['파향점수']) & (csrm1['파주기점수'] == csro1['파주기점수']) & (csrm1['수온점수'] == csro1['수온점수'])
    csrm = csrm1[~compare]
    csro = csro1[~compare]
    
    # 만약 모든 행에서 모델이 같다면
    if csrm.empty and csro.empty:
        print()
        print()
        print("SR 모델차이 없음")
        print()
        print()
    else:
    
    
        csrm_c = csrm.copy()
        
        csrm_c = csrm_c.sort_values(by=['구분','지역'], ascending=[True, True])
        csro = csro.sort_values(by=['구분','지역'], ascending=[True, True])
        
        csrm_c.rename(columns={'유의파고':'유의파고m'},inplace=True)
        csro.rename(columns={'유의파고':'유의파고o'},inplace=True)
        csrm_c.rename(columns={'풍속점수':'풍속점수m'},inplace=True)
        csro.rename(columns={'풍속점수':'풍속점수o'},inplace=True)
        csrm_c.rename(columns={'파향점수':'파향점수m'},inplace=True)
        csro.rename(columns={'파향점수':'파향점수o'},inplace=True)
        csrm_c.rename(columns={'파주기점수':'파주기점수m'},inplace=True)
        csro.rename(columns={'파주기점수':'파주기점수o'},inplace=True)
        csrm_c.rename(columns={'수온점수':'수온점수m'},inplace=True)
        csro.rename(columns={'수온점수':'수온점수o'},inplace=True)
        csrm_c.rename(columns={'예보지수':'예보지수m'},inplace=True)
        csro.rename(columns={'예보지수':'예보지수o'},inplace=True)
        
        sr_result = pd.concat([csrm_c,csro],axis=1)
        
        # 중복된 열을 제거하여 유일한 값을 가지도록 만듦
        sr_result = sr_result.loc[:, ~sr_result.columns.duplicated(keep='first')]
        
        # 컬럼 순서 변경
        sr_result = sr_result[['생산일', '구분', '지역', '유의파고m','유의파고o','풍속점수m','풍속점수o','파향점수m','파향점수o','파주기점수m','파주기점수o','수온점수m','수온점수o','해상특보','육상특보','특보점수','예보지수m','예보지수o']]
        
        sr_result = sr_result.reset_index(drop=True)
        sr_result.index = sr_result.index + 1
        
        # 셀 색칠 함수
        def highlight_diff(x, color):
            style = 'background-color: {}'.format(color)
            if x[0] != x[1]:
                return [style, style]
            else:
                return ['', '']
        def highlight_special(row):
            if row.name == '해상특보':
                return ['background-color: orange' if x != '-' else '' for x in row]
            else:
                return [''] * len(row)    
        
        # 열 비교하여 값이 다른 경우 해당 셀 색칠
        sr_html = sr_result.style.apply(highlight_diff, color='yellow', axis=1, subset=['유의파고m', '유의파고o']) \
                      .apply(highlight_diff, color='blue', axis=1, subset=['풍속점수m', '풍속점수o']) \
                      .apply(highlight_diff, color='red', axis=1, subset=['파향점수m', '파향점수o']) \
                      .apply(highlight_diff, color='green', axis=1, subset=['파주기점수m', '파주기점수o']) \
                      .apply(highlight_diff, color='pink', axis=1, subset=['수온점수m', '수온점수o']) \
                      .apply(lambda x: highlight_special(x), axis=0) \
                      .set_properties(**{'border': '1px solid black'})
        
        
        # 스타일이 적용된 데이터프레임을 HTML 파일로 저장
        with open('서핑1_모델.html', 'w') as f:
            f.write(sr_html.to_html())
        
        # 스타일이 적용된 데이터프레임을 xlsx 파일로 저장
        sr_html.to_excel('서핑1_모델.xlsx', index=True)
        
        #각 권역의 갯수, 각 지역의 갯수, 각 변경요인 갯수
        sr_loc = sr_result['구분'].value_counts().sort_index().to_frame(name='횟수').reset_index().rename(columns={'index': '구분'})
        sr_locp = sr_result.groupby(['구분', '지역'])['지역'].count().reset_index(name='횟수')
        
        #각 권역의 각각의 변경요인 갯수
        #각 지역의 각각의 변경요인 갯수
        
        def count_changes_SR(df, groupby_col, warn_col='해상특보'):
            count = df.groupby(groupby_col).apply(lambda x: pd.Series({'유의파고count': (x['유의파고m'] != x['유의파고o']).sum(),
                                                                          '풍속점수count': (x['풍속점수m'] != x['풍속점수o']).sum(),
                                                                          '파향점수count': (x['파향점수m'] != x['파향점수o']).sum(),
                                                                          '파주기점수count': (x['파주기점수m'] != x['파주기점수o']).sum(),
                                                                          '수온점수count': (x['수온점수m'] != x['수온점수o']).sum(),
                                                                          '파고&수온count': ((x['유의파고m'] != x['유의파고o']) & (x['수온점수m'] != x['수온점수o'])).sum(),
                                                                          '파고&파주기count': ((x['유의파고m'] != x['유의파고o']) & (x['파주기점수m'] != x['파주기점수o'])).sum(),
                                                                          '파고&파향count': ((x['유의파고m'] != x['유의파고o']) & (x['파향점수m'] != x['파향점수o'])).sum(), 
                                                                          '수온&파주기count': ((x['수온점수m'] != x['수온점수o']) & (x['파주기점수m'] != x['파주기점수o'])).sum(), 
                                                                          '수온&파향count': ((x['수온점수m'] != x['수온점수o']) & (x['파향점수m'] != x['파향점수o'])).sum(),
                                                                          '파주기&파향count': ((x['파주기점수m'] != x['파주기점수o']) & (x['파향점수m'] != x['파향점수o'])).sum(),
                                                                          '파고&수온&파주기count': ((x['유의파고m'] != x['유의파고o']) & (x['수온점수m'] != x['수온점수o']) & (x['파주기점수m'] != x['파주기점수o'])).sum(),
                                                                          '파고&수온&파향count': ((x['유의파고m'] != x['유의파고o']) & (x['수온점수m'] != x['수온점수o']) & (x['파향점수m'] != x['파향점수o'])).sum(),
                                                                          '파고&파주기&파향count': ((x['유의파고m'] != x['유의파고o']) & (x['파주기점수m'] != x['파주기점수o']) & (x['파향점수m'] != x['파향점수o'])).sum(),
                                                                          '수온&파주기&파향count': ((x['수온점수m'] != x['수온점수o']) & (x['파주기점수m'] != x['파주기점수o']) & (x['파향점수m'] != x['파향점수o'])).sum(),
                                                                          '파고&수온&파주기&파향count': ((x['유의파고m'] != x['유의파고o']) & (x['수온점수m'] != x['수온점수o']) & (x['파주기점수m'] != x['파주기점수o']) & (x['파향점수m'] != x['파향점수o'])).sum()})).reset_index()
            warn = df[df[warn_col] != '-'].groupby(groupby_col + [warn_col]).size().reset_index(name=warn_col+'count')
            pivot = warn.pivot_table(index=groupby_col, columns=warn_col, values=warn_col+'count', fill_value=0).reset_index()
            count = count.merge(pivot, on=groupby_col, how='left').fillna(0)
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
        count_sr1 = combine_columns(count_sr1, 'TY2', 'TY3', 'TY')
        count_sr2 = combine_columns(count_sr2, 'TY2', 'TY3', 'TY')
        
        count_sr1 = pd.merge(count_sr1, sr_loc, on='구분')
        count_sr2 = pd.merge(count_sr2, sr_locp, on='지역')
        
        
        count_sr1['지역'] = np.nan
        count_sr2 = count_sr2.drop('구분_y', axis=1)
        count_sr2 = count_sr2.rename(columns={'구분_x':'구분'})
        SR_new_order1 = ['구분', '지역','유의파고count','풍속점수count','파향점수count','파주기점수count','수온점수count','파고&수온count','파고&파주기count', '파고&파향count','수온&파주기count',
                          '수온&파향count', '파주기&파향count', '파고&수온&파주기count', '파고&수온&파향count', '파고&파주기&파향count', '수온&파주기&파향count', '파고&수온&파주기&파향count', 'WW','TY','횟수']
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
        sr_sum_all.to_csv('서핑2_요약_모델.csv', encoding='euc-kr', index=True)
        
        def calculate_percentages(df, row_sum):
            df['유의파고%'] = round(df['유의파고count'] / row_sum * 100, 2)
            df['풍속%'] = round(df['풍속점수count'] / row_sum * 100, 2)
            df['파향%'] = round(df['파향점수count'] / row_sum * 100, 2)
            df['파주기%'] = round(df['파주기점수count'] / row_sum * 100, 2)
            df['수온%'] = round(df['수온점수count'] / row_sum * 100, 2)
            df['WW%'] = round(df['WW'] / row_sum * 100, 2)
            df['TY%'] = round(df['TY'] / row_sum * 100, 2)
            df['횟수%'] = round(df['횟수'] / row_sum * 100, 2)
            df['파고&수온%'] = round(df['파고&수온count'] / row_sum * 100, 2)
            df['파고&파주기%'] = round(df['파고&파주기count'] / row_sum * 100, 2)
            df['파고&파향%'] = round(df['파고&파향count'] / row_sum * 100, 2)
            df['수온&파주기%'] = round(df['수온&파주기count'] / row_sum * 100, 2)
            df['수온&파향%'] = round(df['수온&파향count'] / row_sum * 100, 2)
            df['파주기&파향%'] = round(df['파주기&파향count'] / row_sum * 100, 2)
            df['파고&수온&파주기%'] = round(df['파고&수온&파주기count'] / row_sum * 100, 2)
            df['파고&수온&파향%'] = round(df['파고&수온&파향count'] / row_sum * 100, 2)
            df['파고&파주기&파향%'] = round(df['파고&파주기&파향count'] / row_sum * 100, 2)
            df['수온&파주기&파향%'] = round(df['수온&파주기&파향count'] / row_sum * 100, 2)
            df['파고&수온&파주기&파향%'] = round(df['파고&수온&파주기&파향count'] / row_sum * 100, 2)
            return df
        
        def calculate_percentages1(df, row_sum):
            df['유의파고%'] = round(df['유의파고count'] / row_sum['총 예보건수'] * 100, 2)
            df['풍속%'] = round(df['풍속점수count'] / row_sum['총 예보건수'] * 100, 2)
            df['파향%'] = round(df['파향점수count'] / row_sum['총 예보건수'] * 100, 2)
            df['파주기%'] = round(df['파주기점수count'] / row_sum['총 예보건수'] * 100, 2)
            df['수온%'] = round(df['수온점수count'] / row_sum['총 예보건수'] * 100, 2)
            df['WW%'] = round(df['WW'] / row_sum['총 예보건수'] * 100, 2)
            df['TY%'] = round(df['TY'] / row_sum['총 예보건수'] * 100, 2)
            df['횟수%'] = round(df['횟수'] / row_sum['총 예보건수'] * 100, 2)
            df['파고&수온%'] = round(df['파고&수온count'] / row_sum['총 예보건수'] * 100, 2)
            df['파고&파주기%'] = round(df['파고&파주기count'] / row_sum['총 예보건수'] * 100, 2)
            df['파고&파향%'] = round(df['파고&파향count'] / row_sum['총 예보건수'] * 100, 2)
            df['수온&파주기%'] = round(df['수온&파주기count'] / row_sum['총 예보건수'] * 100, 2)
            df['수온&파향%'] = round(df['수온&파향count'] / row_sum['총 예보건수'] * 100, 2)
            df['파주기&파향%'] = round(df['파주기&파향count'] / row_sum['총 예보건수'] * 100, 2)
            df['파고&수온&파주기%'] = round(df['파고&수온&파주기count'] / row_sum['총 예보건수'] * 100, 2)
            df['파고&수온&파향%'] = round(df['파고&수온&파향count'] / row_sum['총 예보건수'] * 100, 2)
            df['파고&파주기&파향%'] = round(df['파고&파주기&파향count'] / row_sum['총 예보건수'] * 100, 2)
            df['수온&파주기&파향%'] = round(df['수온&파주기&파향count'] / row_sum['총 예보건수'] * 100, 2)
            df['파고&수온&파주기&파향%'] = round(df['파고&수온&파주기&파향count'] / row_sum['총 예보건수'] * 100, 2)
            return df
        
        def calculate_percentages2(df):
            df['유의파고%'] = df['유의파고%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['풍속%'] = df['풍속%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['파향%'] = df['파향%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['파주기%'] = df['파주기%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['수온%'] = df['수온%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['WW%'] = df['WW%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['TY%'] = df['TY%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['횟수%'] = df['횟수%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['파고&수온%'] = df['파고&수온%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['파고&파주기%'] = df['파고&파주기%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['파고&파향%'] = df['파고&파향%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['수온&파주기%'] = df['수온&파주기%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['수온&파향%'] = df['수온&파향%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['파주기&파향%'] = df['파주기&파향%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['파고&수온&파주기%'] = df['파고&수온&파주기%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['파고&수온&파향%'] = df['파고&수온&파향%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['파고&파주기&파향%'] = df['파고&파주기&파향%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['수온&파주기&파향%'] = df['수온&파주기&파향%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['파고&수온&파주기&파향%'] = df['파고&수온&파주기&파향%'].apply(lambda x: "{:.1f}".format(float(x)))
            return df
        
        count_sr3 = pd.merge(SR_loc_row, count_sr3, on=['구분','지역'], how= 'inner')
        
        
        count_sr1 = calculate_percentages(count_sr1, sr_row_sum)
        count_sr2 = calculate_percentages(count_sr2, sr_row_sum)
        count_sr3 = calculate_percentages1(count_sr3, count_sr3)
        count_sr1 = calculate_percentages2(count_sr1)
        count_sr2 = calculate_percentages2(count_sr2)
        count_sr3 = calculate_percentages2(count_sr3)
        
    
        
        count_sr3.replace('A', np.nan, inplace=True)
        
        SR_new_order = ['구분', '횟수','횟수%', '유의파고count', '유의파고%','수온점수count','수온%','파주기점수count','파주기%','파향점수count','파향%','파고&수온count','파고&수온%','파고&파주기count','파고&파주기%','파고&파향count','파고&파향%','수온&파주기count','수온&파주기%','수온&파향count','수온&파향%','파주기&파향count','파주기&파향%','파고&수온&파주기count','파고&수온&파주기%','파고&수온&파향count','파고&수온&파향%','파고&파주기&파향count','파고&파주기&파향%','수온&파주기&파향count','수온&파주기&파향%','파고&수온&파주기&파향count','파고&수온&파주기&파향%']
        count_sr1 = count_sr1.reindex(columns=SR_new_order)
        SR_new_order2 = ['구분', '지역','횟수','횟수%', '유의파고count', '유의파고%','수온점수count','수온%','파주기점수count','파주기%','파향점수count','파향%','파고&수온count','파고&수온%','파고&파주기count','파고&파주기%','파고&파향count','파고&파향%','수온&파주기count','수온&파주기%','수온&파향count','수온&파향%','파주기&파향count','파주기&파향%','파고&수온&파주기count','파고&수온&파주기%','파고&수온&파향count','파고&수온&파향%','파고&파주기&파향count','파고&파주기&파향%','수온&파주기&파향count','수온&파주기&파향%','파고&수온&파주기&파향count','파고&수온&파주기&파향%']
        count_sr2 = count_sr2.reindex(columns=SR_new_order2)
        
        SR_new_order5 = ['구분', '지역','총 예보건수', '횟수','횟수%', '유의파고count', '유의파고%','수온점수count','수온%','파주기점수count','파주기%','파향점수count','파향%','파고&수온count','파고&수온%','파고&파주기count','파고&파주기%','파고&파향count','파고&파향%','수온&파주기count','수온&파주기%','수온&파향count','수온&파향%','파주기&파향count','파주기&파향%','파고&수온&파주기count','파고&수온&파주기%','파고&수온&파향count','파고&수온&파향%','파고&파주기&파향count','파고&파주기&파향%','수온&파주기&파향count','수온&파주기&파향%','파고&수온&파주기&파향count','파고&수온&파주기&파향%']
        count_sr3 = count_sr3.reindex(columns=SR_new_order5)
        
        
        # 구분열 안의 요소들을 서해, 남해, 동해 순으로 배열
        SR_new_order3 = ['황해중부', '제주도', '남해서부', '남해동부','동해남부','동해중부']
        count_sr1['구분'] = pd.Categorical(count_sr1['구분'], categories=SR_new_order3, ordered=True)
        count_sr1 = count_sr1.sort_values('구분').reset_index(drop=True)
        count_sr2['구분'] = pd.Categorical(count_sr2['구분'], categories=SR_new_order3, ordered=True)
        count_sr2 = count_sr2.sort_values(['구분','지역']).reset_index(drop=True)
        count_sr3['구분'] = pd.Categorical(count_sr3['구분'], categories=SR_new_order3, ordered=True)
        count_sr3 = count_sr3.sort_values(['구분','지역']).reset_index(drop=True)
        
        
        count_sr3.to_excel('서핑3_지역_모델.xlsx', encoding='euc-kr', float_format='%.1f', index=False)
    
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
    
    # 행의 갯수
    SP_row = spm.shape[0]
    
    
    # 같은 요소의 개수와 같은 권역의 개수를 세는 작업
    grouped = spm.groupby(['권역', '해수욕장']).size().reset_index(name='총 예보건수')
    
    # 권역 요소별 총합 계산
    grouped_sum = grouped.groupby('권역')['총 예보건수'].sum().reset_index(name='총 예보건수')
    
    
    # 권역 요소 아래에 총합 행 추가
    result = pd.concat([grouped, grouped_sum])
    
    SP_new_order3 = ['황해중부', '황해남부', '제주도','남해서부','남해동부','동해남부','동해중부']
    result['권역'] = pd.Categorical(result['권역'], categories=SP_new_order3, ordered=True)
    result = result.sort_values(['권역','해수욕장']).reset_index(drop=True)
    
    # 권역 열의 맨 아래에 총합 위치
    result.loc[result['해수욕장'] == '총합', '권역'] = np.nan
    result = result.fillna('A')
    SP_loc_row = result
    
    
    
    
    spo['해상특보']=''
    spo['육상특보']=''
    spo['특보점수']=''
    
    spm1 = spm[["생산일","권역","해수욕장","최대파고","평균수온","기온점수","풍속점수","해상특보","육상특보","특보점수","예보지수"]]
    spo1 = spo[["생산일","권역","해수욕장","최대파고","평균수온","기온점수","풍속점수","해상특보","육상특보","특보점수","예보지수"]]
    
    compare = spm1['예보지수'] == spo1['예보지수']
    cspm1 = spm1[~compare]
    cspo1 = spo1[~compare]
    
    compare = (cspm1['평균수온'] == cspo1['평균수온']) & (cspm1['최대파고'] == cspo1['최대파고'])
    cspm = cspm1[~compare]
    cspo = cspo1[~compare]
    
    
    # 만약 모든 행에서 모델이 같다면
    if cspm.empty and cspo.empty:
        print()
        print()
        print("SP 모델차이 없음")
        print()
        print()
    else:
    
    
        cspm_c = cspm.copy()
        
        cspm_c = cspm_c.sort_values(by=['권역','해수욕장'], ascending=[True, True])
        cspo = cspo.sort_values(by=['권역','해수욕장'], ascending=[True, True])
        
        cspm_c.rename(columns={'최대파고':'최대파고m'},inplace=True)
        cspo.rename(columns={'최대파고':'최대파고o'},inplace=True)
        cspm_c.rename(columns={'평균수온':'평균수온m'},inplace=True)
        cspo.rename(columns={'평균수온':'평균수온o'},inplace=True)
        cspm_c.rename(columns={'기온점수':'기온점수m'},inplace=True)
        cspo.rename(columns={'기온점수':'기온점수o'},inplace=True)
        cspm_c.rename(columns={'풍속점수':'풍속점수m'},inplace=True)
        cspo.rename(columns={'풍속점수':'풍속점수o'},inplace=True)
        cspm_c.rename(columns={'예보지수':'예보지수m'},inplace=True)
        cspo.rename(columns={'예보지수':'예보지수o'},inplace=True)
        
        sp_result = pd.concat([cspm_c,cspo],axis=1)
        
        # 중복된 열을 제거하여 유일한 값을 가지도록 만듦
        sp_result = sp_result.loc[:, ~sp_result.columns.duplicated(keep='first')]
        
        # 컬럼 순서 변경
        sp_result = sp_result[['생산일', '권역', '해수욕장', '최대파고m','최대파고o','평균수온m','평균수온o','기온점수m','기온점수o','풍속점수m','풍속점수o','해상특보','육상특보','특보점수','예보지수m','예보지수o']]
        sp_result = sp_result.reset_index(drop=True)
        sp_result.index = sp_result.index + 1
        
        # 셀 색칠 함수
        def highlight_diff(x, color):
            style = 'background-color: {}'.format(color)
            if x[0] != x[1]:
                return [style, style]
            else:
                return ['', '']
        
        def highlight_special(row):
            if row.name == '해상특보':
                return ['background-color: orange' if x != '-' else '' for x in row]
            else:
                return [''] * len(row)
        
        # 열 비교하여 값이 다른 경우 해당 셀 색칠
        sp_html = sp_result.style.apply(highlight_diff, color='yellow', axis=1, subset=['최대파고m', '최대파고o']) \
                      .apply(highlight_diff, color='blue', axis=1, subset=['평균수온m', '평균수온o']) \
                      .apply(highlight_diff, color='red', axis=1, subset=['기온점수m', '기온점수o']) \
                      .apply(highlight_diff, color='green', axis=1, subset=['풍속점수m', '풍속점수o']) \
                      .apply(lambda x: highlight_special(x), axis=0) \
                      .set_properties(**{'border': '1px solid black'})
        
        
        # 스타일이 적용된 데이터프레임을 HTML 파일로 저장
        with open('해수욕1_모델.html', 'w') as f:
            f.write(sp_html.to_html())
        
        # 스타일이 적용된 데이터프레임을 xlsx 파일로 저장
        sp_html.to_excel('해수욕1_모델.xlsx', index=True)
        
        #각 권역의 갯수, 각 지역의 갯수, 각 변경요인 갯수
        sp_loc = sp_result['권역'].value_counts().sort_index().to_frame(name='횟수').reset_index().rename(columns={'index': '권역'})
        sp_locp = sp_result.groupby(['권역', '해수욕장'])['해수욕장'].count().reset_index(name='횟수')
        
        #각 권역의 각각의 변경요인 갯수
        #각 지역의 각각의 변경요인 갯수
        def count_changes_SP(df, groupby_col, warn_col='해상특보'):
            count = df.groupby(groupby_col).apply(lambda x: pd.Series({'최대파고count': (x['최대파고m'] != x['최대파고o']).sum(),
                                                                          '평균수온count': (x['평균수온m'] != x['평균수온o']).sum(),
                                                                          '기온점수count': (x['기온점수m'] != x['기온점수o']).sum(),
                                                                          '풍속점수count': (x['풍속점수m'] != x['풍속점수o']).sum(),
                                                                          '파고&수온count': ((x['최대파고m'] != x['최대파고o']) & (x['평균수온m'] != x['평균수온o'])).sum()})).reset_index()
            warn = df[df[warn_col] != '-'].groupby(groupby_col + [warn_col]).size().reset_index(name=warn_col+'count')
            pivot = warn.pivot_table(index=groupby_col, columns=warn_col, values=warn_col+'count', fill_value=0).reset_index()
            count = count.merge(pivot, on=groupby_col, how='left').fillna(0)
            return count
        
        count_sp1 = count_changes_SP(sp_result, ['권역'])
        count_sp2 = count_changes_SP(sp_result, ['권역', '해수욕장'])
        
        
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
        
        count_sp1 = combine_columns(count_sp1, 'WW2', 'WW3', 'WW')
        count_sp2 = combine_columns(count_sp2, 'WW2', 'WW3', 'WW')
        count_sp1 = combine_columns(count_sp1, 'TY2', 'TY3', 'TY')
        count_sp2 = combine_columns(count_sp2, 'TY2', 'TY3', 'TY')
        
        count_sp1 = pd.merge(count_sp1, sp_loc, on='권역')
        count_sp2 = pd.merge(count_sp2, sp_locp, on='해수욕장')
        
        count_sp1['해수욕장'] = np.nan
        count_sp2 = count_sp2.drop('권역_y', axis=1)
        count_sp2 = count_sp2.rename(columns={'권역_x':'권역'})
        SP_new_order1 = ['권역', '해수욕장','최대파고count','평균수온count','기온점수count','풍속점수count','파고&수온count','WW','TY','횟수']
        count_sp3 = pd.concat([count_sp1, count_sp2], ignore_index=True)
        count_sp3 = count_sp3.reindex(columns=SP_new_order1)
        
        count_sp3['권역'] = pd.Categorical(count_sp3['권역'], categories=SP_new_order3, ordered=True)
        count_sp3 = count_sp3.sort_values(['권역','해수욕장']).reset_index(drop=True)
        
        # 권역 열의 맨 아래에 총합 위치
        count_sp3.loc[result['해수욕장'] == '총합', '권역'] = np.nan
        count_sp3 = count_sp3.fillna('A')
        
        
        sp_row_sum = count_sp1["횟수"].sum()
        
        
        print()
        print('SP 총통계')
        sp_sum_all = count_sp1.sum()
        sp_sum_all = pd.DataFrame(sp_sum_all, columns=['변경'])
        sp_sum_all = sp_sum_all.drop('권역', axis=0)
        sp_sum_all = sp_sum_all.rename(index={'횟수': '총예보지수변경'})
        print(sp_sum_all)
        sp_sum_all.to_csv('해수욕2_요약_모델.csv', encoding='euc-kr', index=True)
        
        
        def calculate_percentages(df, row_sum):
            df['최대파고%'] = round(df['최대파고count'] / row_sum * 100, 2)
            df['평균수온%'] = round(df['평균수온count'] / row_sum * 100, 2)
            df['기온%'] = round(df['기온점수count'] / row_sum * 100, 2)
            df['풍속%'] = round(df['풍속점수count'] / row_sum * 100, 2)
            df['WW%'] = round(df['WW'] / row_sum * 100, 2)
            df['TY%'] = round(df['TY'] / row_sum * 100, 2)
            df['횟수%'] = round(df['횟수'] / row_sum * 100, 2)
            df['파고&수온%'] = round(df['파고&수온count'] / row_sum * 100, 2)
            return df
        
        def calculate_percentages1(df, row_sum):
            df['최대파고%'] = round(df['최대파고count'] / row_sum['총 예보건수'] * 100, 2)
            df['평균수온%'] = round(df['평균수온count'] / row_sum['총 예보건수'] * 100, 2)
            df['기온%'] = round(df['기온점수count'] / row_sum['총 예보건수'] * 100, 2)
            df['풍속%'] = round(df['풍속점수count'] / row_sum['총 예보건수'] * 100, 2)
            df['WW%'] = round(df['WW'] / row_sum['총 예보건수'] * 100, 2)
            df['TY%'] = round(df['TY'] / row_sum['총 예보건수'] * 100, 2)
            df['횟수%'] = round(df['횟수'] / row_sum['총 예보건수'] * 100, 2)
            df['파고&수온%'] = round(df['파고&수온count'] / row_sum['총 예보건수'] * 100, 2)
            return df
        
        def calculate_percentages2(df):
            df['최대파고%'] = df['최대파고%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['평균수온%'] = df['평균수온%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['기온%'] = df['기온%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['풍속%'] = df['풍속%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['WW%'] = df['WW%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['TY%'] = df['TY%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['횟수%'] = df['횟수%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['파고&수온%'] = df['파고&수온%'].apply(lambda x: "{:.1f}".format(float(x)))
            return df 
        
        count_sp3 = pd.merge(SP_loc_row, count_sp3, on=['권역','해수욕장'], how= 'inner')
        
        
        count_sp1 = calculate_percentages(count_sp1, sp_row_sum)
        count_sp2 = calculate_percentages(count_sp2, sp_row_sum)
        count_sp3 = calculate_percentages1(count_sp3, count_sp3)
        count_sp1 = calculate_percentages2(count_sp1)
        count_sp2 = calculate_percentages2(count_sp2)
        count_sp3 = calculate_percentages2(count_sp3)
        
        count_sp3.replace('A', np.nan, inplace=True)
        
        SP_new_order = ['권역', '횟수','횟수%', '최대파고count', '최대파고%','평균수온count','평균수온%','파고&수온count','파고&수온%']
        count_sp1 = count_sp1.reindex(columns=SP_new_order)
        SP_new_order2 = ['권역', '해수욕장','횟수','횟수%', '최대파고count', '최대파고%','평균수온count','평균수온%','파고&수온count','파고&수온%']
        count_sp2 = count_sp2.reindex(columns=SP_new_order2)
        SP_new_order5 = ['권역', '해수욕장', '총 예보건수', '횟수','횟수%', '최대파고count', '최대파고%','평균수온count','평균수온%','파고&수온count','파고&수온%']
        count_sp3 = count_sp3.reindex(columns=SP_new_order5)
        
        
        
        # 구분열 안의 요소들을 서해, 남해, 동해 순으로 배열
        SP_new_order3 = ['황해중부', '황해남부', '제주도','남해서부','남해동부','동해남부','동해중부']
        count_sp1['권역'] = pd.Categorical(count_sp1['권역'], categories=SP_new_order3, ordered=True)
        count_sp1 = count_sp1.sort_values('권역').reset_index(drop=True)
        count_sp2['권역'] = pd.Categorical(count_sp2['권역'], categories=SP_new_order3, ordered=True)
        count_sp2 = count_sp2.sort_values(['권역','해수욕장']).reset_index(drop=True)
        count_sp3['권역'] = pd.Categorical(count_sp3['권역'], categories=SP_new_order3, ordered=True)
        count_sp3 = count_sp3.sort_values(['권역','해수욕장']).reset_index(drop=True)
        
        
        count_sp3.to_excel('해수욕3_지역_모델.xlsx', encoding='euc-kr', float_format='%.1f', index=False)
    
    
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
    #result = pd.concat([grouped, grouped_sum.assign(지역='총합')])
    result = pd.concat([grouped, grouped_sum])
    
    SS_new_order3 = ['황해중부', '황해남부', '제주도','남해서부','남해동부','동해남부','동해중부']
    result['권역'] = pd.Categorical(result['권역'], categories=SS_new_order3, ordered=True)
    result = result.sort_values(['권역','지역']).reset_index(drop=True)
    
    # 권역 열의 맨 아래에 총합 위치
    result.loc[result['지역'] == '총합', '권역'] = np.nan
    result = result.fillna('A')
    SS_loc_row = result
    
    
    sso['해상특보']=''
    sso['육상특보']=''
    sso['특보점수']=''
    
    ssm1 = ssm[["생산일","권역","지역","최대파고","평균수온","유속점수","해상특보","육상특보","특보점수","예보지수"]]
    sso1 = sso[["생산일","권역","지역","최대파고","평균수온","유속점수","해상특보","육상특보","특보점수","예보지수"]]
    
    compare = ssm1['예보지수'] == sso1['예보지수']
    cssm1 = ssm1[~compare]
    csso1 = sso1[~compare]
    
    compare = (cssm1['평균수온'] == csso1['평균수온']) & (cssm1['최대파고'] == csso1['최대파고'])
    cssm = cssm1[~compare]
    csso = csso1[~compare]
    
    # 만약 모든 행에서 모델이 같다면
    if cssm.empty and csso.empty:
        print()
        print()
        print("SS 모델차이 없음")
        print()
        print()
    else:
    
    
        cssm_c = cssm.copy()
        
        cssm_c = cssm_c.sort_values(by=['권역','지역'], ascending=[True, True])
        csso = csso.sort_values(by=['권역','지역'], ascending=[True, True])
        
        cssm_c.rename(columns={'최대파고':'최대파고m'},inplace=True)
        csso.rename(columns={'최대파고':'최대파고o'},inplace=True)
        cssm_c.rename(columns={'평균수온':'평균수온m'},inplace=True)
        csso.rename(columns={'평균수온':'평균수온o'},inplace=True)
        cssm_c.rename(columns={'유속점수':'유속점수m'},inplace=True)
        csso.rename(columns={'유속점수':'유속점수o'},inplace=True)
        cssm_c.rename(columns={'예보지수':'예보지수m'},inplace=True)
        csso.rename(columns={'예보지수':'예보지수o'},inplace=True)
        
        ss_result = pd.concat([cssm_c,csso],axis=1)
        
        # 중복된 열을 제거하여 유일한 값을 가지도록 만듦
        ss_result = ss_result.loc[:, ~ss_result.columns.duplicated(keep='first')]
        
        # 컬럼 순서 변경
        ss_result = ss_result[['생산일', '권역', '지역', '최대파고m','최대파고o','평균수온m','평균수온o','유속점수m','유속점수o','해상특보','육상특보','특보점수','예보지수m','예보지수o']]
        ss_result = ss_result.reset_index(drop=True)
        ss_result.index = ss_result.index + 1
        
        # 셀 색칠 함수
        def highlight_diff(x, color):
            style = 'background-color: {}'.format(color)
            if x[0] != x[1]:
                return [style, style]
            else:
                return ['', '']
        
        def highlight_special(row):
            if row.name == '해상특보':
                return ['background-color: orange' if x != '-' else '' for x in row]
            else:
                return [''] * len(row)
        
        # 열 비교하여 값이 다른 경우 해당 셀 색칠
        ss_html = ss_result.style.apply(highlight_diff, color='yellow', axis=1, subset=['최대파고m', '최대파고o']) \
                      .apply(highlight_diff, color='blue', axis=1, subset=['평균수온m', '평균수온o']) \
                      .apply(highlight_diff, color='red', axis=1, subset=['유속점수m', '유속점수o']) \
                      .apply(lambda x: highlight_special(x), axis=0) \
                      .set_properties(**{'border': '1px solid black'})
        
        
        # 스타일이 적용된 데이터프레임을 HTML 파일로 저장
        with open('스킨스쿠버1_모델.html', 'w') as f:
            f.write(ss_html.to_html())
        
        # 스타일이 적용된 데이터프레임을 xlsx 파일로 저장
        ss_html.to_excel('스킨스쿠버1_모델.xlsx', index=True)
        
        #각 권역의 갯수, 각 지역의 갯수, 각 변경요인 갯수
        ss_loc = ss_result['권역'].value_counts().sort_index().to_frame(name='횟수').reset_index().rename(columns={'index': '권역'})
        ss_locp = ss_result.groupby(['권역', '지역'])['지역'].count().reset_index(name='횟수')
        
        #각 권역의 각각의 변경요인 갯수
        #각 지역의 각각의 변경요인 갯수
        def count_changes_SS(df, groupby_col, warn_col='해상특보'):
            count = df.groupby(groupby_col).apply(lambda x: pd.Series({'최대파고count': (x['최대파고m'] != x['최대파고o']).sum(),
                                                                          '평균수온count': (x['평균수온m'] != x['평균수온o']).sum(),
                                                                          '유속점수count': (x['유속점수m'] != x['유속점수o']).sum(),
                                                                          '파고&수온count': ((x['최대파고m'] != x['최대파고o']) & (x['평균수온m'] != x['평균수온o'])).sum()})).reset_index()
            warn = df[df[warn_col] != '-'].groupby(groupby_col + [warn_col]).size().reset_index(name=warn_col+'count')
            pivot = warn.pivot_table(index=groupby_col, columns=warn_col, values=warn_col+'count', fill_value=0).reset_index()
            count = count.merge(pivot, on=groupby_col, how='left').fillna(0)
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
        
        count_ss1 = combine_columns(count_ss1, 'WW2', 'WW3', 'WW')
        count_ss2 = combine_columns(count_ss2, 'WW2', 'WW3', 'WW')
        count_ss1 = combine_columns(count_ss1, 'TY2', 'TY3', 'TY')
        count_ss2 = combine_columns(count_ss2, 'TY2', 'TY3', 'TY')
        
        count_ss1 = pd.merge(count_ss1, ss_loc, on='권역')
        count_ss2 = pd.merge(count_ss2, ss_locp, on='지역')
        
        count_ss1['지역'] = np.nan
        count_ss2 = count_ss2.drop('권역_y', axis=1)
        count_ss2 = count_ss2.rename(columns={'권역_x':'권역'})
        SS_new_order1 = ['권역', '지역','최대파고count','평균수온count','유속점수count','파고&수온count','WW','TY','횟수']
        count_ss3 = pd.concat([count_ss1, count_ss2], ignore_index=True)
        count_ss3 = count_ss3.reindex(columns=SS_new_order1)
        
        count_ss3['권역'] = pd.Categorical(count_ss3['권역'], categories=SS_new_order3, ordered=True)
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
        ss_sum_all.to_csv('스킨스쿠버2_요약_모델.csv', encoding='euc-kr', index=True)
        
        
        def calculate_percentages(df, row_sum):
            df['최대파고%'] = round(df['최대파고count'] / row_sum * 100, 2)
            df['평균수온%'] = round(df['평균수온count'] / row_sum * 100, 2)
            df['유속%'] = round(df['유속점수count'] / row_sum * 100, 2)
            df['WW%'] = round(df['WW'] / row_sum * 100, 2)
            df['TY%'] = round(df['TY'] / row_sum * 100, 2)
            df['횟수%'] = round(df['횟수'] / row_sum * 100, 2)
            df['파고&수온%'] = round(df['파고&수온count'] / row_sum * 100, 2)
            return df
        
        def calculate_percentages1(df, row_sum):
            df['최대파고%'] = round(df['최대파고count'] / row_sum['총 예보건수'] * 100, 2)
            df['평균수온%'] = round(df['평균수온count'] / row_sum['총 예보건수'] * 100, 2)
            df['유속%'] = round(df['유속점수count'] / row_sum['총 예보건수'] * 100, 2)
            df['WW%'] = round(df['WW'] / row_sum['총 예보건수'] * 100, 2)
            df['TY%'] = round(df['TY'] / row_sum['총 예보건수'] * 100, 2)
            df['횟수%'] = round(df['횟수'] / row_sum['총 예보건수'] * 100, 2)
            df['파고&수온%'] = round(df['파고&수온count'] / row_sum['총 예보건수'] * 100, 2)
            return df
        
        def calculate_percentages2(df):
            df['최대파고%'] = df['최대파고%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['평균수온%'] = df['평균수온%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['유속%'] = df['유속%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['WW%'] = df['WW%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['TY%'] = df['TY%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['횟수%'] = df['횟수%'].apply(lambda x: "{:.1f}".format(float(x)))
            df['파고&수온%'] = df['파고&수온%'].apply(lambda x: "{:.1f}".format(float(x)))
            return df 
        
        count_ss3 = pd.merge(SS_loc_row, count_ss3, on=['권역','지역'], how= 'inner')
        
        
        count_ss1 = calculate_percentages(count_ss1, ss_row_sum)
        count_ss2 = calculate_percentages(count_ss2, ss_row_sum)
        count_ss3 = calculate_percentages1(count_ss3, count_ss3)
        count_ss1 = calculate_percentages2(count_ss1)
        count_ss2 = calculate_percentages2(count_ss2)
        count_ss3 = calculate_percentages2(count_ss3)
        
        count_ss3.replace('A', np.nan, inplace=True)
        
        SS_new_order = ['권역', '횟수','횟수%', '최대파고count', '최대파고%','평균수온count','평균수온%','파고&수온count','파고&수온%']
        count_ss1 = count_ss1.reindex(columns=SS_new_order)
        SS_new_order2 = ['권역', '지역','횟수','횟수%', '최대파고count', '최대파고%','평균수온count','평균수온%','파고&수온count','파고&수온%']
        count_ss2 = count_ss2.reindex(columns=SS_new_order2)
        SS_new_order5 = ['권역', '지역', '총 예보건수', '횟수','횟수%', '최대파고count', '최대파고%','평균수온count','평균수온%','파고&수온count','파고&수온%']
        count_ss3 = count_ss3.reindex(columns=SS_new_order5)
        
        
        
        # 구분열 안의 요소들을 서해, 남해, 동해 순으로 배열
        SS_new_order3 = ['황해중부', '황해남부', '제주도','남해서부','남해동부','동해남부','동해중부']
        count_ss1['권역'] = pd.Categorical(count_ss1['권역'], categories=SS_new_order3, ordered=True)
        count_ss1 = count_ss1.sort_values('권역').reset_index(drop=True)
        count_ss2['권역'] = pd.Categorical(count_ss2['권역'], categories=SS_new_order3, ordered=True)
        count_ss2 = count_ss2.sort_values(['권역','지역']).reset_index(drop=True)
        count_ss3['권역'] = pd.Categorical(count_ss3['권역'], categories=SS_new_order3, ordered=True)
        count_ss3 = count_ss3.sort_values(['권역','지역']).reset_index(drop=True)
        
    
        count_ss3.to_excel('스킨스쿠버3_지역_모델.xlsx', encoding='euc-kr', float_format='%.1f', index=False)

