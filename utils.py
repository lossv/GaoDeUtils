import numpy as np


from sklearn.preprocessing import normalize

# 计算多边形面积
def st_area(_point_list):
    # 弧度
    _point_list = np.array(_point_list, dtype=np.float32).reshape(-1, 2)
    # print(_point_list)
    radian = np.pi / 180.0
    # 地球半径
    radius = 6378137
    # 地球弧度
    earth_radian = radius * radian
    # 面积
    area = 0

    length = len(_point_list)
    if length < 3:
        return 0
    for index in range(0, length - 1):
        front_point = _point_list[index]
        rear_point = _point_list[index + 1]

        front_sector = front_point[0] * earth_radian * np.cos(front_point[1] * radian)
        front_line = front_point[1] * earth_radian
        rear_sector = rear_point[0] * earth_radian * np.cos(rear_point[1] * radian)
        area += (front_sector * rear_point[1] * earth_radian - rear_sector * front_line)
    wkt_rear = _point_list[length - 1]
    wkt_front = _point_list[0]
    wkt_rear_sector = wkt_rear[0] * earth_radian * np.cos(wkt_rear[1] * radian)
    wkt_rear_line = wkt_rear[1] * earth_radian
    wkt_front_sector = wkt_front[0] * earth_radian * np.cos(wkt_front[1] * radian)
    area += wkt_rear_sector * wkt_front[1] * earth_radian - wkt_front_sector * wkt_rear_line
    return 0.5 * abs(area) / 1000000


def normal(data):
    data = normalize(data, axis=0, norm='max')
    return data