import csv
import json
import os
import time
import numpy as np
from sklearn.preprocessing import normalize
import requests
from tqdm import tqdm
from config import amap_keys, search_type, save_base_path, csv_path
from utils import st_area

api_count = 0
index_amap_keys = -1


def read_data(_csv_path: str) -> list:
    _point_data_poi = list()
    with open(_csv_path, 'r') as f:
        csv_file = csv.reader(f)
        for row in csv_file:
            _point_data_poi.append(row)
    return _point_data_poi


def generate_url(_search_keys: str, _data_list: list, _cur_page: int) -> str:
    base_url_round = "https://restapi.amap.com/v3/place/around?key={0}&location={1},{2}&radius={3}&keywords={4}" \
                     "&page={5}&offset=20&output=json&extensions=all"
    base_url_polygon = "https://restapi.amap.com/v3/place/polygon?key={0}&polygon={1}&keywords={2}&offset=20&page={" \
                       "3}&output=json&extensions=all"

    if int(_data_list[-1]) == 0:
        return base_url_round.format(amap_keys[index_amap_keys], _data_list[0], _data_list[1], _data_list[2],
                                     _search_keys, _cur_page)
    else:
        str_row = "|".join([','.join(_data_list[i:i + 2]) for i in range(0, len(_data_list) - 1, 2)])
        return base_url_polygon.format(amap_keys[index_amap_keys], str_row, _search_keys, _cur_page)


def generate_save_path(index, _save_base_path):
    save_path = os.path.join(_save_base_path, "区域" + str(index))
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    return save_path


def save_data_items(keyword, save_path, data):
    tmp_arr = list()
    with open(os.path.join(save_path, keyword + ".csv"), 'a+') as f:
        csv_file = csv.writer(f)

        for item in data['pois']:
            l = list()
            l.append(item['name'])
            l.append(item['location'])
            tmp_arr += l[1:]
            csv_file.writerow(l)
    return tmp_arr


def save_per_location_data(type_data: list, _search_type: list, save_path, _index) -> None:
    with open(os.path.join(save_path, "区域" + str(_index) + ".csv"), 'a+') as f:
        csv_file = csv.writer(f)
        for index, type in enumerate(_search_type):
            temp_array = list()
            temp_array.append(type)
            temp_array.append(type_data[index])
            csv_file.writerow(temp_array)


def caculate_convient(data: list, point_data: list, weight: list):
    data = np.array(data).astype(np.float64)
    weight = np.array(weight).astype(np.float64).reshape(-1, len(weight))
    point_data = np.array(point_data)

    for index, arr in enumerate(data):

        if int(point_data[index][-1]) == 0:
            area = (np.power(float(point_data[index][-2]) / 1000, 2) * np.math.pi)
        else:
            area = st_area(point_data[index][:-1])

        new_data = arr / area
        # print(new_data)
        data[index, :] = new_data[:]

    data = np.dot(weight, data.T).squeeze(axis=0).tolist()
    return data





def search(_search_type, _point_data_poi: list, _save_base_path, _all_type_data=None):
    global api_count, index_amap_keys
    _house_point = list()
    for index, locations in enumerate(_point_data_poi):
        save_path = generate_save_path(index, _save_base_path)
        tmp_arr = list()
        for type_index, key_word in enumerate(_search_type):
            cur_page = 0
            item_count = 0
            while True:
                if api_count % 30000 == 0:
                    index_amap_keys += 1
                url = generate_url(key_word, locations, cur_page)
                data = requests.get(url).json()

                api_count += 1
                if data['status'] != '1':
                    # 当日该key可使用量已经达到上限
                    index_amap_keys += 1
                    continue
                cur_page += 1

                print("\rcur area {}  key_word {} count {} ".
                      format(index, key_word, item_count), end='', flush=True)

                # count == 0 表明当前区域没有该类型的设施
                if int(data['count']) == 0:
                    print("\n当前区域 {0} 没有该类型 {1}".format(index, key_word))
                    break
                item_count = int(data['count'])
                tmp_arr += save_data_items(key_word, save_path, data)
                # data = json.dumps(data, indent=4, ensure_ascii=False)
                # print(data)
            if _all_type_data is not None:
                _all_type_data[index][type_index] += item_count
            # break
        _house_point.append(tmp_arr)
        print(_house_point)
        if _all_type_data is not None:
            save_per_location_data(_all_type_data[index], _search_type, save_path, index)
        print(_all_type_data)

    return _all_type_data, _house_point


