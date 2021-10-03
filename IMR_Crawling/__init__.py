# -*- coding: utf-8 -*-
# author: ZJendex
# place: Boston Amherst
# last update:  
from requests_html import HTMLSession

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
    url = 'https://en.wikipedia.org/wiki/List_of_countries_by_infant_and_under-five_mortality_rates'
    r = session.get(url)

    text = r.html.text
    # 筛数据锁
    f = True
    # 跳过第一个
    fir = True
    # 存数据的map
    map = {}
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
                    map[country_name] = t
                    country_name = ""
            fir = False

    map = sorted(map.items(), key=lambda x: float(x[1]), reverse=True)
    print(map)

    import csv

    with open('IMR_WorldWide.csv', 'w', encoding='utf-8') as f:  # You will need 'wb' mode in Python 2.x
        csv_out = csv.writer(f)
        csv_out.writerow(['country_name', 'IMR(per 1000 five-years-old children)'])
        for row in map:
            csv_out.writerow(row)


if __name__ == '__main__':
    main()
