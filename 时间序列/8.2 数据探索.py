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
print(combine)

combine.plot(legend=False) 
plt.title('时序图')
plt.show()
plot_acf(combine)
plt.title('自相关图')
plt.show()
