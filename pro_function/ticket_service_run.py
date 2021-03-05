# -- coding: utf-8 --
import json
import pickle
import re
import time
import random
import requests
import smtplib
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from pro_function.requests_12306_spiders import spider_main
from pro_function.qiangpiao_xiadan import main
from pro_function.Chepiao_Models import MonestFunctionSeleniumSpider
from _utils.setting_models.setting_class import setting, USER_AGENTS
from init.cookieservices.checklogincookie import ApiCookie


class Ticket_Service_Client(object):

    def checklogin(self, cookies):
        """
        验证cookies是否登录
        :param cookies:
        :return:
        """
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
            return True
        else:
            print('登录验证失败')
            return False

    def getcookies(self):
        """
        获取cookie
        :return:
        """
        try:
            cookies = pickle.load(open("cookied/{}_cookie".format(setting.username), 'rb'))
            print('[tcket-service-run]-[getcookies]-本地cookies加载成功', cookies)
            cookie_dicts = {}
            for cookie in cookies:
                cookie_dicts[cookie["name"]] = cookie["value"]
            if self.checklogin(cookies=cookie_dicts):
                print('[tcket-service-run]-[getcookies]-本地cookies验证成功', cookies)
                cookie_dict = cookie_dicts
            else:
                print('[tcket-service-run]-[getcookies]-本地cookies验证失败')
                print('正在重新登陆')
                model = MonestFunctionSeleniumSpider()
                cookie_dict = model.requests_function_login()
        except:
            print('[tcket-service-run]-[getcookies]-本地cookies读取失败')
            print('正在重新登陆')
            model = MonestFunctionSeleniumSpider()
            cookie_dict = model.requests_function_login()
        return cookie_dict

    def cookie_api(self):
        """
        获取服务器cookie
        :return:
        """
        try:
            f = open('cookied/{}_cookie.txt'.format(setting.username), encoding='utf-8')
            line = f.readlines()
            f.close()
            lin_list = []
            for item in line:
                lin_list.append(item)
            jscook = re.sub(r'\'|\s|\{|\}|"', '', ''.join(lin_list))
            split = jscook.split(',')

            cookies = {}
            for item in split:
                s_item = item.split(':')
                cookies[s_item[0]] = s_item[1]
            print(cookies)
            print('[tcket-service-run]-[cookie_api]-本地cookies读取成功')
            if self.checklogin(cookies=cookies):
                print('[tcket-service-run]-[cookie_api]-本地cookies验证成功', cookies)
                cookie_dict = cookies
            else:
                print('[tcket-service-run]-[cookie_api]-本地cookies验证失败')
                print('正在重新登陆')
                model = ApiCookie()
                cookie_dict = model.get_api_cookie()
            return cookie_dict

        except:
            print('[tcket-service-run]-[cookie_api]-本地cookies读取失败')
            print('正在重新登陆')
            model = ApiCookie()
            cookie_dict = model.get_api_cookie()
            return cookie_dict

    def Email_Client(self, playinfo):
        """
        发送购票付款码及购票信息到邮箱
        :return:
        """
        # 发送邮箱服务器
        playaddress = '付款地址[https://kyfw.12306.cn/otn/view/train_order.html]'
        smtpserver = 'smtp.163.com'
        # 发送邮箱用户名密码
        users = setting.email_user
        password = setting.email_pwd
        # 发送和接收邮箱
        receives = [setting.email_to, users]

        msg = MIMEMultipart()  # 创建一个带附件的实例
        subject = Header('您的12306购票信息', 'utf-8').encode()
        msg["Subject"] = subject  # 指定邮件主题
        msg["From"] = users  # 邮件发送人
        msg["To"] = ','.join(receives)
        msg.attach(MIMEText('您的购票信息：{}，请查收!本次订单在30分钟内有效，请注意付款时间！'
                            '您可以使用支付宝扫描附件中的付款码进行购票或者请移步：{}进行付款购买。'.
                            format(playinfo, playaddress), _subtype='html', _charset='utf-8'))

        try:
            pngpath = 'pro_function/images/play_erweima.png'
            part = MIMEApplication(open(pngpath, 'rb').read())
            part.add_header('Content-Disposition', 'attachment', filename=pngpath)
            msg.attach(part)

            s = smtplib.SMTP(smtpserver, timeout=30)  # 连接smtp邮件服务器,端口默认是25
            s.login(users, password)  # 登陆服务器
            s.sendmail(users, receives, msg.as_string())  # 发送邮件
            s.close()
            print('------->邮件发送成功', '已发送{}的购票二维码到{}！'.format(playinfo[2], setting.email_to))
            print('------->success')
        except Exception as e:
            print("------->send email error:" + str(e))

            print('------->错误', '请检查邮箱地址是否正确！并重新查询后再次发送邮件。')
        print("已为您完成抢票！程序将自动关闭。")

    def MIMETexts(self, playinfo):
        """
        发送购票信息到邮箱
        :param playinfo:
        :return:
        """
        playaddress = '，付款地址[https://kyfw.12306.cn/otn/view/train_order.html]'
        fromaddr = setting.email_user  # 邮件发送方邮箱地址    #DHSENJMFFAVKXBEJ
        password = setting.email_pwd  # 密码(部分邮箱为授权码)
        # 发送和接收邮箱
        toaddrs = [setting.email_to, fromaddr]  # 邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发

        data = str(playinfo) + playaddress
        message = MIMEText(str(data), 'plain', 'utf-8')
        message['Subject'] = '{}的12306购票通知'.format(playinfo[2])
        message['From'] = fromaddr
        message['To'] = ','.join(toaddrs)
        try:
            server = smtplib.SMTP('smtp.163.com')  # 163邮箱服务器地址，端口默认为25
            server.login(fromaddr, password)
            server.sendmail(fromaddr, toaddrs, message.as_string())
            server.quit()
            print('------->邮件发送成功', '已发送{}的购票二维码到{}！'.format(playinfo[2], setting.email_to))
            print('------->success')
        except Exception as e:
            print("------->send email error:" + str(e))
            print('------->错误', '请检查邮箱地址是否正确！并重新查询后再次发送邮件。')
            print("已为您完成抢票！程序将自动关闭。")

    def start_main(self, list_getnum):
        """
        主函数：工程入口    requests请求抢购
        """
        global cookies
        if setting.apitype == 'api':
            cookies = self.cookie_api()
        else:
            cookies = self.getcookies()
        i = 0       # 查询次数标记
        while True:
            secretStr, bgss, ip_bp = spider_main(cookies)
            i += 1
            time.sleep(0.2)
            if i % 400 == 0:
                time.sleep(15)
            if ip_bp[0] == 1:
                time.sleep(10)
            if len(secretStr) != 0 and len(bgss) != 0:
                if bgss[-1] == 'True':
                    if len(secretStr) == 1:
                        print("有票了！！马上进行抢购哦~")
                        if setting.apitype == 'api':
                            cookie_dict = self.cookie_api()
                        else:
                            cookie_dict = self.getcookies()
                        cookies = cookie_dict
                        break
                else:
                    print("您查询的车次不存在，请检擦重新输入车次信息。")
            print('正在进行第{}次查询，请稍后...'.format(list_getnum[-1] + i))
        bgs = main(secretStr, cookies)
        return bgs, i


