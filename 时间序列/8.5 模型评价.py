import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.stats.diagnostic import acorr_ljungbox
from math import cos, pi

# 设置 Matplotlib 参数以支持中文和负号
plt.rcParams['font.sans-serif'] = ['SimHei']  # 正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号

# 数据读取与预处理
funddata = pd.read_csv("user_balance_table.csv")
funddata['report_date'] = pd.to_datetime(funddata['report_date'], format='%Y%m%d')
combine = funddata.groupby(['report_date']).agg({'total_purchase_amt': 'sum'})

# 明确时间序列频率并填充缺失值
combine = combine.asfreq('D').fillna(method='ffill')  # 使用前向填充补全缺失值

# 平稳序列截取
smooth = combine.loc['2014-03':'2014-07']

# 模型定阶
train_results = sm.tsa.arma_order_select_ic(
    smooth.dropna(),
    ic=['bic'],
    trend='n',
    max_ar=5,
    max_ma=5
)
print('根据BIC信息准则，最佳阶数为：', train_results.bic_min_order)

# 构建与拟合ARIMA模型
p, q = train_results.bic_min_order
model = ARIMA(smooth.dropna(), order=(p, 1, q))  # 设置 d=1
results = model.fit()

# 残差分析
resid = results.resid

# 获取预测与真实值数据
predict_sunspots = results.predict(start='2014-08-01', end='2014-08-31', dynamic=False)
right_num = combine.loc['2014-08-01':'2014-08-31']

# 检查预测值与真实值索引范围
if predict_sunspots.index.equals(right_num.index):
    print("预测值与真实值索引一致，继续处理。")
else:
    print("预测值与真实值索引不一致，请检查数据！")

# 预测值和实际值
predict_array = predict_sunspots.values
right_num_array = right_num.iloc[:, 0].values


# print('predict_array:',predict_array)
# print('right_num_array:',right_num_array)

# 得到误差
error_new = np.abs(predict_array - right_num_array) / right_num_array
print("误差：", error_new)

# 得到得分
score_array = [
    5 * cos(10 * pi * error / 3) + 5 if error < 0.3 else 0
    for error in error_new
]

print("得分：", score_array)

# 绘制真实值和预测值的对比图
fig, ax = plt.subplots(figsize=(7, 4))
combine.loc['2014-08-01':'2014-08-31'].plot(ax=ax, label="真实值")
predict_sunspots.plot(ax=ax, style='r--', label="预测值")

plt.legend()
plt.title('真实值与预测值对比图')
plt.show()
