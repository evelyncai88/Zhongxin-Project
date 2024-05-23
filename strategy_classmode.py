# -*- coding: utf-8 -*-
"""
Created on Sun Jan 23 16:46:52 2022

@author: Lenovo
"""

import tushare as ts
import pandas as pd
import numpy as np
from pandas import Series,DataFrame
import matplotlib.pyplot as plt
def get_info(ticker,start_date,end_date):
    '''
    根据股票代码、起止日期获取股票原始信息
    '''
    df=ts.get_k_data(ticker,start_date,end_date)
    df['date']=pd.to_datetime(df['date'])
    df.set_index('date',inplace=True)
    return df

def get_price(df):
    '''
    获取股票开盘价和收盘价
    '''
    return df[['open','close']]

def get_close(df):
    '''
    获取股票收盘价
    '''
    return df[['close']]

def get_moving_average(df,n):
    '''
    获取以n为参数的股票均线
    '''
    df['ma'+str(n)]=df['close'].rolling(n).mean()
    return df 

def get_total_capital(df,n1,n2,fond):
    '''
    输入带有‘ma n1’和‘ma n2’的DataFrame、n1、n2和初始现金，
    获取按照双均线策略的带有total_capital的DataFrame
    '''
    df_size=len(df)
    asset=DataFrame(data=np.random.randint(0,100,size=(df_size,1)))
    stock_num=0
    for i in range(df_size-1):
        if df['ma'+str(n1)][i]<=df['ma'+str(n2)][i] and df['ma'+str(n1)][i+1]>df['ma'+str(n2)][i+1]:
            stock_num=fond/df['close'][i]
            fond=0
        elif df['ma'+str(n1)][i]>=df['ma'+str(n2)][i] and df['ma'+str(n1)][i+1]<df['ma'+str(n2)][i+1]:
            if stock_num!=0:
                fond=stock_num*df['close'][i]
                stock_num=0
            else:
                pass
        else:
            pass
        asset.iloc[i,0]=fond+stock_num*df['close'][i]
    asset.iloc[df_size-1,0]=asset.iloc[df_size-2,0]
    df['total_capital']=[asset.iloc[i,0] for i in range(df_size)]        
    return df

df_ZTE=get_info('000063', '2010-01-01', '2021-12-31')
df_ZTE=get_close(df_ZTE)       
df_ZTE=get_moving_average(df_ZTE, 5)        
df_ZTE=get_moving_average(df_ZTE, 10)      
df_ZTE=df_ZTE.dropna(axis=0)
df_ZTE=get_total_capital(df_ZTE,5, 10, 1000000)

def performance(ticker,year,n1,n2):
    '''
    输入股票代码、需要计算的年份、均线的参数n1和n2（默认n1<n2），
    返回包含年化收益率annual_return_rate、年化波动率annual_volatility_rate
    和夏普比率Sharp_Ratio的Series
    '''
    df=get_info(ticker, year+'-01-01', year+'-12-31')
    df=get_close(df)
    df=get_moving_average(df,n1)
    df=get_moving_average(df,n2)
    df=df.dropna(axis=0)
    df=get_total_capital(df, n1, n2, 10)
    annual_return_rate=(df['total_capital'][len(df)-1]-df['total_capital'][0])/10
    df['return_ratio']=df['close']
    df['return_ratio'][0]=0
    for i in range(len(df)-1):
        df['return_ratio'][i+1]=(df['total_capital'][i+1]-df['total_capital'][i])/df['total_capital'][i]
    annual_volatility_rate=np.std(df['return_ratio'],ddof=1)*(len(df))**0.5
    SR=annual_return_rate/annual_volatility_rate
    dic={'annual_return_rate':annual_return_rate,'annual_volatility_rate':annual_volatility_rate,'Sharp_Ratio':SR}
    return Series(data=dic)

performance_ZTE=performance('000063', '2021', 5, 10)

def max_SR(ticker,year):
    '''
    输入股票代码和年份，输出当n1属于[3,5],n2属于[8,12]时Sharp_Ratio的最大值
    '''
    max_SR=DataFrame(data=np.random.randint(0,100,size=(3,5)),index=(3,4,5),columns=(8,9,10,11,12))
    for i in range(3):
        for j in range(5):
            per=performance(ticker,year,i+3,j+8)
            max_SR.iloc[i,j]=per[2]
    return max_SR

max_SR_ZTE=max_SR('000063', '2021')          

