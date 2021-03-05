# -- coding: utf-8 --

import requests
import json
import re
from openpyxl import workbook
import random

from _utils.setting_models.setting_class import variable, getztid, USER_AGENTS

def decrypt(string):
    """
    处理字符串
    :param string:
    :return:
    """
    # 定义正则表达式提取规则
    reg1 = re.compile('.*?\|预订\|.*?\|(.*?)\|(.*?)\|(.*?)\|.*?\|.*?\|(.*?)\|(.*?)\|(.*?)\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|.*?\|.*?\|.*?\|.*')
    reg2 = re.compile('.*?\|.*?起售\|.*?\|(.*?)\|(.*?)\|(.*?)\|.*?\|.*?\|(.*?)\|(.*?)\|(.*?)\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|.*?\|.*?\|.*?\|.*')
    reg3 = re.compile('.*?\|.*?停运\|.*?\|(.*?)\|(.*?)\|(.*?)\|.*?\|.*?\|(.*?)\|(.*?)\|(.*?)\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|.*?\|.*?\|.*?\|.*')
    reg4 = re.compile('.*?\|.*?暂停发售\|.*?\|(.*?)\|(.*?)\|(.*?)\|.*?\|.*?\|(.*?)\|(.*?)\|(.*?)\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|.*?\|.*?\|.*?\|.*')
    # 因网站存在三种状态的列车信息，所以使用try语句进行处理。

    try:
        result = re.findall(reg1,string)[0]
    except IndexError as e:
        try:
            result = re.findall(reg2, string)[0]
        except:
            try:
                result = re.findall(reg3, string)[0]
            except:
                result = re.findall(reg4, string)[0]
    return result


def getchepiaoinfo(city_id_dict, cookies):
    """
    获取列车信息并保存至本地。
    :param city_id_dict:
    :return:
    """
    # 通过抓包可知车次信息为请求如下地址得到
    url = "https://kyfw.12306.cn/otn/leftTicket/queryZ?"
    # 构造form表单
    params = {
        'leftTicketDTO.train_date': variable.date,
        'leftTicketDTO.from_station': city_id_dict[variable.cfc],
        'leftTicketDTO.to_station': city_id_dict[variable.ddc],
        'purpose_codes': 'ADULT',
    }
    print(params)
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'kyfw.12306.cn',
        'If-Modified-Since': '0',
        'Pragma': 'no-cache',
        'sec-ch-ua': '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie': '_uab_collina=161062575272433666449274; JSESSIONID=3A1166990741727AACF14A49C5B17BAC; _jc_save_wfdc_flag=dc; BIGipServerotn=1675165962.24610.0000; BIGipServerpassport=1005060362.50215.0000; RAIL_EXPIRATION=1611412406714; RAIL_DEVICEID=M-m9YLeHdsV_0Or8kSn6m3GT6i4HW3VtaHbWkEt47bvFULgjp3TMg6bW_qCs3WycoajUUvYKvuSCs4CQtOtgYRyMt5hK2y_Cipm_HWeSU_e0807PIVcve2mdkOqjRq2uN0kIXdM9WFNCe4EO7rxvFFi_bUO27-ZQ; route=9036359bb8a8a461c164a04f8f50b252; _jc_save_fromStation=%u5317%u4EAC%2CBJP; _jc_save_toStation=%u5E7F%u5DDE%2CGZQ; _jc_save_toDate=2021-01-20; _jc_save_fromDate=2021-01-22'
    }
    headers['User-Agent'] = random.choice(USER_AGENTS)
    response = requests.get(url=url, params=params, headers=headers, timeout=5)
    print(response.status_code)
    try:
        secretStr, bgs = parms_index(response.text, city_id_dict)
        ip_bp = [0]  # 判断ip是否被检查
        return secretStr, bgs, ip_bp
    except json.decoder.JSONDecodeError as e:
        print("ip 被限制: requests_12306_spiders.py-[getchepiaoinfo]-error--->", e)
        ip_bp = [1]  # 判断ip是否被检查
        secretStr, bgs = [], []
        return secretStr, bgs, ip_bp


def parms_index(response, city_id_dict):
    # 请求到的数据使用json来进行处理
    # print(response)
    jsdata = json.loads(response)['data']['result']

    secretStr = []      # 存放待定购车次信息
    bgs = []            # 判断所选车次是否存在
    contents = []
    spietm = []              # 存放列车各个信息列表
    read_id = {}
    for k, v in city_id_dict.items():
        read_id[v] = k
    # 获取车次详情信息，并保存至本地
    for item in jsdata:
        # break
        result = list(decrypt(item))
        result[1] = variable.cfc
        result[2] = variable.ddc
        # 构建content列表，用于存放列车信息
        content = [result[0], read_id[item.split('|')[6]], read_id[item.split('|')[7]], result[3],
                   result[4], result[5], result[-1], result[-2], result[-3], item.split('|')[21],
                   result[-10], result[8], result[-5], result[9], result[-4], result[-7], result[-6]]
        if variable.time in content:
            print(item.split('|'))
            spietm.append(item.split('|'))
            contents.append(item)

            print(content)
    if variable.time in contents[0]:        # 未考虑其他车型和高铁同一时间的情况，待改进
        bgs.append('True')
        if spietm[0][variable.seat[variable.zwtype]] == '有':
            print(contents[0].split('|'))
            secretStr.append(contents[0])
        else:
            try:
                zws = int(spietm[0][variable.seat[variable.zwtype]])
                print(contents[0].split('|'))
                secretStr.append(contents[0])
            except:
                print("您当前选购的车次[{}]从[{}]到[{}] [{} {}]出发无[{}]，正在重试。".
                      format(contents[0].split('|')[3], read_id[contents[0].split('|')[6]], read_id[contents[0].split('|')[7]],
                             variable.date, variable.time, variable.zwtype))
    else:
        bgs.append('False')
        print("您当前选购从[{}]到[{}] [{} {}]出发的车次无信息或已停售，请确认是否填写正确后重试。".
              format(variable.cfc, variable.ddc, variable.date, variable.time))

    return secretStr, bgs


def spider_main(cookies):
    # 主函数，程序运行入口
    city_id_dict =  getztid(cookies)
    secretStr, bgs, ip = getchepiaoinfo(city_id_dict=city_id_dict, cookies=cookies)
    return secretStr, bgs, ip


if __name__ == '__main__':
    # spider_main()
    pass