# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 10:44:03 2023

@author: sang
"""

import pandas as pd
import numpy as np


# 불러올 파일들이 있는 디렉토리 경로
#file_path = 'C:/Users/sang/Desktop/test/*.xlsx'

# 파일불러오기
sdm = pd.read_excel('sdmod.xlsx') #강수량 해상육상특보
sdo = pd.read_excel('sdorg.xlsx') #X
sfm = pd.read_excel('sfmod.xlsx') #해상육상특보
sfo = pd.read_excel('sforg.xlsx') #X
skm = pd.read_excel('skmod.xlsx') #특보
sko = pd.read_excel('skorg.xlsx') #X
srm = pd.read_excel('srmod.xlsx') #해상육상특보
sro = pd.read_excel('srorg.xlsx') #X
tlm = pd.read_excel('tlmod.xlsx') #강수량 해상육상특보
tlo = pd.read_excel('tlorg.xlsx') #X
spm = pd.read_excel('spmod.xlsx') #강수량 해상육상특보
spo = pd.read_excel('sporg.xlsx') #X
ssm = pd.read_excel('ssmod.xlsx') #강수량 해상육상특보
sso = pd.read_excel('ssorg.xlsx') #X


sdmA = sdm[["생산일","강수량","해상특보","육상특보"]]
sfmA = sfm[["생산일","해상특보","육상특보"]]
skmA = skm[["생산일","특보"]]
srmA = srm[["생산일","해상특보","육상특보"]]
tlmA = tlm[["생산일","강수량","해상특보","육상특보"]]
spmA = spm[["생산일","강수량","해상특보","육상특보"]]
ssmA = ssm[["생산일","해상특보","육상특보"]]


sdmA = sdmA.replace('-', np.nan)
sfmA= sfmA.replace('-', np.nan)
skmA = skmA.replace('-', np.nan)
srmA  = srmA .replace('-', np.nan)
tlmA  = tlmA .replace('-', np.nan)
spmA  = spmA .replace('-', np.nan)
ssmA  = ssmA .replace('-', np.nan)



# 중복 생산일 제거 후 '특보' 값이 '원하는 특보'인 행만 추출
def filter_dataframe(df, condition):
    return df[df.apply(lambda x: condition(x), axis=1)].drop_duplicates('생산일')
WW_sdmA = filter_dataframe(sdmA, lambda x: x['해상특보'] in ['WW1','WW2','WW3'])
TY_sdmA = filter_dataframe(sdmA, lambda x: x['해상특보'] in ['TY1','TY2','TY3'])
RD_sdmA = filter_dataframe(sdmA, lambda x: int(x['강수량']) > 0)

WW_sfmA = filter_dataframe(sfmA, lambda x: x['해상특보'] in ['WW1','WW2','WW3'])
TY_sfmA = filter_dataframe(sfmA, lambda x: x['해상특보'] in ['TY1','TY2','TY3'])

WW_skmA = filter_dataframe(skmA, lambda x: x['특보'] in ['WW1','WW2','WW3'])
TY_skmA = filter_dataframe(skmA, lambda x: x['특보'] in ['TY1','TY2','TY3'])

WW_srmA = filter_dataframe(srmA, lambda x: x['해상특보'] in ['WW1','WW2','WW3'])
TY_srmA = filter_dataframe(srmA, lambda x: x['해상특보'] in ['TY1','TY2','TY3'])

WW_tlmA = filter_dataframe(tlmA, lambda x: x['해상특보'] in ['WW1','WW2','WW3'])
TY_tlmA = filter_dataframe(tlmA, lambda x: x['해상특보'] in ['TY1','TY2','TY3'])
RD_tlmA = filter_dataframe(tlmA, lambda x: int(x['강수량']) > 0)

WW_spmA = filter_dataframe(spmA, lambda x: x['해상특보'] in ['WW1','WW2','WW3'])
TY_spmA = filter_dataframe(spmA, lambda x: x['해상특보'] in ['TY1','TY2','TY3'])
RD_spmA = filter_dataframe(spmA, lambda x: int(x['강수량']) > 0)

WW_ssmA = filter_dataframe(ssmA, lambda x: x['해상특보'] in ['WW1','WW2','WW3'])
TY_ssmA = filter_dataframe(ssmA, lambda x: x['해상특보'] in ['TY1','TY2','TY3'])


SS_sdmA = filter_dataframe(sdmA, lambda x: x['육상특보'] in ['SS1','SS2','SS3'])
SR_sdmA = filter_dataframe(sdmA, lambda x: x['육상특보'] in ['SR1','SR2','SR3'])

SS_sfmA = filter_dataframe(sfmA, lambda x: x['육상특보'] in ['SS1','SS2','SS3'])
SR_sfmA = filter_dataframe(sfmA, lambda x: x['육상특보'] in ['SR1','SR2','SR3'])

SS_srmA = filter_dataframe(srmA, lambda x: x['육상특보'] in ['SS1','SS2','SS3'])
SR_srmA = filter_dataframe(srmA, lambda x: x['육상특보'] in ['SR1','SR2','SR3'])

SS_skmA = filter_dataframe(skmA, lambda x: x['특보'] in ['SS1','SS2','SS3'])
SR_skmA = filter_dataframe(skmA, lambda x: x['특보'] in ['SR1','SR2','SR3'])

SS_tlmA = filter_dataframe(tlmA, lambda x: x['육상특보'] in ['SS1','SS2','SS3'])
SR_tlmA = filter_dataframe(tlmA, lambda x: x['육상특보'] in ['SR1','SR2','SR3'])

SS_spmA = filter_dataframe(spmA, lambda x: x['육상특보'] in ['SS1','SS2','SS3'])
SR_spmA = filter_dataframe(spmA, lambda x: x['육상특보'] in ['SR1','SR2','SR3'])

SS_ssmA = filter_dataframe(ssmA, lambda x: x['육상특보'] in ['SS1','SS2','SS3'])
SR_ssmA = filter_dataframe(ssmA, lambda x: x['육상특보'] in ['SR1','SR2','SR3'])



RD_sdmA = RD_sdmA[["생산일","강수량"]]
RD_tlmA = RD_tlmA[["생산일","강수량"]]
RD_spmA = RD_spmA[["생산일","강수량"]]


WW_tlmA.columns = ['생산일', '강수량','해상특보tl','육상특보tl']
TY_tlmA.columns = ['생산일', '강수량','해상특보tl','육상특보tl']
SS_tlmA.columns = ['생산일', '강수량','해상특보tl','육상특보tl']
SR_tlmA.columns = ['생산일', '강수량','해상특보tl','육상특보tl']


WW_spmA.columns = ['생산일', '강수량','해상특보sp','육상특보sp']
TY_spmA.columns = ['생산일', '강수량','해상특보sp','육상특보sp']
SS_spmA.columns = ['생산일', '강수량','해상특보sp','육상특보sp']
SR_spmA.columns = ['생산일', '강수량','해상특보sp','육상특보sp']

WW_ssmA.columns = ['생산일','해상특보ss','육상특보ss']
TY_ssmA.columns = ['생산일','해상특보ss','육상특보ss']
SS_ssmA.columns = ['생산일','해상특보ss','육상특보ss']
SR_ssmA.columns = ['생산일','해상특보ss','육상특보ss']


# 데이터 프레임 합치기 일
merge_WW = pd.merge(WW_sdmA, pd.merge(WW_sfmA, WW_srmA, on='생산일', how='outer'), on='생산일', how='outer')
mWW1 = pd.merge(merge_WW, pd.merge(WW_skmA, WW_tlmA, on='생산일', how='outer'), on='생산일', how='outer')
mWW = pd.merge(mWW1, pd.merge(WW_spmA, WW_ssmA, on='생산일', how='outer'), on='생산일', how='outer')
mWW = mWW.sort_values('생산일')
mWW = mWW.reset_index(drop=True)


mWW['해상특보'].fillna('', inplace=True)
mWW['육상특보'].fillna('', inplace=True)
mWW['해상특보_x'].fillna('', inplace=True)
mWW['해상특보_y'].fillna('', inplace=True)
mWW['해상특보tl'].fillna('', inplace=True)
mWW['특보'].fillna('', inplace=True)
mWW['육상특보_x'].fillna('', inplace=True)
mWW['육상특보_y'].fillna('', inplace=True)
mWW['육상특보tl'].fillna('', inplace=True)
mWW['강수량_x'].fillna('0', inplace=True)
mWW['강수량_y'].fillna('0', inplace=True)
mWW['강수량'].fillna('0', inplace=True)
mWW['해상특보sp'].fillna('', inplace=True)
mWW['육상특보sp'].fillna('', inplace=True)
mWW['해상특보ss'].fillna('', inplace=True)
mWW['육상특보ss'].fillna('', inplace=True)

mWW['해상특보WW'] = mWW['해상특보_x'].astype(str) + mWW['해상특보_y'].astype(str) + mWW['해상특보tl'].astype(str) + mWW['해상특보'].astype(str) + mWW['해상특보sp'].astype(str) + mWW['해상특보ss'].astype(str) + mWW['특보'].astype(str)
mWW['육상특보WW'] = mWW['육상특보_x'].astype(str) + mWW['육상특보_y'].astype(str) + mWW['육상특보tl'].astype(str) + mWW['육상특보'].astype(str) + mWW['육상특보sp'].astype(str) + mWW['육상특보ss'].astype(str)
mWW['강수량WW'] = mWW['강수량_x'].astype(int) + mWW['강수량_y'].astype(int) + mWW['강수량'].astype(int)
mWW.drop(['해상특보_x', '해상특보_y', '해상특보tl','육상특보_x', '육상특보_y', '육상특보tl','특보','해상특보','육상특보','강수량_x','강수량_y','강수량','해상특보sp', '육상특보sp','해상특보ss', '육상특보ss'], axis=1, inplace=True)

##########################################################################################

merge_TY= pd.merge(TY_sdmA, pd.merge(TY_sfmA, TY_srmA, on='생산일', how='outer'), on='생산일', how='outer')
mTY1= pd.merge(merge_TY, pd.merge(TY_skmA, TY_tlmA, on='생산일', how='outer'), on='생산일', how='outer')
mTY= pd.merge(mTY1, pd.merge(TY_spmA, TY_ssmA, on='생산일', how='outer'), on='생산일', how='outer')
mTY = mTY.sort_values('생산일')
mTY = mTY.reset_index(drop=True)

mTY['해상특보'].fillna('', inplace=True)
mTY['육상특보'].fillna('', inplace=True)
mTY['해상특보_x'].fillna('', inplace=True)
mTY['해상특보_y'].fillna('', inplace=True)
mTY['해상특보tl'].fillna('', inplace=True)
mTY['특보'].fillna('', inplace=True)
mTY['육상특보_x'].fillna('', inplace=True)
mTY['육상특보_y'].fillna('', inplace=True)
mTY['육상특보tl'].fillna('', inplace=True)
mTY['강수량_x'].fillna('0', inplace=True)
mTY['강수량_y'].fillna('0', inplace=True)
mTY['강수량'].fillna('0', inplace=True)
mTY['해상특보sp'].fillna('', inplace=True)
mTY['육상특보sp'].fillna('', inplace=True)
mTY['해상특보ss'].fillna('', inplace=True)
mTY['육상특보ss'].fillna('', inplace=True)

mTY['해상특보TY'] = mTY['해상특보_x'].astype(str) + mTY['해상특보_y'].astype(str) + mTY['해상특보tl'].astype(str) + mTY['특보'].astype(str) + mTY['해상특보'].astype(str) + mTY['해상특보sp'].astype(str) + mTY['해상특보ss'].astype(str)
mTY['육상특보TY'] = mTY['육상특보_x'].astype(str) + mTY['육상특보_y'].astype(str) + mTY['육상특보tl'].astype(str) + mTY['육상특보'].astype(str) + mTY['육상특보sp'].astype(str) + mTY['육상특보ss'].astype(str)
mTY['강수량TY'] = mTY['강수량_x'].astype(int) + mTY['강수량_y'].astype(int) + mTY['강수량'].astype(int)

mTY.drop(['해상특보_x', '해상특보_y', '해상특보tl','육상특보_x', '육상특보_y', '육상특보tl','특보','해상특보','육상특보','강수량_x','강수량_y','강수량','해상특보sp', '육상특보sp','해상특보ss', '육상특보ss'], axis=1, inplace=True)

##########################################################################################

merge_SS= pd.merge(SS_sdmA, pd.merge(SS_sfmA, SS_srmA, on='생산일', how='outer'), on='생산일', how='outer')
mSS1= pd.merge(merge_SS, pd.merge(SS_skmA, SS_tlmA, on='생산일', how='outer'), on='생산일', how='outer')
mSS= pd.merge(mSS1, pd.merge(SS_spmA, SS_ssmA, on='생산일', how='outer'), on='생산일', how='outer')
mSS = mSS.sort_values('생산일')
mSS = mSS.reset_index(drop=True)

mSS['해상특보'].fillna('', inplace=True)
mSS['육상특보'].fillna('', inplace=True)
mSS['해상특보_x'].fillna('', inplace=True)
mSS['해상특보_y'].fillna('', inplace=True)
mSS['해상특보tl'].fillna('', inplace=True)
mSS['특보'].fillna('', inplace=True)
mSS['육상특보_x'].fillna('', inplace=True)
mSS['육상특보_y'].fillna('', inplace=True)
mSS['육상특보tl'].fillna('', inplace=True)
mSS['강수량_x'].fillna('0', inplace=True)
mSS['강수량_y'].fillna('0', inplace=True)
mSS['강수량'].fillna('0', inplace=True)
mSS['해상특보sp'].fillna('', inplace=True)
mSS['육상특보sp'].fillna('', inplace=True)
mSS['해상특보ss'].fillna('', inplace=True)
mSS['육상특보ss'].fillna('', inplace=True)


mSS['해상특보SS'] = mSS['해상특보_x'].astype(str) + mSS['해상특보_y'].astype(str) + mSS['해상특보'].astype(str) + mSS['해상특보tl'].astype(str) + mSS['해상특보sp'].astype(str) + mSS['해상특보ss'].astype(str)
mSS['육상특보SS'] = mSS['육상특보_x'].astype(str) + mSS['육상특보_y'].astype(str) + mSS['육상특보'].astype(str) + mSS['육상특보tl'].astype(str) + mSS['육상특보sp'].astype(str) + mSS['육상특보ss'].astype(str)
mSS['강수량SS'] = mSS['강수량_x'].astype(int) + mSS['강수량_y'].astype(int) + mSS['강수량'].astype(int)
mSS.drop(['해상특보_x', '해상특보_y','육상특보_x', '육상특보_y','특보','해상특보','육상특보','강수량_x','강수량_y', '해상특보tl', '육상특보tl','강수량_x','강수량_y','강수량','해상특보sp', '육상특보sp','해상특보ss', '육상특보ss'], axis=1, inplace=True)

##########################################################################################

merge_SR= pd.merge(SR_sdmA, pd.merge(SR_sfmA, SR_srmA, on='생산일', how='outer'), on='생산일', how='outer')
mSR1= pd.merge(merge_SR, pd.merge(SR_skmA, SR_tlmA, on='생산일', how='outer'), on='생산일', how='outer')
mSR= pd.merge(mSR1, pd.merge(SR_spmA, SR_ssmA, on='생산일', how='outer'), on='생산일', how='outer')
mSR = mSR.sort_values('생산일')
mSR = mSR.reset_index(drop=True)

mSR['해상특보'].fillna('', inplace=True)
mSR['육상특보'].fillna('', inplace=True)
mSR['해상특보_x'].fillna('', inplace=True)
mSR['해상특보_y'].fillna('', inplace=True)
mSR['해상특보tl'].fillna('', inplace=True)
mSR['특보'].fillna('', inplace=True)
mSR['육상특보_x'].fillna('', inplace=True)
mSR['육상특보_y'].fillna('', inplace=True)
mSR['육상특보tl'].fillna('', inplace=True)
mSR['강수량_x'].fillna('0', inplace=True)
mSR['강수량_y'].fillna('0', inplace=True)
mSR['강수량'].fillna('0', inplace=True)
mSR['해상특보sp'].fillna('', inplace=True)
mSR['육상특보sp'].fillna('', inplace=True)
mSR['해상특보ss'].fillna('', inplace=True)
mSR['육상특보ss'].fillna('', inplace=True)


mSR['해상특보SR'] = mSR['해상특보_x'].astype(str) + mSR['해상특보_y'].astype(str) + mSR['해상특보'].astype(str) + mSR['해상특보tl'].astype(str) + mSR['해상특보sp'].astype(str) + mSR['해상특보ss'].astype(str)
mSR['육상특보SR'] = mSR['육상특보_x'].astype(str) + mSR['육상특보_y'].astype(str) + mSR['육상특보'].astype(str) + mSR['육상특보tl'].astype(str) + mSR['육상특보sp'].astype(str) + mSR['육상특보ss'].astype(str)
mSR['강수량SR'] = mSR['강수량_x'].astype(int) + mSR['강수량_y'].astype(int) + mSR['강수량'].astype(int)
mSR.drop(['해상특보_x', '해상특보_y','육상특보_x', '육상특보_y','특보','해상특보','육상특보','강수량_x','강수량_y', '해상특보tl', '육상특보tl','강수량_x','강수량_y','강수량','해상특보sp', '육상특보sp','해상특보ss', '육상특보ss'], axis=1, inplace=True)

##########################################################################################

merge_all1= pd.merge(RD_sdmA, pd.merge(mWW, mTY, on='생산일', how='outer'), on='생산일', how='outer')
merge_all2= pd.merge(merge_all1, pd.merge(mSS, mSR, on='생산일', how='outer'), on='생산일', how='outer')
merge_all3 = pd.merge(RD_tlmA, merge_all2, on='생산일', how='outer')
merge_all = pd.merge(RD_spmA, merge_all3, on='생산일', how='outer')
merge_all = merge_all.sort_values('생산일')
merge_all = merge_all.reset_index(drop=True)
mall=merge_all


mall['강수량'].fillna('0', inplace=True)
mall['강수량_x'].fillna('0', inplace=True)
mall['강수량_y'].fillna('0', inplace=True)
mall['강수량WW'].fillna('0', inplace=True)
mall['강수량TY'].fillna('0', inplace=True)
mall['강수량SS'].fillna('0', inplace=True)
mall['강수량SR'].fillna('0', inplace=True)
#mall['강수량_x_y'].fillna('0', inplace=True)
#mall['강수량_y_y'].fillna('0', inplace=True)

mall['강수량_all'] = mall['강수량'].astype(int) + mall['강수량_x'].astype(int) + mall['강수량_y'].astype(int) + mall['강수량WW'].astype(int) + mall['강수량TY'].astype(int) + mall['강수량SS'].astype(int) + mall['강수량SR'].astype(int)
mall.drop(['강수량','강수량_x','강수량_y','강수량WW','강수량TY','강수량SS','강수량SR'], axis=1, inplace=True)

##########################################################################################



# 0을 빈문자열로 채우기
def replace_zero_with_empty(df):
    return df.replace(0, '')

mall = replace_zero_with_empty(mall)

def replace_empty_with_nan(df):
    return df.replace('', np.nan)

mall = replace_empty_with_nan(mall)

count_mall = mall.count()

#print(count_mall)

# 특정 열의 원소 개수 세기
count_day = mall['생산일'].count()
count_WW = mall['해상특보WW'].count()
count_TY = mall['해상특보TY'].count()
count_SS = mall['육상특보SS'].count()
count_SR = mall['육상특보SR'].count()
count_RD = mall['강수량_all'].count()
count_TYWW = mall[(mall['해상특보WW'].notnull()) & (mall['해상특보TY'].notnull())]['해상특보WW'].count()
count_TYSS = mall[(mall['육상특보SS'].notnull()) & (mall['해상특보TY'].notnull())]['육상특보SS'].count()
count_TYSR = mall[(mall['육상특보SR'].notnull()) & (mall['해상특보TY'].notnull())]['육상특보SR'].count()
count_WWSS = mall[(mall['해상특보WW'].notnull()) & (mall['육상특보SS'].notnull())]['해상특보WW'].count()
count_WWSR = mall[(mall['해상특보WW'].notnull()) & (mall['육상특보SR'].notnull())]['해상특보WW'].count()
count_SSSR = mall[(mall['육상특보SS'].notnull()) & (mall['육상특보SR'].notnull())]['육상특보SS'].count()
count_TYRD = mall[(mall['해상특보TY'].notnull()) & (mall['강수량_all'].notnull())]['해상특보TY'].count()
count_WWRD = mall[(mall['해상특보WW'].notnull()) & (mall['강수량_all'].notnull())]['해상특보WW'].count()
count_SSRD = mall[(mall['육상특보SS'].notnull()) & (mall['강수량_all'].notnull())]['육상특보SS'].count()
count_SRRD = mall[(mall['육상특보SR'].notnull()) & (mall['강수량_all'].notnull())]['육상특보SR'].count()
count_TYWWSS = mall[(mall['해상특보WW'].notnull()) & (mall['해상특보TY'].notnull()) & (mall['육상특보SS'].notnull())]['해상특보WW'].count()
count_TYWWSR = mall[(mall['해상특보WW'].notnull()) & (mall['해상특보TY'].notnull()) & (mall['육상특보SR'].notnull())]['해상특보WW'].count()
count_TYWWRD = mall[(mall['해상특보WW'].notnull()) & (mall['해상특보TY'].notnull()) & (mall['강수량_all'].notnull())]['해상특보WW'].count()
count_TYSSSR = mall[(mall['육상특보SS'].notnull()) & (mall['해상특보TY'].notnull()) & (mall['육상특보SR'].notnull())]['육상특보SS'].count()
count_TYSSRD = mall[(mall['육상특보SS'].notnull()) & (mall['해상특보TY'].notnull()) & (mall['강수량_all'].notnull())]['육상특보SS'].count()
count_TYSRRD = mall[(mall['육상특보SR'].notnull()) & (mall['해상특보TY'].notnull()) & (mall['강수량_all'].notnull())]['육상특보SR'].count()
count_WWSSSR = mall[(mall['해상특보WW'].notnull()) & (mall['육상특보SS'].notnull()) & (mall['육상특보SR'].notnull())]['해상특보WW'].count()
count_WWSSRD = mall[(mall['해상특보WW'].notnull()) & (mall['육상특보SS'].notnull()) & (mall['강수량_all'].notnull())]['해상특보WW'].count()
count_WWSRRD = mall[(mall['해상특보WW'].notnull()) & (mall['육상특보SR'].notnull()) & (mall['강수량_all'].notnull())]['해상특보WW'].count()
count_SSSRRD = mall[(mall['육상특보SS'].notnull()) & (mall['육상특보SR'].notnull()) & (mall['강수량_all'].notnull())]['육상특보SS'].count()
count_TYWWSSSR = mall[(mall['해상특보WW'].notnull()) & (mall['해상특보TY'].notnull()) & (mall['육상특보SS'].notnull())& (mall['육상특보SR'].notnull())]['해상특보WW'].count()
count_TYWWSSRD = mall[(mall['해상특보WW'].notnull()) & (mall['해상특보TY'].notnull()) & (mall['육상특보SS'].notnull())& (mall['강수량_all'].notnull())]['해상특보WW'].count()
count_TYWWSRRD = mall[(mall['해상특보WW'].notnull()) & (mall['해상특보TY'].notnull()) & (mall['육상특보SR'].notnull())& (mall['강수량_all'].notnull())]['해상특보WW'].count()
count_TYSSSRRD = mall[(mall['육상특보SS'].notnull()) & (mall['해상특보TY'].notnull()) & (mall['육상특보SR'].notnull())& (mall['강수량_all'].notnull())]['육상특보SS'].count()
count_WWSSSRRD = mall[(mall['해상특보WW'].notnull()) & (mall['육상특보SS'].notnull()) & (mall['육상특보SR'].notnull())& (mall['강수량_all'].notnull())]['해상특보WW'].count()
count_TYWWSSSRRD = mall[(mall['해상특보WW'].notnull()) & (mall['해상특보TY'].notnull()) & (mall['육상특보SS'].notnull()) & (mall['육상특보SR'].notnull()) & (mall['강수량_all'].notnull())]['해상특보WW'].count()

if count_day != 0:
    perWW = round(count_WW / count_day * 100, 1)
    perTY = round(count_TY / count_day * 100, 1)
    perRD = round(count_RD / count_day * 100, 1)
    perSS = round(count_SS / count_day * 100, 1)
    perSR = round(count_SR / count_day * 100, 1)
    perTYWW = round(count_TYWW / count_day * 100, 1)
    perTYSS = round(count_TYSS / count_day * 100, 1)
    perTYSR = round(count_TYSR / count_day * 100, 1)
    perTYRD = round(count_TYRD / count_day * 100, 1)
    perWWSS = round(count_WWSS / count_day * 100, 1)
    perWWSR = round(count_WWSR / count_day * 100, 1)
    perWWRD = round(count_WWRD / count_day * 100, 1)
    perSSSR = round(count_SSSR / count_day * 100, 1)
    perSSRD = round(count_SSRD / count_day * 100, 1)
    perSRRD = round(count_SRRD / count_day * 100, 1)
    perTYWWSS = round(count_TYWWSS / count_day * 100, 1)
    perTYWWSR = round(count_TYWWSR / count_day * 100, 1)
    perTYWWRD = round(count_TYWWRD / count_day * 100, 1)
    perTYSSSR = round(count_TYSSSR / count_day * 100, 1)
    perTYSSRD = round(count_TYSSSR / count_day * 100, 1)
    perTYSRRD = round(count_TYSRRD / count_day * 100, 1)
    perWWSSSR = round(count_WWSSSR / count_day * 100, 1)
    perWWSSRD = round(count_WWSSRD / count_day * 100, 1)
    perWWSRRD = round(count_WWSRRD / count_day * 100, 1)
    perSSSRRD = round(count_SSSRRD / count_day * 100, 1)
    perTYWWSSSR = round(count_TYWWSSSR / count_day * 100, 1)
    perTYWWSSRD = round(count_TYWWSSRD / count_day * 100, 1)
    perTYWWSRRD = round(count_TYWWSRRD / count_day * 100, 1)
    perTYSSSRRD = round(count_TYSSSRRD / count_day * 100, 1)
    perWWSSSRRD = round(count_WWSSSRRD / count_day * 100, 1)
    perTYWWSSSRRD  = round(count_TYWWSSSRRD / count_day * 100, 1)



print("생산일 :",count_day,"일")
print("태풍 :",count_TY,"일,", perTY,'%')
print("풍랑 :",count_WW,"일,", perWW,'%')
print("폭풍해일 :",count_SS,"일,", perSS,'%')
print("호우 :",count_SR,"일,", perSR,'%')
print("강수일 :",count_RD,"일,", perRD,'%')

print("태풍&풍랑 :",count_TYWW,"일,", perTYWW,'%')
print("태풍&폭풍해일 :",count_TYSS,"일,", perTYSS,'%')
print("태풍&호우 :",count_TYSR,"일,", perTYSR,'%')
print("태풍&강수 :",count_TYRD,"일,", perTYRD,'%')
print("풍랑&폭풍해일 :",count_WWSS,"일,", perWWSS,'%')
print("풍랑&호우 :",count_WWSR,"일,", perWWSR,'%')
print("풍랑&강수 :",count_WWRD,"일,", perWWRD,'%')
print("폭풍해일&호우 :",count_SSSR,"일,", perSSSR,'%')
print("폭풍해일&강수 :",count_SSRD,"일,", perSSRD,'%')
print("호우&강수 :",count_SRRD,"일,", perSRRD,'%')

print("태풍&풍랑&폭풍해일 :",count_TYWWSS,"일,", perTYWWSS,'%')
print("태풍&풍랑&호우 :",count_TYWWSR,"일,", perTYWWSR,'%')
print("태풍&풍랑&강수 :",count_TYWWRD,"일,", perTYWWRD,'%')
print("태풍&폭풍해일&호우 :",count_TYSSSR,"일,", perTYSSSR,'%')
print("태풍&폭풍해일&강수 :",count_TYSSRD,"일,", perTYSSRD,'%')
print("태풍&호우&강수 :",count_TYSRRD,"일,", perTYSRRD,'%')
print("풍랑&폭풍해일&호우 :",count_WWSSSR,"일,", perWWSSSR,'%')
print("풍랑&폭풍해일&강수 :",count_WWSSRD,"일,", perWWSSRD,'%')
print("풍랑&호우&강수 :",count_WWSRRD,"일,", perWWSRRD,'%')
print("폭풍해일&호우&강수 :",count_SSSRRD,"일,", perSSSRRD,'%')

print("태풍&풍랑&폭풍해일&호우 :",count_TYWWSSSR,"일,", perTYWWSSSR,'%')
print("태풍&풍랑&폭풍해일&강수 :",count_TYWWSSRD,"일,", perTYWWSSRD,'%')
print("태풍&풍랑&호우&강수 :",count_TYWWSRRD,"일,", perTYWWSRRD,'%')
print("태풍&폭풍해일&호우&강수 :",count_TYSSSRRD,"일,", perTYSSSRRD,'%')
print("풍랑&폭풍해일&호우&강수 :",count_WWSSSRRD,"일,", perWWSSSRRD,'%')

print("태풍&풍랑&폭풍해일&호우&강수 :",count_TYWWSSSRRD,"일,", perTYWWSSSRRD,'%')




