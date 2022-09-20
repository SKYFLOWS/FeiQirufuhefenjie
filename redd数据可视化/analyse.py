import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import re
import warnings
import seaborn as sns
import itertools
warnings.filterwarnings("ignore")
plt.rcParams['font.sans-serif']='SimHei'
plt.rcParams['axes.unicode_minus']=False


#一.合并数据
#读表获取每个房间的设备信息
#只分析洗衣机、洗碗机、微波炉、电烤箱、电暖气、电炉、空调、空气处理装
root=os.path.abspath("low_freq.csv")
users=os.listdir(root)
io = pd.io.excel.ExcelFile("新redd设备信息.xlsx")
#获取每个房间的设备型号,key为房间号，value为设备名称、设备号的dataframe
devices_df={}
for i in range(1,7):
    device=pd.read_excel(io, sheet_name='房间'+str(i))
    device=device[device["设备名称"].str.contains("洗衣机|洗碗机|微波炉|电烤箱|电暖气|电炉|空调|空气处理装置")]
    name="building"+str(i)
    devices_df[name]=device
io.close()
print('devices_df["building1"]示例数据结构如下:')



#合并所有表格
#在原有基础上添加三列：
       #所属用户user
       #设备类型dev_type
       #开关状态 statu
all_df = []
for user in users:
    print("\n==========正在合并%s的信息=========" % user)
    excels = os.path.join(root, os.path.join(user, "elec"))
    file_path = os.path.join(root, excels)
    for file in os.listdir(file_path):
        # 匹配文件名的数字，判断是否是我们需要分析的电器
        the_type = int(re.findall("meter(.*).csv", file)[0])
        if the_type not in list(devices_df[user]["设备号"]) or the_type == 2:
            continue
        print(file, "正在合并meter", the_type)
        # 当前用户的家电使用情况信息
        excel = os.path.join(file_path, file)
        df = pd.read_csv(excel)[1:]
        length = len(df)

        # 新增user列
        df["user"] = [user] * length
        # 获取设备号对应的设备名称
        # 当不存在该电器时，跳过
        try:
            df["dev_type"] = [devices_df[user].loc[devices_df[user]["设备号"] == the_type, "设备名称"].values[
                                  0]] * length
            # 新增status列1为运行状态，0为非运行状态
            start_power = devices_df[user].loc[devices_df[user]["设备号"] == the_type, "家电开启功率阈值/W"].values[0]
            df['status'] = df['power'].apply(lambda x: 1 if float(x) > 10 else 0)
            # 最短开启时间 开启的最短运行时间/s
            df['open_time'] = [devices_df[user].loc[
                                   devices_df[user]["设备号"] == the_type, "开启的最短运行时间/s"].values[0]] * length
            # 最短关闭时间 关闭的最短运行时间/s
            df['shut_time'] = [devices_df[user].loc[
                                   devices_df[user]["设备号"] == the_type, "关闭的最短运行时间/s"].values[0]] * length
            all_df.append(df)
        except:
            continue

print("合并所有building的信息...")
data = pd.concat(all_df)
data.head()

#数据清洗
#1、physical_quantity重命名为time
#2、由于time列的都以04:00结尾，由此去掉这一部分，并将该列转换为时间序列
#3、将time时间序列设置为索引列
data.rename(columns={"physical_quantity":"time"},inplace=True)
data.time=data.time.str.replace("-04:00","")
data.time=pd.to_datetime(data.time)
data=data.set_index("time")
data.head()
data['power'].astype('float').plot(figsize=(12,8),title="用电功率天数统计")#查看数据
#plt.show()

#开关状态判断
#对于读取的状态数据（1为运行，0为关闭），将数据与最小开启/关闭时间作判断，更正误判状态
#将状态值进行差分，差分结果0为运行，非0值统计为1，代表一次开关状态
def judge_status(data):
    count=0
    last=0
    for k,v in itertools.groupby(data['status']):
        #连续相等值长度
        sequence=len(list(v))

        #获取该段数据
        temp=data.iloc[last:count,]
        if len(temp)==0:
            continue
        delta=(temp.index[-1]-temp.index[0]).seconds
        #判断当前开关状态
        if k==1:
            #如果开状态小于设定值，修改这部分状态为关闭
            if delta<temp['open_time'][0]:
                data[count:sequence:,]=0
        elif k==0:
             if delta<temp['shut_time'][0]:
                data[count:sequence:,]=1
        count+=sequence
    data['diff']=data['status'].diff().fillna(0)
    data['diff']=data['diff'].apply(lambda x:1 if x!=0 else 0 )

#用电时间段频率统计(时间序列聚合)
#将所有用户时间汇总，聚合每半小时的数据，开关次数（记录条数）
#汇总6张表（对应6个用户，每张表48条数据对应一天中的各个半小时）
result=[]
electrical=data.dev_type.unique()
for user in users:
    for e in electrical:
        print("\r正在计算{}:{}".format(user,e),end=" ")
        #按半小时聚合
        half_data=data[(data["user"]==user) & (data["dev_type"]==e)]
        #如果不存在，就跳过
        if len(half_data)==0:
            continue
        judge_status(half_data)
        hour_agg=half_data.resample("0.5H").sum()

        user_names=[]
        switches=[]
        hours=[]
        types=[]
        for hour in range(48):
            h=int(hour/2)
            m=(hour%2*30)
            temp=hour_agg[(hour_agg.index.hour==h) & (hour_agg.index.minute==m)]
            switch=temp['diff'].sum()
            switches.append(switch)
            types.append(e)
            user_names.append(user)
            hours.append(hour)
        add_df=pd.DataFrame({
            "switch":switches,
            "user":user_names,
            "dev_type":types,
            "hours":hours
        })
        result.append(add_df)
print("\n计算完成！")




