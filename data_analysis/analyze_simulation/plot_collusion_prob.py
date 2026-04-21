import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

n = 100

x = np.linspace(0,1,11)
x_share = x*n

y = x_share/(n-1) * ((x_share-1)/(n-2))

print("X: ", x_share)
print("Y: ", y)

plt.plot(x_share, y, 'x')

n = 100

x_share = x*n
y = x_share/(n-1) * ((x_share-1)/(n-2))
plt.xlabel("Malicious share x")
plt.ylabel("coll prob: (x/(n-1))*((x-1)/(n-2))")
plt.plot(x_share, y, 'o')

plt.show()