# -*- coding: utf-8 -*-
# arima 时序模型

import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import adfuller as ADF
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.arima.model import ARIMA

# 参数初始化
discfile = 'arima_data.xls'  # 数据文件
forecastnum = 5  # 预测步数

# 读取数据，指定日期列为指标，Pandas 自动将“日期”列识别为 Datetime 格式
data = pd.read_excel(discfile, index_col='日期')

# 时序图
plt.rcParams['font.sans-serif'] = ['SimHei']  # 正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号
data.plot()
plt.title("原始数据时序图")
plt.show()

# 自相关图
plot_acf(data)
plt.title("原始数据自相关图")
plt.show()

# 平稳性检测
print('原始序列的ADF检验结果为：', ADF(data['销量']))

# 差分后的结果
D_data = data.diff().dropna()
D_data.columns = ['销量差分']
D_data.plot()
plt.title("差分后的时序图")
plt.show()
plot_acf(D_data)
plt.title("差分后的自相关图")
plt.show()
plot_pacf(D_data)
plt.title("差分后的偏自相关图")
plt.show()
print('差分序列的ADF检验结果为：', ADF(D_data['销量差分']))

# 白噪声检验
print('差分序列的白噪声检验结果为：', acorr_ljungbox(D_data, lags=[1]))  # 返回统计量和 p 值

# 定阶
data['销量'] = data['销量'].astype(float)
pmax = int(len(D_data) / 10)  # 一般阶数不超过 length/10
qmax = int(len(D_data) / 10)
bic_matrix = []  # BIC 矩阵
for p in range(pmax + 1):
    tmp = []
    for q in range(qmax + 1):
        try:
            tmp.append(ARIMA(data, order=(p, 1, q)).fit().bic)
        except:
            tmp.append(None)
    bic_matrix.append(tmp)

bic_matrix = pd.DataFrame(bic_matrix)  # 从中可以找出最小值
print(bic_matrix)

p, q = bic_matrix.stack().idxmin()  # 找出最小 BIC 值的位置
print(f'BIC最小的p值和q值为：{p}、{q}')

# 建立 ARIMA 模型
model = ARIMA(data, order=(p, 1, q)).fit()
print(model.summary())  # 输出模型报告

# 预测未来值
forecast_result = model.get_forecast(steps=forecastnum)  # 进行预测
mean_forecast = forecast_result.predicted_mean  # 预测值
conf_int = forecast_result.conf_int()  # 置信区间

# 输出结果
print("预测值：")
print(mean_forecast)
print("\n置信区间：")
print(conf_int)

# 绘制预测结果
plt.figure(figsize=(10, 6))
plt.plot(data, label='历史数据')
plt.plot(mean_forecast, label='预测值', color='red')
plt.fill_between(conf_int.index,
                 conf_int.iloc[:, 0], conf_int.iloc[:, 1],
                 color='pink', alpha=0.3, label='置信区间')
plt.legend()
plt.title("ARIMA 模型预测结果")
plt.show()
