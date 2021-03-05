# -- coding: utf-8 --
# @Time : 2021/1/17 11:53
# @Author : Los Angeles Clippers
# @Email: 229456906@qq.com
# @sinaemail: angelesclippers@sina.com

from pro_function.Chepiao_Models import MonestFunctionSeleniumSpider
from check_api_headers.api_headers import Enheaders

from flask import Flask, request

app = Flask(__name__)


@app.route("/login/12306/api/v=20210117.5352", methods=["POST", "GET"])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(request.headers)
        headers = requests_headers(request.headers['Authorization'], request.headers['Cookie'],
                                   request.headers['User-Agent'],request.headers['Host'],
                                   request.headers['Referer'])
        #  {'cokie': cookie, 'authorization': authorization, 'referer': referer, 'chrome': chrome, 'host': host}
        if headers['cookie'] == 'True' and headers['authorization'] == 'True' and \
                headers['referer'] == 'True' and headers['chrome'] == 'True' and headers['host'] == 'True':
            main = MonestFunctionSeleniumSpider(username, password)
            cookies = main.requests_function_login()
            return cookies, 721
        else:
            return "{'response': 'Fasle'}", 404
    else:
        return "{'message': '请求成功, 但不调用登录接口，参数错误！'}", 721


def requests_headers(Authorization, Cookie, UserAgent, Host, Referer):
    md5 = '08620028f72b4a69c0fb84a4b0aaa959'
    if 'Chrome' in UserAgent:
        chrome = 'True'
    else:
        chrome = 'False'
    if Host == 'www.osuoga.top':
        host = 'True'
    else:
        host = 'False'
    if Referer == 'http://www.osuoga.top/login/12306/api/v=20210117.5353':
        referer = 'True'
    else:
        referer = 'False'
    if Authorization == 'tiebanggg':
        authorization = 'True'
    else:
        authorization = 'False'
    cp = Cookie.split('=')
    if cp[0] == '_token':
        en = Enheaders()
        cp1 = en.Dbase64(en.Ebase64(cp[1]))
        if cp1 == md5:
            cookie = 'True'
        else:
            cookie = 'False'
    else:
        cookie = 'False'

    return {'cookie': cookie, 'authorization': authorization, 'referer': referer, 'chrome': chrome, 'host': host}



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7272, debug=True)
