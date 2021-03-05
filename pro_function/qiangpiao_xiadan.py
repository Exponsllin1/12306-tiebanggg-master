import datetime
import random
import re
import time

import requests
import json
from _utils.setting_models.setting_class import setting, getztid, variable, USER_AGENTS

class SubmitOrderRequests():
    def __init__(self):
        self.session = requests.session()

    def checkUser(self, cookies):
        """
        验证是否登陆
        :return:
        """
        url = "https://kyfw.12306.cn/otn/login/checkUser"
        data = {
            '_json_att': ''
        }
        setting.headers['User-Agent'] = random.choice(USER_AGENTS)
        resposne = self.session.post(url=url, data=data, headers=setting.headers, cookies=cookies)
        try:
            httpstatus = json.loads(resposne.text)['httpstatus']
            print('[checkUser]-httpstatus:', httpstatus)
            print('[checkUser]-resposne.text:', resposne.text)
            return True
        except:
            return False

    def submit(self, res, cookies, read_id, item):
        """
        请求 url = "https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest"
        :param res: 列车信息返回的secretStr中，切割获取即可
        :param cookies:
        :param read_id: 城市与其对应的ID------>  KQW-贵阳北
        :param item: 列车信息返回的字符串
        :return:
        """
        url = "https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest"
        data = {
            'secretStr': res,
            'train_date': variable.date,
            'back_train_date': variable.date,
            'tour_flag': 'dc',
            'purpose_codes': 'ADULT',
            'query_from_station_name': read_id[item.split('|')[6]],
            'query_to_station_name': read_id[item.split('|')[7]],
        }
        setting.headers['User-Agent'] = random.choice(USER_AGENTS)
        print('[submit]-data:', data)
        response = self.session.post(url=url, data=data, headers=setting.headers, cookies=cookies)
        try:
            messages = json.loads(response.text)['messages']
            print('[submit]-messages:', messages)
            print('[submit]-ponse.status_code:', response.status_code)
            print('[submit]-response.text:', response.text)
            if len(messages) != 0:
                if '当前时间不可以订票' in messages[0]:
                    return '当前时间不可以订票'
                elif '您还有未处理的订单' in messages[0]:
                    return '您还有未处理的订单'
                elif '提交失败，请重试...' in messages[0]:
                    return '提交失败，请重试...'
                else:
                    return 'True'
            else:
                return 'True'
        except json.decoder.JSONDecodeError as e:
            print("===" * 40)
            print("请先登录哦~")
            print("===" * 40)
            return '未登录'


    def initDc(self, cookies):
        """
        请求 url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        获取到REPEAT_SUBMIT_TOKEN， leftTicket, ticketInfoForPassengerForm
        :param cookies:
        :return:
        """
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        data = {
            '_json_att': ''
        }
        setting.headers['User-Agent'] = random.choice(USER_AGENTS)
        response = self.session.post(url=url, data=data, headers=setting.headers, cookies=cookies)
        # print(response.text)
        globalRepeatSubmitToken = re.search(r"globalRepeatSubmitToken = '(.*?)'", response.text)
        print('[initDc]-globalRepeatSubmitToken:', globalRepeatSubmitToken)
        leftTicket = re.search(r"'leftTicketStr':'(.*?)'", response.text)
        print('[initDc]-leftTicket:', leftTicket)
        ticketInfoForPassengerForm = re.search(r"ticketInfoForPassengerForm=(.*?);", response.text)
        print('[initDc]-ticketInfoForPassengerForminitDc', ticketInfoForPassengerForm)

        return globalRepeatSubmitToken, leftTicket, ticketInfoForPassengerForm

    def confirmPassengergetPassengerDTOs(self, REPEAT_SUBMIT_TOKEN, cookies):
        """
        请求 url = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
        :param REPEAT_SUBMIT_TOKEN: 通过 initDc函数得到
        :param cookies:
        :return:
        """
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
        data = {
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': REPEAT_SUBMIT_TOKEN.group(1),
        }
        # 'Referer': 'https://kyfw.12306.cn/otn/confirmPassenger/initDc',
        setting.headers['Referer'] = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        setting.headers['User-Agent'] = random.choice(USER_AGENTS)
        response = self.session.post(url=url, data=data, headers=setting.headers, cookies=cookies).text
        userinfo = json.loads(response)
        print('[confirmPassengergetPassengerDTOs]-userinfo', userinfo)
        return userinfo

    def checkOrderInfo(self, userinfo, REPEAT_SUBMIT_TOKEN, cookies):
        """
        请求 url = "https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo"
        :param userinfo: 通过 confirmPassengergetPassengerDTOs函数得到
        :param REPEAT_SUBMIT_TOKEN: 通过 initDc函数得到
        :param cookies:
        :return:
        """
        userinfo = userinfo
        url = "https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo"
        passenger_id_no = userinfo['data']['normal_passengers'][0]['passenger_id_no']       # 身份证
        mobile_no = userinfo['data']['normal_passengers'][0]['mobile_no']                   # 电话
        allEncStr = userinfo['data']['normal_passengers'][0]['allEncStr']
        passenger_name = userinfo['data']['normal_passengers'][0]['passenger_name']         # 姓名
        data = {
            'cancel_flag': '2',
            'bed_level_order_num': '000000000000000000000000000000',
            'passengerTicketStr': '{},0,1,{},1,{},{},N,{}'.format(variable.play_zuowei_id, passenger_name, passenger_id_no, mobile_no, allEncStr),
            'oldPassengerStr': '{},1,{},1_'.format(passenger_name, passenger_id_no),
            'tour_flag': 'dc',
            'randCode': '',
            'whatsSelect': '1',
            'sessionId': '',
            'sig': '',
            'scene': 'nc_login',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': REPEAT_SUBMIT_TOKEN.group(1),
        }
        setting.headers['User-Agent'] = random.choice(USER_AGENTS)
        print('[checkOrderInfo]-data:', data)
        setting.headers['Referer'] = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        response = self.session.post(url=url, data=data, headers=setting.headers, cookies=cookies).text
        # submitStatus":true,"smokeStr":""},"messages":[系统繁忙],"validateMessages":{}}
        print('[checkOrderInfo]-response.text:', response)
        return [passenger_name, mobile_no, passenger_id_no]

    def getQueueCount(self, REPEAT_SUBMIT_TOKEN, leftTicket, item, cookies, train_no, stationTrainCode, train_location):
        """
        请求 url = "https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount"
        :param REPEAT_SUBMIT_TOKEN: 通过 initDc函数得到
        :param leftTicket: 通过 initDc函数得到
        :param item: 列车信息字符串
        :param cookies:
        :param train_no: 通过 secretStr列车字符串得到，切割处理提取即可
        :param stationTrainCode: 通过 secretStr列车字符串得到，切割处理提取即可
        :param train_location: 通过 secretStr列车字符串得到，切割处理提取即可
        :return:
        """
        url = "https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount"
        data = {
            'train_date': '{} {} {} {} 00:00:00 GMT+0800 (中国标准时间)'.format(
                variable.xingqi[self.weekdays(variable.date)],
                variable.yuefen[variable.date.split('-')[1]],
                variable.date.split('-')[2],
                variable.date.split('-')[0]),
            'train_no': train_no,
            'stationTrainCode': stationTrainCode,
            'seatType': '3',
            'fromStationTelecode': item.split('|')[6],
            'toStationTelecode': item.split('|')[7],
            'leftTicket': leftTicket.group(1),
            'purpose_codes': '00',
            'train_location': train_location,
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': REPEAT_SUBMIT_TOKEN.group(1),
        }
        setting.headers['User-Agent'] = random.choice(USER_AGENTS)
        print('[getQueueCount]-data:', data)
        response = self.session.post(url=url, data=data, headers=setting.headers, cookies=cookies).text
        print('[getQueueCount]-response.text:', response)

    def confirmSingleForQueue(self, userinfo, key_check_isChange, leftTicketStr, REPEAT_SUBMIT_TOKEN, train_location, cookies):
        """
        请求 url = "https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue"
        :param userinfo: 通过 confirmPassengergetPassengerDTOs函数得到
        :param key_check_isChange: 通过 initDc函数得到的ticketInfoForPassengerForm字符串，切割处理提取即可
        :param leftTicketStr: 通过 initDc函数得到的对象
        :param REPEAT_SUBMIT_TOKEN: 通过 initDc函数得到
        :param train_location: 通过 secretStr列车字符串得到，切割处理提取即可
        :param cookies:
        :return:
        """
        url = "https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue"
        passenger_id_no = userinfo['data']['normal_passengers'][0]['passenger_id_no']  # 身份证
        mobile_no = userinfo['data']['normal_passengers'][0]['mobile_no']  # 电话
        allEncStr = userinfo['data']['normal_passengers'][0]['allEncStr']
        passenger_name = userinfo['data']['normal_passengers'][0]['passenger_name']  # 姓名
        data = {
            'passengerTicketStr':  '{},0,1,{},1,{},{},N,{}'.format(variable.play_zuowei_id, passenger_name, passenger_id_no, mobile_no, allEncStr),
            'oldPassengerStr': '{},1,{},1_'.format(passenger_name, passenger_id_no),
            'randCode': '',
            'purpose_codes': '00',
            'key_check_isChange': key_check_isChange.group(1),
            'leftTicketStr': leftTicketStr.group(1),
            'train_location': train_location,
            'choose_seats': '',
            'seatDetailType': '000',
            'is_jy': 'N',
            'encryptedData': 'b2RYyohqKS7CquRGBxTcHCFH9xuPXhLQm.5rOPDxuYx9MWPRiVUUCJR8Jb7768PlO18xwtO_f2kqeWp9PhBkEI2ppH5IQU70taHE9qkQNzShJUCIe2C2_GIbAVCDaMU39FmF6t_iWHG4HCD5aGxTxvP6D_SK3WolFGw5zNr95cWjKBAHeDyYcbJKlO2fNC.IiLjGhPYxevdIyaORNVBkIglROvhx7yS5ByTx4aX2h0CtaWX1.GUfJowJ_wy92Ei1WHoTKEEyOC0v6OdrRpjMeUpcN0GL3qkXlBX27YV06yRcNwRjzFj4VHUD4mS04MiaJKPwmBYFOj1a6crtiR523OlManLqy4oyHv20T__zBNpGiDKdwv3Q0d_2y6T0P1BdM2Cy7tL7xVwPnkOtHGpNBoGNDLwc7WRdd8AWT5xpkeoxVa_6qMMdq3CGkihLe3jQtVh5WEqDF0.OlEJuH9KZCKHeQGO3okH4pXMZuoIrbFw7bZ9aEPJHHjvcqhqpksLMRjC.ijD6xYfuSqMBYI2Ir8WWyBBefP3WQeFGWvNmtKX0DZ6PA7RkFrCvGYoGBuCw.d.SnC2AJnDDN5j6XF2tWbYWXZztJVCT2JorEzXGLIzfZJ8R13vSQP0r.u5yq_Rag0wa_t2pUNMSuMoseiJ_bR18WDU.4ZHYOOpdi3XX845jWV7lWznKEMJJQhSZdqh5wNo5isW8rLeleiNMxMvMiYm3E47PNkMRlBGmlsCM_55Ang429sP.Ga3ngROj4Fo6jdyBm8HjIjdsn.5yQDK7ES9MoyDYSu6fULH8MKXSmstUig1i2bXSBOphvfxr1UgQsjyL9hlnaGUh5E._E7RF7ujjSKrDAYqwp.pm1lVwx8Iu5ZGIFuIUFugWFeknw_ruHY5bjYH1w.PhFuldQtoMfhpLVdftAhIpbntglTm.tvPvTNbxjkU4IirOy9tjMn6K2OBnTyWHG57e6ZyqeXB3pVQLPVCpEih4YUS5kTed9NuewHEy9NHWlkCJJDIEFtrKbxSbLzyJv7.UbWvIqARcrPKUdUvqTZ3VKxnz9z2WzLIhdPVe.v9oRwXNVoY.CK6J_FZV3tqRqQjza304CCt.AFHrVyNv7TLrACRty9IkjKYIE.ICDBd4xdRoMpA.IIgD0_i2bbxzJCqjnXfToCEN1fwHhyKRJdTY5flrg5rx7aVH08xBJzqNzZhPo1TG238DGeG74dBmk9eb2O0gKtl3ygBhvC_VPYESkT1z7ScdyyhhREAENOh7gKGY3G2yBt_SQGlh.wIN8cAg_Sy1oE31UHa1kL91xaw0pj_JG91XaLwANiig1qSu0n8QNUl6gD21CSi_mn47Q1DJNDB_IpFLUTTr9.CK8hSKvJvWM7oE65JKznhLygMzOcXaCdoVtsMq25DXl_UjThVw9LDUEzQi6A.9uz3sDNBRyGn6rKrK8eqTAtZf0yjfOUOP1xA9EJ_2ItvB_nBazADRlswyPAmuHHFqR6Vs5cW8xZXW4JDG8yMDYyn_wuztN85wOhnUDukPJqEPXDZSH6IDW25BY95GYepHd7ccklxsqYDOoJNcMCvIWw_mlYdqgXAH.M7yU3aDZugIg2tQp0cn2VVzCJpoHUZqjt29PmuXPEvxg2nwHJj7w8XRFa0S8ozDowufygXu2_OdConIAbv9CAPW_Ige9S8c2MdJ0u4S44CtSHFxIvKiZX3yjqaGghRriF0sqXVf_srYaV.tA1tt8HNiVDATN70MDEo1sGdodYm02f4aexOYiAsvYb0E2PP8_QKa52In9rRPisKnUlr5ZDRJU2EZj7JbnT70rCO2r7pHiiO5714RLl2NDSzAw3L2f4wGXQ2_VDY2IxyVKptLZqpLmWzIdtFSBFD2bpFyYTX1.jQpb4zFt4KLOv.Tfle0bZzBGipBzwwojpziZ4.9Cwv.LIp4xA',
            # RkXXxFjB2ICUIkwDtFahao__T3Kn3WMkoFRXZ8w_x2wWC1n6aRiept9ZAaLeNSLwRroyXsdvPLs4NfW1o0rq2f3Z631ottPWE6Q5_Qdh7AR_XE_eR4SRSyPBBuON2lqPoHosQLHWGu_z4AZEWvNQQ_AMqkfh0TiiOAZjQ06XaYReCRAfzjOyJBDbGL64R4_X5DIsE_RrigeAIrSUQ_I.1oXExpXi3xQkKKKuFkS5mqkxCQWXyonORb0fkoaixk7u4txJ5LVz8gu_Ljl.B5wophGqWuu9I20oEtoH8MUZLaJU2FwC.hjAO_sbf6ijuwciusrwj6_F7Cn.42u3HbGShqVad7yYtpB40voB0cFa2YGB9uExIKGVlUti0c8IixDD_77btCLq_DgebG2oIkJnR.z5GdCMvs0mhQCtiu7_Peg.NSLagzKbGpC1av_xp1gS0vk9ywasHPvegIcVxx4ABA0VQYsvZ.oouNz_tCkjuHkkx89hb8S3Nm0uTSAfk5x_kso7ubgPdtBd7iDj5p_LUPz.ZIkHdDTlx2cCL4F1q9YksIbiWoN3LtdM0taP61hRuOm9Te37FofIzDKzcNrj5UmwHjKTq86e.bB6GW_ehdvxspTqj2sl7CG_hVSQjbIw4vNFUydpHygI7CdWGw.vX5G4Kga37YV9MVbssDqh7L7jWG2XNcY0stBuctYRn3KxdKHOJciPGHL3OA42DYggenHTVzAdu_bI7epCe6dH5Bve12m_VIBxzhLjOnxLwKUA1iPbvkseIRzr7ux_635Zo9wPOglJdUiLsf5NPisZHWUxfquT4lY_Bb0mjq0gyW8BbpLEMxKjBMmbmGkr1QF7QGSnExKXEea9yRtd1gWuyc5_nwKUXrT1VV9mTfWE2q0kyCPU.NfFk8sVTU98SvLRVY9.Cq06J73CR34YZT67U_5FuuvVh7s3K56y0mC99MWhcGNXNOGZQQx4y6IXOHKdjvdUB8syJMzCEMas2YjSg0RcMNGGdoIb2hg9JzFdi1C3wVb0Vzsirj53mXhR6fSAR.XGIN7Ex9rnChhXSnfCBaoTgd_wye664Txj2EktZsu8Cu3AizncPvnXh7zADlwOs94qnVYEiDaneUPKAFx4eSUw4gg7oUYPMJju_0eAw.Yan0msBuvjr145Wn_f8jQwnh4Vn_yOOKiMXdvBsILJnaXPqJVQfsS91HwEsL9FZhWs9_gwXWkx.IlLe.sPaiQusmVOCFHUbDaFq12PsrG7HWCiRJl1FXfw4DOq312cWr.eagMdEpwkjr5V.qtTQUSFrGylAIONiWKkNIs5R4BSzjeCCNwchkadoEemP7IK0zLHqG7_Idie5FaYyCh7mHoImfVlChi4yTAYx4KFGgjqcSXBBLCbHUrrxn_LQg9bTW_AiOfT8ZnYc5jjk8FzlnmToeRtZgw5Yt86bF3Yq1G7zltvOux0prMKrCeVoI0VopP7wg1r14p8VWrCp1EPNovNS2bM4.yCFIqfbllOO2m_nuScsM8DEZ8VYuqxOEFAmAf0386mYdhTUovjtgcRcMbd7CKzINHUcvp9scG21tCPMYWlTg8SZ11icB7MRBi54N.Fgoxf.znAakR195JQVxkP4yoWTmd423VQCfe6PfUJsDR4KUl1pdJBPiHyTmMauLguBdsPfgp_8zv5uINGz7eGyy73h1LIJQ3ukeKVC4Gd8g0
            'whatsSelect': '1',
            'roomType': '00',
            'dwAll': 'N',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': REPEAT_SUBMIT_TOKEN.group(1),
        }
        setting.headers['User-Agent'] = random.choice(USER_AGENTS)
        setting.headers['Referer'] = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        response = self.session.post(url=url, data=data, headers=setting.headers, cookies=cookies).text
        print("[confirmSingleForQueue]-response.text:", response)
        if '余票不足' in response:
            return '余票不足!'
        else:
            return 'True'

    def queryMyOrderNoComplete(self, cookies):
        """
        获取待支付订单信息
        :param cookies:
        :return:
        """
        url = "https://kyfw.12306.cn/otn/queryOrder/queryMyOrderNoComplete"
        setting.headers['User-Agent'] = random.choice(USER_AGENTS)
        setting.headers['Referer'] = 'https://kyfw.12306.cn/otn/view/train_order.html'
        data = {
            '_json_att': '',
        }

        info_dict = {}
        response = self.session.post(url=url, headers=setting.headers, cookies=cookies, data=data).text
        jsdata = json.loads(response)['data']['orderDBList'][0]
        info_dict['姓名：'] = jsdata['array_passser_name_page'][0]         # 姓名
        info_dict['出发地：'] = jsdata['from_station_name_page'][0]        # 出发地
        info_dict['目的地：'] = jsdata['to_station_name_page'][0]          # 目的地
        info_dict['出发日期：'] = jsdata['start_train_date_page'].split(' ')[0]             # 出发日期
        info_dict['订单号：'] = jsdata['sequence_no']                   # 订单号
        info_dict['价格：'] = jsdata['ticket_total_price_page']         # 价格
        info_dict['出发时间：'] = jsdata['start_time_page']             # 出发时间
        info_dict['到达时间：'] = jsdata['arrive_time_page']            # 到达时间
        info_dict['车次：'] = jsdata['train_code_page']                 # 车号
        tickets = jsdata['tickets'][0]
        a = tickets['coach_name']                   # 车厢
        b = tickets['seat_name']                    #座位号
        info_dict['列车信息：'] = a + '车' + b
        info_dict['座位性质：'] = tickets['seat_type_name']          # 座位性质
        info_dict['支付时间：'] = tickets['reserve_time']            # 支付时间
        info_dict['到期时间：'] = tickets['pay_limit_time']          # 到期时间
        return info_dict

    def payOrder(self, REPEAT_SUBMIT_TOKEN, cookies):
        """
        请求 url = 'https://kyfw.12306.cn/otn//payOrder/init?random={}'.format(int(time.time()*1000))
        支付必须先走这一步，浏览器会记录指纹
        :param REPEAT_SUBMIT_TOKEN: 通过 initDc函数得到
        :param cookies:
        :return: sequence_no, payOrder_url
        """
        url = 'https://kyfw.12306.cn/otn//payOrder/init?'
        setting.headers['User-Agent'] = random.choice(USER_AGENTS)
        setting.headers['Referer'] = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        data = {
            'json_att': '',
            'REPEAT_SUBMIT_TOKEN': REPEAT_SUBMIT_TOKEN.group(1),
        }
        params = {
            'random':str(int(time.time()*1000))
        }
        response = self.session.post(url=url, data=data, headers=setting.headers,
                                     cookies=cookies, params=params).text
        if len(list(response)) < 3000:
            print("[payOrder]-response.text", response)
        sequence_no = re.search(r"sequence_no = '(.*?)'", response)
        print("[payOrder]-sequence_no:", sequence_no)
        payOrder_url = url
        return sequence_no, payOrder_url + 'random=' + params['random']

    def resultOrderForDcQueue(self, sequence_no, REPEAT_SUBMIT_TOKEN, cookies):
        """
        url = "https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue"
        支付必须先走这一步，浏览器会记录指纹
        :param sequence_no: 通过payOrder函数获得
        :param REPEAT_SUBMIT_TOKEN: 通过 initDc函数得到
        :param cookies:
        :return: None
        """
        url = "https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue"
        setting.headers['User-Agent'] = random.choice(USER_AGENTS)
        setting.headers['Referer'] = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        data = {
            'orderSequence_no': sequence_no.group(1),
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': REPEAT_SUBMIT_TOKEN.group(1),
        }
        response = self.session.post(url=url, data=data, cookies=cookies, headers=setting.headers).text
        print("[resultOrderForDcQueue]-response.text:", response)

    def paycheckNew(self, payOrder_url, cookies):
        """
        url = "https://kyfw.12306.cn/otn/payOrder/paycheckNew"
        referer对象为 payOrder 函数中请求的对象
        :param payOrder_url: 从 payOrder 函数返回值中获取
        :param cookies:
        :return: payForm
        """
        url = "https://kyfw.12306.cn/otn/payOrder/paycheckNew"
        data = {
            'batch_nos': '',
            'coach_nos': '',
            'seat_nos': '',
            'passenger_id_types': '',
            'passenger_id_nos': '',
            'passenger_names': '',
            'allEncStr': '',
            'insure_price_all': '',
            'insure_types': '',
            'if_buy_insure_only': 'N',
            'ins_selected_time': '',
            'ins_clause_time': '',
            'ins_notice_time': '',
            'hasBoughtIns': '',
            '_json_att': '',
        }
        setting.headers['User-Agent'] = random.choice(USER_AGENTS)
        setting.headers['Referer'] = payOrder_url
        response = self.session.post(url=url, data=data, headers=setting.headers, cookies=cookies).text
        payForm = json.loads(response)['data']['payForm']
        print("[paycheckNew]-payForm:", payForm)
        return payForm

    def weekdays(self, apply_time):
        """
        判断购买日期为星期几
        :param apply_time:
        :return:
        """
        apply_week = datetime.datetime.strptime(apply_time, "%Y-%m-%d").weekday() + 1
        return str(apply_week)

    def check_play(self, cookies):
        """
        判断是否抢购成功
        :param d_play:
        :return:
        """
        i = 0
        while True:
            time.sleep(0.3)
            i += 1
            try:
                d_play = self.queryMyOrderNoComplete(cookies=cookies)
                cc = d_play['车次：']
                rt = 'True'
                break
            except:
                if i > 5:
                    rt = 'False'
                    break

        if rt == 'True':
            return True
        if rt == 'False':
            return False

