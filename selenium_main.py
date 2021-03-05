# -- coding: utf-8 --
# @Time : 2021/1/14 0:19
# @Author : Los Angeles Clippers
# @Email: 229456906@qq.com
# @sinaemail: angelesclippers@sina.com
import time

from pro_function.Chepiao_Models import MonestFunctionSeleniumSpider


if __name__ == '__main__':
    """
    使用selenium进行抢购
    """
    model = MonestFunctionSeleniumSpider()
    model.login2()
    time.sleep(3)
    model.search_city()


