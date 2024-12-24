# coding: utf-8

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.stats.diagnostic import acorr_ljungbox

plt.rcParams['font.sans-serif'] = ['SimHei']  # 正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号

# 数据读取与预处理
funddata = pd.read_csv("user_balance_table.csv")
funddata['report_date'] = pd.to_datetime(funddata['report_date'], format='%Y%m%d')
combine = funddata.groupby(['report_date']).agg({'total_purchase_amt': 'sum'})

# 明确时间序列频率
combine = combine.asfreq('D')  # 假设为每日频率，具体根据实际情况修改

# 平稳序列截取
smooth = combine['2014-03':'2014-07']

# 模型定阶
train_results = sm.tsa.arma_order_select_ic(smooth.dropna(), ic=['bic'], trend='n', max_ar=5, max_ma=5)
print('根据BIC信息准则，最佳阶数为：', train_results.bic_min_order)

# 构建与拟合ARIMA模型
p, q = train_results.bic_min_order
model = ARIMA(smooth.dropna(), order=(p, 1, q))
results = model.fit()

# 残差分析
resid = results.resid
plt.figure(figsize=(12, 8))

# 绘制残差ACF图
plt.subplot(2, 1, 1)
plot_acf(resid.values.squeeze(), lags=40, ax=plt.gca())
plt.title('残差自相关图')

# 绘制残差PACF图
plt.subplot(2, 1, 2)
plot_pacf(resid.values.squeeze(), lags=40, ax=plt.gca())
plt.title('残差偏自相关图')

plt.tight_layout()
plt.show()

# 白噪声检验
ljungbox_results = acorr_ljungbox(resid.values.squeeze(), lags=10)
print('差分序列的白噪声检验结果：')
print(pd.DataFrame({
    '滞后阶数': list(range(1, len(ljungbox_results) + 1)),
    '统计量': ljungbox_results['lb_stat'],
    'p值': ljungbox_results['lb_pvalue']
}))

# 输出模型摘要
print(results.summary())
