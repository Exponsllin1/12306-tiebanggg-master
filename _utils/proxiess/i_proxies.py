# -- coding: utf-8 --
# @Time : 2020/11/16 2:58
# @Author : osuoga_
# @Email: 839146079@163.com
import requests
import time


def duxiang():
    api_url = "http://kps.kdlapi.com/api/getkps?orderid=950551111078297&num=1"
    # 获取API接口返回的代理IP
    proxy_ip = requests.get(api_url).text
    print(proxy_ip)
    # 白名单方式（需提前设置白名单）
    username = ""
    password = ""
    proxies = {
        "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": proxy_ip},
        "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": proxy_ip}
    }
    # 要访问的目标网页
    target_url = "https://www.baidu.com/"

    # 使用隧道域名发送请求
    response = requests.get(target_url, proxies=proxies)

    # 获取页面内容
    if response.status_code == 200:
        print(response)
        return proxies


def suidao():
    tunnel = "tps158.kdlapi.com:15818"
    username = ""
    password = ""
    proxies = {
        "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
        "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel}
    }

    return proxies



