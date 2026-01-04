import random
import matplotlib.pyplot as plt

# 1. 生成数据
low, high, mode = 0.1, 0.7, 0.4
samples = [random.triangular(low, high, mode) for _ in range(1000)]

# 2. 画图
plt.figure(figsize=(6, 4))
plt.hist(samples, bins=50, density=True, alpha=0.7, color='steelblue', edgecolor='black')
plt.title(f'Triangular distribution\nlow={low}  high={high}  mode={mode}')
plt.xlabel('Value')
plt.ylabel('Density')
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()