def main(secretStr, cookies):
    """
    入口函数
    :param secretStr: 从 requests_12306_spiders中获取到，为列车信息字符串
    :param cookies:
    :return:
    """
    print(secretStr)
    res = str(secretStr[0].split('|')[0]).replace('%2F', '/').replace('%0A', '').replace('%2B', '+').replace('%3D', '=')
    print('res:', res)
    train_no = str(secretStr[0].split('|')[2])
    stationTrainCode = str(secretStr[0].split('|')[3])
    train_location = str(secretStr[0].split('|')[15])
    city_id_dict = getztid(cookies=cookies)
    read_id = {}
    for k, v in city_id_dict.items():
        read_id[v] = k
    SubmitOrderRequest = SubmitOrderRequests()
    if SubmitOrderRequest.checkUser(cookies):
        submit = SubmitOrderRequest.submit(
            res=res,
            cookies=cookies,
            read_id=read_id,
            item=secretStr[0]
        )
        if submit == 'True':
            REPEAT_SUBMIT_TOKEN, leftTicket, ticketInfoForPassengerForm = SubmitOrderRequest.initDc(cookies)
            if leftTicket != None:
                key_check_isChange = re.search(r"'key_check_isChange':'(.*?)'", ticketInfoForPassengerForm.group(1))
                userinfo = SubmitOrderRequest.confirmPassengergetPassengerDTOs(REPEAT_SUBMIT_TOKEN, cookies)
                play_info = SubmitOrderRequest.checkOrderInfo(userinfo, REPEAT_SUBMIT_TOKEN, cookies)
                SubmitOrderRequest.getQueueCount(
                    REPEAT_SUBMIT_TOKEN,
                     leftTicket,
                     secretStr[0],
                     cookies,
                     train_no,
                     stationTrainCode,
                     train_location
                )
                csf = SubmitOrderRequest.confirmSingleForQueue(
                    userinfo,
                                     key_check_isChange,
                                     leftTicket,
                                     REPEAT_SUBMIT_TOKEN,
                                     train_location,
                                     cookies
                                                )
                if csf == '余票不足!':
                    print("===" * 40)
                    print("余票不足!")
                    print("===" * 40)
                    return 'ypbz'               # 余票不足
                try:
                    # 付款流程
                    sequence_no, payOrder_url = SubmitOrderRequest.payOrder(REPEAT_SUBMIT_TOKEN, cookies)
                    SubmitOrderRequest.resultOrderForDcQueue(sequence_no, REPEAT_SUBMIT_TOKEN, cookies)
                    payFrom = SubmitOrderRequest.paycheckNew(payOrder_url=payOrder_url, cookies=cookies)
                    captchaloging = "二维码加载成功，您可以使用支付宝扫码付款或者请在30分钟内登录12306进行付款！"
                    play_info.insert(0, 'True')
                    play_info.insert(1, secretStr[0].split('|')[3])
                    play_info.append(
                        read_id[secretStr[0].split('|')[6]] + '---->' + read_id[secretStr[0].split('|')[7]])
                    play_info.append(variable.zwtype)
                    play_info.append(variable.date)
                    play_info.append(secretStr[0].split('|')[8] + '---->' + secretStr[0].split('|')[9])
                    play_info.append('历时 ' + secretStr[0].split('|')[10])
                    play_info.append(captchaloging)
                    return [play_info]
                except AttributeError as e:
                    captchaloging = "二维码加载失败，请在30分钟内登录12306进行付款！"
                    if SubmitOrderRequest.check_play(cookies=cookies):
                        play_info.insert(0, 'True')
                    else:
                        play_info.insert(0, 'False')
                    play_info.insert(1, secretStr[0].split('|')[3])
                    play_info.append(read_id[secretStr[0].split('|')[6]] + '---->' + read_id[secretStr[0].split('|')[7]])
                    play_info.append(variable.zwtype)
                    play_info.append(variable.date)
                    play_info.append(secretStr[0].split('|')[8] + '---->' + secretStr[0].split('|')[9])
                    play_info.append('历时 ' + secretStr[0].split('|')[10])
                    play_info.append(captchaloging)
                    return [play_info]

        elif submit == '当前时间不可以订票':
            print("===" * 40)
            print("当前时间不可以订票" )
            print("===" * 40)
            return ['bkddp']                      # 不可订票
        elif submit == '您还有未处理的订单':
            print("===" * 40)
            print("您还有未处理的订单, 未付款, 请处理后再重新购票。\n待处理信息：\n")
            d_play = SubmitOrderRequest.queryMyOrderNoComplete(cookies=cookies)
            for k, v in d_play.items():
                print(k, v)
            print("\n处理地址[https://kyfw.12306.cn/otn/view/train_order.html]")
            print("===" * 40)
            return ['wfk']                        # 未付款
        elif submit == '提交失败，请重试...':
            print("===" * 40)
            print("提交失败，请重试...")
            print("===" * 40)
            return ['postfalse']                  # 提交失败
        else:
            return ['lodlogin']                   # 未登录
    else:
        print("===" * 40)
        print("请先登录！")
        print("===" * 40)
        return ['lodlogin']                       # 未登录