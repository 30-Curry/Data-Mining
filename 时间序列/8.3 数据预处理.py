# coding: utf-8


from math import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from pylab import *
# 时序图
plt.rcParams['font.sans-serif'] = ['SimHei']  # 正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号

funddata = pd.read_csv("user_balance_table.csv")
# 将目标列读取为日期型
funddata['report_date'] = pd.to_datetime(funddata['report_date'], format='%Y%m%d')

# 对相同日期的资金申购量进行统计
combine = funddata.groupby(['report_date']).agg({'total_purchase_amt': sum})

# 截取平稳部分数据
smooth = combine['2014-3':'2014-7']  
# print(smooth)
smooth .plot(legend=False)  # 截取数据的时序图
plt.title('截取数据时序图')
plt.show()  # 截取的训练数据自相关图
plot_acf(smooth )
plt.title('截取数据自相关图')
plt.show()



# 周期性差分
diffresult = smooth .diff(7)
diffresult.plot(legend=False)
diffresult = diffresult['2014-03-08':'2014-07-31']  # 需要进行数据的提取
plt.title('差分时序图')
plt.show()  # 差分时序图
plot_acf(diffresult)  # 差分数据自相关图
plt.title('差分自相关图')
plt.show()



# ADF检验
from statsmodels.tsa.stattools import adfuller as ADF
print('差分序列的ADF检验结果为：\n', ADF(diffresult))
# 白噪声检验
from statsmodels.stats.diagnostic import acorr_ljungbox
print('差分序列的白噪声检验结果为：\n', acorr_ljungbox(diffresult, lags=1))