def cover_house(_data_house, _search_type, _save_base_path, data_arr=None):
    global api_count, index_amap_keys
    if data_arr is None:
        data_arr = []
    base_url_round = "https://restapi.amap.com/v3/place/around?key={0}&location={1}&radius=1000&keywords={2}" \
                     "&page={3}&offset=20&output=json&extensions=all"
    for index_locations, locations in enumerate(_data_house):
        type_arr = []
        for index_house, location in enumerate(locations):
            tmp_arr = [0 for _ in range(len(_search_type))]
            for type_index, key_word in enumerate(_search_type):
                if api_count % 30000 == 0:
                    index_amap_keys += 1
                url = base_url_round.format(amap_keys[index_amap_keys], location, key_word, 0)
                data = requests.get(url).json()
                api_count += 1
                if int(data['count']) != 0:
                    tmp_arr[type_index] += 1
            type_arr.append(tmp_arr)
        print("区域 {} 覆盖率计算完成".format(index_locations))
        print(type_arr)
        data_arr.append(type_arr)
    print()
    return data_arr


def caculate_cover(_all_data_house, _search_type, _save_base_path):
    # _all_data_house = np.array(_all_data_house, dtype=np.float32)
    try:
        print("*************************************")
        print(_all_data_house)
        print("**************************************")
        result = list()
        for index, area_house_data in enumerate(_all_data_house):
            area_house_data = np.array(area_house_data)
            data_ones = np.ones([1, len(area_house_data)])
            data_temp = np.dot(data_ones, area_house_data) / len(area_house_data)
            result.append(data_temp.tolist())

        with open(os.path.join(_save_base_path, 'cover_rate.csv'), 'a+') as f:
            csv_file = csv.writer(f)
            # csv_file.writerow(_search_type)
            result = np.array(result).squeeze(axis=1)
            csv_file.writerows(result)
    finally:
        return result






# 保存便利度
def save_caculated_data(_data, _save_base_path, _point_data_poi):
    for index, location in enumerate(_point_data_poi):
        save_path = generate_save_path(index, _save_base_path)
        with open(os.path.join(save_path, str(index) + "区域便利度.csv"), 'a+') as f:
            csv_file = csv.writer(f)
            csv_file.writerow(["便利度", _data[index]])





if __name__ == '__main__':

    start = time.time()

    weight = [0.05, 0.1, 0.075, 0.025, 0.04, 0.03, 0.03, 0.08, 0.08, 0.02, 0.02, 0.105, 0.015, 0.03, 0.03, 0.04,
              0.03, 0.03, 0.02, 0.05, 0.025, 0.025, 0.025, 0.02, 0.005]

    len_search_type = len(search_type)

    if not os.path.exists(save_base_path):
        os.mkdir(save_base_path)

    point_data_poi = read_data(csv_path)

    all_type_data = [[0 for _ in range(len_search_type)] for _ in range(len(point_data_poi))]

    # # print(generate_url(0, '便利店', point_data_poi[0], 1, base_url))
    data, _ = search(search_type, point_data_poi, _save_base_path=save_base_path,
                     _all_type_data=all_type_data)

    # print("计算便利度----->")
    # data = normal(data)
    # data = caculate_convient(data, point_data_poi, weight)
    # save_caculated_data(data, save_base_path, point_data_poi)
    # print(data)
    #
    _, data_house = search(['住宅'], point_data_poi, save_base_path)

    data_cover = cover_house(data_house, search_type, save_base_path)

    print(data_house)

    print("计算覆盖率------------------------------>")
    result = caculate_cover(data_cover, search_type, save_base_path)
    print("覆盖率计算完毕--------------------------->")
    # result = np.array(result).squeeze(axis=1)
    print(result)

    end = time.time()
    print("Duraing time {}".format(end - start))