def get_info2(ticker,year,n1,n2):
    '''
    输入股票代码、年份和n1、n2，返回只有ma n1，ma n2和total_capital的DataFrame
    '''
    df=get_info(ticker, year+'-01-01', year+'-12-31')
    df=get_close(df)
    df=get_moving_average(df,n1)
    df=get_moving_average(df,n2)
    df=df.dropna(axis=0)
    df=get_total_capital(df, n1, n2, 10)
    df=df.drop(labels='close',axis=1)
    return df

def mix_performance_SR(ticker1,ticker2,ticker3,ticker4,ticker5,year,n1,n2):
    '''
    输入五个股票的代码、年份和n1、n2，得到混合投资的Sharp_Ratio
    '''
    df1=get_info2(ticker1, year, n1, n2)
    df2=get_info2(ticker2, year, n1, n2)
    df3=get_info2(ticker3, year, n1, n2)
    df4=get_info2(ticker4, year, n1, n2)
    df5=get_info2(ticker5, year, n1, n2)
    df1['total_capital_of_5']=df1['total_capital']
    for i in range(len(df1)):
        df1['total_capital_of_5'][i]=df2['total_capital'][i]+df3['total_capital'][i]
        +df4['total_capital'][i]+df5['total_capital'][i]
    per1=performance(ticker1,year,n1,n2)
    per2=performance(ticker2,year,n1,n2)
    per3=performance(ticker3,year,n1,n2)
    per4=performance(ticker4,year,n1,n2)
    per5=performance(ticker5,year,n1,n2)
    mix_annual_return_rate=(per1[0]+per2[0]+per3[0]+per4[0]+per5[0])/5
    df1['mix_return_ratio']=df1['total_capital']
    df1['mix_return_ratio'][0]=0
    for i in range(len(df1)-1):
        df1['mix_return_ratio'][i+1]=(df1['total_capital_of_5'][i+1]-df1['total_capital_of_5'][i])/df1['total_capital_of_5'][i]
    mix_annual_volatility_rate=np.std(df1['mix_return_ratio'],ddof=1)*(len(df1))**0.5
    return mix_annual_return_rate/mix_annual_volatility_rate
    
mix_SR=mix_performance_SR('000063','000550','000576','000612','002708','2021',5,10)

def mix_strategy(ticker,start_date,end_date,n1,n2,n3,fund):
    '''
    输入股票代码、起止日期、n1、n2、n3和初始现金，
    返回带有收盘价格、ma n1、ma n2、m3 n3、三个条件成立个数num
    和总资产total_capital的DataFrame
    '''
    df=get_info(ticker, start_date, end_date)
    df=get_close(df)
    df=get_moving_average(df,n1)
    df=get_moving_average(df,n2)
    df=get_moving_average(df,n3)
    df=df.dropna(axis=0)
    df_size=len(df)
    stock_num=0
    df['num']=df['close']
    for i in range(df_size):
        if df['ma'+str(n1)][i]>=df['ma'+str(n2)][i]>=df['ma'+str(n3)][i]:
            df['num'][i]=3
        elif df['ma'+str(n1)][i]<df['ma'+str(n2)][i]<df['ma'+str(n3)][i]:
            df['num'][i]=0
        elif df['ma'+str(n1)][i]>=df['ma'+str(n3)][i]>df['ma'+str(n2)][i] or df['ma'+str(n2)][i]>df['ma'+str(n1)][i]>=df['ma'+str(n3)][i]:
            df['num'][i]=2
        else:
            df['num'][i]=1
    df['total_capital']=df['close']
    df['total_capital'][0]=fund
    if df['num'][0]==3:
        stock_num=fund/df['close'][0]
        fund=0
    if df['num'][0]==2:
        stock_num=(fund/df['close'][0])*(2/3)
        fund=fund*(1/3)
    if df['num'][0]==1:
        stock_num=(fund/df['close'][0])*(1/3)
        fund=fund*(2/3)
    else:
        pass
    for i in range(df_size-1):
        if df['num'][i+1]!=df['num'][i]:
            if df['num'][i+1]==3:
                stock_num=stock_num+fund/df['close'][i]
                fund=0
            elif df['num'][i+1]==2:
                stock_num=(df['total_capital'][i]/df['close'][i])*(2/3)
                fund=df['total_capital'][i]*(1/3)
            elif df['num'][i+1]==1:   
                stock_num=(df['total_capital'][i]/df['close'][i])*(1/3)
                fund=df['total_capital'][i]*(2/3)
            else:
                fund=stock_num*df['close'][i]+fund
                stock_num=0
        else:
            pass
        df['total_capital'][i+1]=fund+df['close'][i+1]*stock_num
    return df

df_ZTE_mix=mix_strategy('000063', '2010-01-01', '2021-12-31', 5, 10, 20, 1000000)
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            