def ticket_server_main():
    with open('init/cookie_bgs/cookiezt.txt', 'w') as f:
        f.write('False\n')
        f.close()

    start = time.time()
    ticket = Ticket_Service_Client()
    list_getnum = [0]
    while True:
        bgs, i = ticket.start_main(list_getnum=list_getnum)
        list_getnum.append(i)
        if 'True' in bgs[0]:
            gpf = bgs[0]
            emailinfo = gpf[-1]
            print("===" * 40)
            print("恭喜你，抢到票了！！！")
            print(emailinfo)
            del gpf[-1]
            print("购票信息：", gpf)
            print("请在30分钟内登录12306官方网站进行支付购买，否则本次购票将失效！")
            if emailinfo.split('，')[0] == '二维码加载成功':
                if setting.email_bgs == 1:
                    ticket.Email_Client(playinfo=gpf)
                else:
                    pass
            if emailinfo.split('，')[0] == '二维码加载失败':
                if setting.email_bgs == 1:
                    ticket.MIMETexts(playinfo=gpf)
                else:
                    pass
            print("===" * 40)
            break
        elif bgs[0] == 'bkddp':
            break
        elif bgs[0] == 'wfk':
            break
        elif bgs[0] == 'ypbz':
            pass
        elif bgs[0] == 'postfalse':
            pass
        elif bgs[0] == 'lodlogin':
            pass
    print("startime cost:", start, "seconds")
    end = time.time()
    print("endtime cost:", end, "seconds")
    print("main threed cost:", end - start, "seconds")

    with open('init/cookie_bgs/cookiezt.txt', 'w') as f:
        f.write('True\n')
        f.close()


    # spider_main()
    # window.json_ua.toString()   encryptedData
