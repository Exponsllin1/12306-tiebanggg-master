# -- coding: utf-8 --
# @Time : 2021/1/16 14:41
# @Author : Los Angeles Clippers
# @Email: 229456906@qq.com
# @sinaemail: angelesclippers@sina.com
import json
import re
import time

import requests
import pickle
import random
from _utils.setting_models.setting_class import setting, USER_AGENTS
from pro_function.Chepiao_Models import MonestFunctionSeleniumSpider
from check_api_headers.api_headers import Enheaders


class CookieSVClient(object):

    def __init__(self):
        self.cookie_file = "cookied/{}_cookie".format(setting.username)


    def checkcookie(self):
        """
        cookie服务
        :return:
        """
        try:
            cookies = pickle.load(open(self.cookie_file, 'rb'))
            print('本地cookies加载成功', cookies)
            cookie_dict = {}
            for cookie in cookies:
                cookie_dict[cookie["name"]] = cookie["value"]
        except:
            print('本地cookies加载失败')
            print('正在重新登陆')
            model = MonestFunctionSeleniumSpider()
            cookie_dict = model.requests_function_login()
        return cookie_dict

    def checklogin(self, cookies):
        """
        验证cookies是否登录
        :param cookies:
        :return:
        """
        print("[init-cookieservices-checklogincookie.py]-[checklogin]-本地cookie：", cookies)
        url = 'https://kyfw.12306.cn/otn/index/initMy12306Api'
        url1 = 'https://kyfw.12306.cn/otn/modifyUser/initQueryUserInfoApi'
        url2 = 'https://kyfw.12306.cn/otn/passengers/query'
        data2 = {
            'pageIndex': '1',
            'pageSize': '10'
        }
        headers = {}
        headers['User-Agent'] = random.choice(USER_AGENTS)
        response = requests.post(url, cookies=cookies, headers=headers).text
        response1 = requests.post(url1, cookies=cookies, headers=headers).text
        response2 = requests.post(url2, cookies=cookies, data=data2, headers=headers).text
        if '_validatorMessage' in response and '_validatorMessage' in response1 and '_validatorMessage' in response2:
            print(response)
            print(response1)
            print(response2)
            print("本地登录验证成功")
            return True
        else:
            print('本地登录验证失败')
            return False

    def run(self):
        cookies = self.checkcookie()
        if self.checklogin(cookies=cookies):
            pass
        else:
            print("正在调用本地登录服务")
            model = MonestFunctionSeleniumSpider()
            cookie_dict = model.requests_function_login()
            self.run()



class ApiCookie(object):

    def cookie_api(self):
        try:
            f = open('cookied/{}_cookie.txt'.format(setting.username), encoding='utf-8')
            line = f.readlines()
            f.close()
            lin_list = []
            for item in line:
                lin_list.append(item)
            jscook = re.sub(r'\"|\'|\s|\{|\}', '', ''.join(lin_list))
            split = jscook.split(',')

            cookies = {}
            for item in split:
                s_item = item.split(':')
                cookies[s_item[0]] = s_item[1]
            return cookies

        except:
            cookies = self.get_api_cookie()
            return cookies

    def get_api_cookie(self):
        url = setting.api
        data = {
            'username': setting.username,
            'password': setting.password
        }
        en = Enheaders()
        headers = setting.api_headers
        # 加密cookie值
        ck = en.MD5(headers['Host'] + headers['Referer'] + headers['Origin']
                    + headers['User-Agent'] + headers['Authorization'])
        setting.api_headers['Cookie'] = '_token=' + ck
        response = requests.post(url, data=data, headers=setting.api_headers)
        if response.status_code == 721:
            cookies = json.loads(response.text)
            with open('cookied/{}_cookie.txt'.format(setting.username), 'w') as f:
                f.write(str(cookies))
                f.close()
            recookies = re.sub(r"\"|\'|\{|\}|\s", '', str(cookies))
            split = recookies.split(',')

            cookies = {}
            for item in split:
                s_item = item.split(':')
                cookies[s_item[0]] = s_item[1]
            return cookies
        else:
            print("服务器接口调用失败：参数异常\n即将调用本地登录服务")
            scv = CookieSVClient()
            scv.run()
            time.sleep(30)

    def checklogin_api(self, cookies):
        """
        验证cookies是否登录
        :param cookies:
        :return:
        """
        print("[init-cookieservices-checklogincookie.py]-[checklogin_api]-本地cookie：", cookies)
        url = 'https://kyfw.12306.cn/otn/index/initMy12306Api'
        url1 = 'https://kyfw.12306.cn/otn/modifyUser/initQueryUserInfoApi'
        url2 = 'https://kyfw.12306.cn/otn/passengers/query'
        data2 = {
            'pageIndex': '1',
            'pageSize': '10'
        }
        headers = {}
        headers['User-Agent'] = random.choice(USER_AGENTS)
        response = requests.post(url, cookies=cookies, headers=headers).text
        response1 = requests.post(url1, cookies=cookies, headers=headers).text
        response2 = requests.post(url2, cookies=cookies, data=data2, headers=headers).text
        if '_validatorMessage' in response and '_validatorMessage' in response1 and '_validatorMessage' in response2:
            print(response)
            print(response1)
            print(response2)
            print("服务器登录验证成功")
            return True
        else:
            print('服务器登录验证失败')
            return False

    def run(self):
        cookies = self.cookie_api()
        if self.checklogin_api(cookies=cookies):
            pass
        else:
            print("正在调用服务器登录接口")
            model = ApiCookie()
            cookie_dict = model.get_api_cookie()
            self.run()