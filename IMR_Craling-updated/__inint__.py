# -*- coding: utf-8 -*-
# author: ZJendex
# place: Boston Amherst
# last update:
from requests_html import HTMLSession
import numpy as np
import netCDF4 as nc
from geopy.geocoders import Nominatim


def is_number(s):
    try:  # 如果能运行float(s)语句，返回True（字符串s是浮点数）
        float(s)
        return True
    except ValueError:  # ValueError为Python的一种标准异常，表示"传入无效的参数"
        pass  # 如果引发了ValueError这种异常，不做任何事情（pass：不做任何事情，一般用做占位语句）
    try:
        import unicodedata  # 处理ASCii码的包

        unicodedata.numeric(s)  # 把一个表示数字的字符串转换为浮点数返回的函数
        return True
    except (TypeError, ValueError):
        pass
    return False


def main():
    # 建立一个会话（session）
    session = HTMLSession()

    # 获取网页内容，html格式的
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_infant_and_under-five_mortality_rates"
    r = session.get(url)

    text = r.html.text
    # 筛数据锁
    f = True
    # 跳过第一个
    fir = True
    # 存数据的map
    c_map = {}
    country_name = ""
    for t in text.split("\n"):
        if t == "2019 mortality rate, under-5 (per 1000 live births)":
            f = False
        if t == "OECD. Under-five mortality from the World Bank[edit]":
            f = True
        if not f:
            # 有用数据
            if not fir:
                if country_name == "":
                    country_name = t.split("\u202f")[0]
                else:
                    c_map[country_name.upper()] = t  # 加了个Upper，方便后期compare
                    country_name = ""
            fir = False
    c_map_copy = c_map.copy()
    c_map = sorted(c_map.items(), key=lambda x: float(x[1]), reverse=True)
    # print(c_map)

    import csv

    with open(
        "IMR_WorldWide.csv", "w", encoding="utf-8"
    ) as f:  # You will need 'wb' mode in Python 2.x
        csv_out = csv.writer(f)
        csv_out.writerow(["country_name", "IMR(per 1000 five-years-old children)"])
        for row in c_map:
            csv_out.writerow(row)

    datasets = [
        nc.Dataset("MERRA2_400.tavgM_2d_lnd_Nx.202108.nc4", "r")
    ]  # Change to support multiple files

    # Just a constant look up table
    var_to_use = [
        "TSOIL1",
        "TSOIL2",
        "TSOIL3",
        "TSOIL4",
        "TSOIL5",
        "TSOIL6",
        "LHLAND",
        "Var_LHLAND",
        "PRECSNOLAND",
        "Var_PRECSNOLAND",
        "PRMC",
        "Var_PRMC",
        "QINFIL",
        "Var_QINFIL",
        "SMLAND",
        "Var_SMLAND",
    ]
    # A data structure to be mapped by a country
    varmap = {key: [] for key in var_to_use}  # {var_to_use : [] # parrallel file list}
    coun_varmap = {country: varmap for country in c_map_copy.keys()}

    # initialize Nominatim API
    geolocator = Nominatim(user_agent="geoapiExercises")

    for dataset in datasets:
        lon_list = dataset.vairables["lon"][...]
        lat_list = dataset.variables["lat"][...]

        np_obj_lis = {
            var_name: np.array(dataset.variables[var_name]).reshape(361, 576)
            for var_name in var_to_use
        }

        for i in range(len(lat_list)):
            for j in range(len(lon_list)):
                location = geolocator.reverse(lat_list[i] + "," + lon_list[j])
                address = location.raw["address"]
                country_name = address.get("country", "")
                country_name = country_name.upper()
                if country_name in c_map_copy:
                    for var in np_obj_lis:
                        coun_varmap[country_name][var] = np_obj_lis[var][i][j]

    print(coun_varmap["CHINA"])


if __name__ == "__main__":
    main()
