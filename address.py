import pandas as pd
import json

# 读取pca.csv文件，pca文件一行为一个地名，现在读取每一行，并将每一行转化为一个数组
def read_pca_csv():
    # 读取
    pca_data = pd.read_csv("pca.csv", header=None)
    # 提取pca_data第2列和第三列
    pca_data = pca_data.iloc[:, [1, 2, 3]]





    return pca_data_list

read_pca_csv()