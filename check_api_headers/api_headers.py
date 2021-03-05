# -- coding: utf-8 --
# @Time : 2021/1/18 10:38
# @Author : Los Angeles Clippers
# @Email: 229456906@qq.com
# @sinaemail: angelesclippers@sina.com
import hashlib
import base64


class Enheaders():
    def Dbase64(self, string):
        # base64解密
        dstr = base64.b64decode(string).decode('utf-8')  # byte类型与字符串类型都统一解密
        return dstr

    def Ebase64(self, string):
        # base64加密
        estr = str(base64.b64encode(string.encode('utf-8')), 'utf-8')  # 返回字符串类型
        return estr

    def MD5(self, str):
        # 创建md5对象
        hl = hashlib.md5()
        hl.update(str.encode(encoding='utf-8'))
        return hl.hexdigest()


if __name__ == '__main__':

    en = Enheaders()
    print(en.MD5('重庆'))





