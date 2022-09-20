import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

data = pd.read_csv("data.csv")
# print(data)

n = int(data.max(axis=0, skipna=True)[1]) + 1  # gets the number of readings
h = int(data.max(axis=0, skipna=True)[0])  # gets the number of houses

houses = np.zeros((n, 5, h))  # time, tv inst power, aggr power, filtered tv , on/off

for i in range(h):
    houses[:, 0:3, i] = data[data['House'] == i + 1].values[:, 1:]  # data is now seperated by house

# visulise data
plt.figure()
plt.suptitle('Tv power and agg power seperated ')
plt.subplot(211)
for i in range(h):
    plt.plot(houses[:, 0, i], houses[:, 1, i], label='House ' + str(i + 1))
plt.subplot(212)
for i in range(h):
    plt.plot(houses[:, 0, i], houses[:, 2, i], label='House ' + str(i + 1))
plt.legend()
# plt.show()

plt.figure()
plt.suptitle('Normalised data, shown by house')
for i in range(h):
    plt.subplot(3, 1, i + 1)
    plt.plot(houses[:, 0, i], houses[:, 1, i] / np.average(houses[:, 1, i]))
    plt.plot(houses[:, 0, i], houses[:, 2, i] / np.average(houses[:, 2, i]))
plt.legend()
plt.show()