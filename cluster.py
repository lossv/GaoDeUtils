import csv
import os
import pandas as pd

if __name__ == '__main__':
    # search_type = ['便利店', '连锁超市', '农贸市场', '百货市场，购物中心', '幼儿园', '小学', '中学', '快餐', '中国餐馆',
    #                '外国餐馆', '休闲餐饮', '地铁站点', '公交车站', '停车场', '诊所', '综合医院', '药店', '美容美发', '维修护理',
    #                '物流服务', 'ATM', '银行', '游乐场所', '影院', '体育场馆，文化艺术']

    search_type = ['日常购物', '教育设施', '餐饮设施', '交通设施', '医疗设施', '便名服务', '金融服务', '休闲娱乐']
    # cluster_data = {
    #     '日常购物': ['便利店', '连锁超市', '农贸市场', '百货市场，购物中心'],
    #     '教育设施': ['幼儿园', '小学', '中学'],
    #     '餐饮设施': ['中国餐馆', '外国餐馆', '休闲餐饮'],
    #     '交通设施': ['地铁站点', '公交车站', '停车场'],
    #     '医疗设施': ['诊所', '综合医院'],
    #     '便名服务': ['美容美发', '维修护理', '物流服务'],
    #     '金融服务': ['ATM', '银行'],
    #     '休闲娱乐': ['游乐场所', '影院', '体育场馆，文化艺术']
    # }
    # cluster_data = {
    #     '住宅': ['小区']
    # }
    # ['养老院', '福利院', '敬老院']
    cluster_data = {
        '养老院': ['养老院'],
        '福利院': ['福利院'],
        '敬老院': ['敬老院']
    }

    base_dir = 'tmp_data'
    save_dir = 'tmp_data/eight_cluster'

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for i in cluster_data.keys():
        save_file_path = os.path.join(save_dir, i + '.csv')
        with open(save_file_path, 'w') as f:
            for item in cluster_data[i]:
                for j in range(15):
                    type_dir_path = os.path.join(base_dir, '区域{}'.format(j), '{}.csv'.format(item))
                    csv_file_save = csv.writer(f)
                    if os.path.exists(type_dir_path):
                        with open(type_dir_path, 'r') as type_f:
                            csv_file_reader = csv.reader(type_f)
                            temp_data = list()
                            for row in csv_file_reader:
                                temp_data.append(row)
                            csv_file_save.writerows(temp_data)

    print(save_dir)

    file_list = os.listdir(save_dir)
    print(file_list)
    for i in os.listdir(save_dir):
        csv_file_path = os.path.join(save_dir, i)
        print(csv_file_path)
        if csv_file_path == 'tmp_data/eight_cluster/福利院.csv':
            continue
        csv_read = pd.read_csv(csv_file_path)
        csv_read.drop_duplicates()
        csv_read.to_csv(csv_file_path, index=False, header=['名称', '经纬度'], encoding='UTF-8')
