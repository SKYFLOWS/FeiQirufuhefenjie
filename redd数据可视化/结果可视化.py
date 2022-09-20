#结果可视化
import pandas as pd
import matplotlib.pyplot as plt
from analyse import result,electrical


res=pd.concat(result)
res.to_csv("result.csv",index=None)
plt.figure(figsize=(15,8))
#根据类型和小时聚合
total=res.groupby(["dev_type","hours"]).sum()


'''折线图'''
marker=['-.','+-','*-','p-','>-','X-','s-']
for e,m in zip(electrical,marker):
    temp=total.loc[(e)]
    plt.plot(temp.index,temp.switch,m,label=e)
    x_major_locator=plt.MultipleLocator(1)
    ax=plt.gca()
    #ax为两条坐标轴的实例
    ax.xaxis.set_major_locator(x_major_locator)
    plt.ylabel("开启总次数")
    plt.xlabel("小时")
    plt.legend()
plt.xlim(0,48)
plt.show()

'''柱状图'''
plt.figure(figsize=(15,8))
for e in electrical:
    temp=total.loc[(e)]
    plt.bar(temp.index,temp.switch,label=e)
    x_major_locator=plt.MultipleLocator(1)
    ax=plt.gca()
    #ax为两条坐标轴的实例
    ax.xaxis.set_major_locator(x_major_locator)
    plt.ylabel("开启总次数")
    plt.xlabel("小时")
    plt.legend()
    plt.show()

'''统计每个用户一天中不同时间段的用电频率'''
user_df = res[res["dev_type"] != "总"]
users = list(user_df.user.unique())
frequency = []
plt.figure(figsize=(24, 10))
count = 1
# 遍历6个用户,每个用户绘制一张子图
for user in users:
    temp = user_df[user_df["user"] == user]
    plt.subplot(2, 3, count)
    # 遍历该用户的各个电器，用于绘制曲线
    for d in list(temp.dev_type.unique()):
        dev = temp[temp["dev_type"] == d]
        total = dev['switch'].sum()  # 该电器在所有时段的开启次
        if total != 0:
            dev['switch'] /= total
        plt.plot(dev.hours, dev.switch, label=d)

    plt.title("{}电器各时间段使用频率".format(user))
    plt.legend()
    plt.xlabel("/半小时")
    plt.ylabel("使用频率")
    count += 1
plt.show()


