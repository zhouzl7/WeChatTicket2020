#!/usr/bin/env python
# encoding: utf-8
"""
@author: zhouzl
@contact: zzl850783164@163.com
@software: 
@file: functionTests.py
@time: 2020/11/20 20:38
@desc:
"""
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import datetime

from wechat.models import Activity
from adminpage.unitTests import create_act, create_superuser


class AdminLoginFunctionTest(LiveServerTestCase):
    def setUp(self) -> None:
        create_superuser()
        self.browser = webdriver.Chrome()

    def tearDown(self) -> None:
        self.browser.quit()

    def test_valid_login(self):
        self.browser.get(self.live_server_url + '/a/login')
        inputUserName = self.browser.find_element_by_id('inputUsername')
        inputPassword = self.browser.find_element_by_id('inputPassword')
        login_button = self.browser.find_element_by_id('loginnow')

        inputUserName.clear()
        inputUserName.send_keys('superuser')

        inputPassword.clear()
        inputPassword.send_keys('123456test')

        login_button.click()
        time.sleep(3)

        self.assertEqual(self.browser.title, '活动列表 - 紫荆之声')

    def test_invalid_username(self):
        self.browser.get(self.live_server_url + '/a/login')
        inputUserName = self.browser.find_element_by_id('inputUsername')
        inputPassword = self.browser.find_element_by_id('inputPassword')
        login_button = self.browser.find_element_by_id('loginnow')

        inputUserName.clear()
        inputUserName.send_keys('null_user')

        inputPassword.clear()
        inputPassword.send_keys('123456test')

        login_button.click()
        time.sleep(3)

        self.assertEqual(self.browser.find_element_by_id('alert').text, '用户名或密码错误')

    def test_wrong_password(self):
        self.browser.get(self.live_server_url + '/a/login')
        inputUserName = self.browser.find_element_by_id('inputUsername')
        inputPassword = self.browser.find_element_by_id('inputPassword')
        login_button = self.browser.find_element_by_id('loginnow')

        inputUserName.clear()
        inputUserName.send_keys('superuser')

        inputPassword.clear()
        inputPassword.send_keys('error_pwd')

        login_button.click()
        time.sleep(3)

        self.assertEqual(self.browser.find_element_by_id('alert').text, '用户名或密码错误')


class AdminLogoutFunctionTest(LiveServerTestCase):
    def setUp(self) -> None:
        create_superuser()
        self.browser = webdriver.Chrome()
        self.browser.get(self.live_server_url + '/a/login')
        inputUserName = self.browser.find_element_by_id('inputUsername')
        inputPassword = self.browser.find_element_by_id('inputPassword')
        login_button = self.browser.find_element_by_id('loginnow')

        inputUserName.clear()
        inputUserName.send_keys('superuser')

        inputPassword.clear()
        inputPassword.send_keys('123456test')

        login_button.click()
        time.sleep(2)

    def tearDown(self) -> None:
        self.browser.quit()

    def test_logout(self):
        logout_button = self.browser.find_element_by_id('logout-button')
        logout_button.click()
        time.sleep(3)
        self.assertEqual('“紫荆之声”票务管理系统', self.browser.find_element_by_id('nav-title').text)


class ActivityFunctionTest(LiveServerTestCase):
    def setUp(self) -> None:
        create_superuser()
        self.browser = webdriver.Chrome()
        self.browser.get(self.live_server_url + '/a/login')
        inputUserName = self.browser.find_element_by_id('inputUsername')
        inputPassword = self.browser.find_element_by_id('inputPassword')
        login_button = self.browser.find_element_by_id('loginnow')

        inputUserName.clear()
        inputUserName.send_keys('superuser')

        inputPassword.clear()
        inputPassword.send_keys('123456test')

        login_button.click()
        time.sleep(2)

        self.browser.find_element(By.LINK_TEXT, "新增活动").click()
        time.sleep(2)

        inputName = self.browser.find_element_by_id('input-name')
        inputName.clear()
        inputName.send_keys('马兰花开')
        time.sleep(.5)

        inputKey = self.browser.find_element_by_id('input-key')
        inputKey.clear()
        inputKey.send_keys('马兰花开')
        time.sleep(.5)

        inputPlace = self.browser.find_element_by_id('input-place')
        inputPlace.clear()
        inputPlace.send_keys('大礼堂')
        time.sleep(.5)

        inputDescription = self.browser.find_element_by_id('input-description')
        inputDescription.clear()
        inputDescription.send_keys('好看的舞台剧')
        time.sleep(.5)

        inputPicUrl = self.browser.find_element_by_id('input-pic_url')
        inputPicUrl.clear()
        inputPicUrl.send_keys('''https://github.com/zhouzl7/WeChatTicket2020/blob/main/static/cat.jpg''')
        time.sleep(.5)

        inputTotalTickets = self.browser.find_element_by_id('input-total_tickets')
        inputTotalTickets.clear()
        inputTotalTickets.send_keys('1000')
        time.sleep(.5)

        self.timeList = list()
        for field0 in ('start', 'end', 'book-start', 'book-end'):
            tmpList = list()
            for field1 in ('year', 'month', 'day', 'hour', 'minute'):
                tmpList.append(self.browser.find_element_by_id('input-{}-{}'.format(field0, field1)))
            self.timeList.append(tmpList)
        start_time = datetime.datetime.now() + datetime.timedelta(30)
        end_time = datetime.datetime.now() + datetime.timedelta(32)
        book_start = datetime.datetime.now() + datetime.timedelta(7)
        book_end = datetime.datetime.now() + datetime.timedelta(10)
        self.inputTuple = (start_time.year, start_time.month, start_time.day, start_time.hour, start_time.minute,
                           end_time.year, end_time.month, end_time.day, end_time.hour, end_time.minute,
                           book_start.year, book_start.month, book_start.day, book_start.hour, book_start.minute,
                           book_end.year, book_end.month, book_end.day, book_end.hour, book_end.minute)
        idx = 0
        for tmpList in self.timeList:
            for val in tmpList:
                val.clear()
                val.send_keys(self.inputTuple[idx])
                idx += 1
                time.sleep(.5)

    def tearDown(self) -> None:
        Activity.objects.all().delete()
        self.browser.quit()

    def test_save(self):
        saveBtn = self.browser.find_element_by_id('saveBtn')
        saveBtn.click()
        time.sleep(2)
        self.assertEqual("成功", self.browser.find_element_by_id('resultHolder').text)
        self.browser.find_element(By.LINK_TEXT, "继续修改").click()
        time.sleep(3)
        idx = 0
        for field0 in ('start', 'end', 'book-start', 'book-end'):
            for field1 in ('year', 'month', 'day', 'hour', 'minute'):
                self.assertEqual(
                    str(self.inputTuple[idx]),
                    self.browser.find_element_by_id('input-{}-{}'.format(field0, field1)).get_attribute('value'))
                idx += 1

    def test_save_twice(self):
        saveBtn = self.browser.find_element_by_id('saveBtn')
        saveBtn.click()
        time.sleep(2)
        self.browser.find_element(By.LINK_TEXT, "继续修改").click()
        time.sleep(1)
        inputDescription = self.browser.find_element_by_id('input-description')
        inputDescription.clear()
        inputDescription.send_keys('超好看的舞台剧(修改)')
        time.sleep(1)
        saveBtn = self.browser.find_element_by_id('saveBtn')
        saveBtn.click()
        time.sleep(3)
        self.assertEqual("成功", self.browser.find_element_by_id('resultHolder').text)

    def test_publish(self):
        publishBtn = self.browser.find_element_by_id('publishBtn')
        publishBtn.click()
        time.sleep(3)
        self.assertEqual("成功", self.browser.find_element_by_id('resultHolder').text)

    def test_save_before_publish(self):
        saveBtn = self.browser.find_element_by_id('saveBtn')
        saveBtn.click()
        time.sleep(2)
        self.browser.find_element(By.LINK_TEXT, "继续修改").click()
        time.sleep(1)
        inputDescription = self.browser.find_element_by_id('input-description')
        inputDescription.clear()
        inputDescription.send_keys('超好看的舞台剧(修改)')
        time.sleep(1)
        publishBtn = self.browser.find_element_by_id('publishBtn')
        publishBtn.click()
        time.sleep(3)
        self.assertEqual("成功", self.browser.find_element_by_id('resultHolder').text)

    def test_reset(self):
        resetBtn = self.browser.find_element_by_id('resetBtn')
        resetBtn.click()
        time.sleep(3)

        self.assertEqual('', self.browser.find_element_by_id('input-name').get_attribute('value'))


class ActivityListFunctionTest(LiveServerTestCase):
    def setUp(self) -> None:
        create_superuser()
        create_act()
        self.browser = webdriver.Chrome()
        self.browser.get(self.live_server_url + '/a/login')
        inputUserName = self.browser.find_element_by_id('inputUsername')
        inputPassword = self.browser.find_element_by_id('inputPassword')
        login_button = self.browser.find_element_by_id('loginnow')

        inputUserName.clear()
        inputUserName.send_keys('superuser')

        inputPassword.clear()
        inputPassword.send_keys('123456test')

        login_button.click()
        time.sleep(2)

    def tearDown(self) -> None:
        Activity.objects.all().delete()
        self.browser.quit()

    def test_detail(self):
        self.browser.find_elements(By.LINK_TEXT, "详情")[0].click()
        time.sleep(3)
        self.assertEqual('act_saved', self.browser.find_element_by_id('input-name').get_attribute('value'))

    def test_delete(self):
        self.browser.find_element_by_id('del-2').click()
        time.sleep(2)
        self.browser.find_element_by_css_selector("[onclick=\"delConfirm()\"]").click()
        time.sleep(3)
        self.assertEqual(1, len(self.browser.find_elements(By.CLASS_NAME, "td-delete")))

    def test_checkin(self):
        time.sleep(1)
        self.assertEqual(1, len(self.browser.find_elements(By.LINK_TEXT, "检票")))
        self.browser.find_element(By.LINK_TEXT, "检票").click()
        time.sleep(3)

    def test_edit_booking_act(self):
        self.browser.find_elements(By.LINK_TEXT, "详情")[1].click()
        time.sleep(3)
        self.assertEqual('true', self.browser.find_element_by_id('input-name').get_attribute('disabled'))
        self.assertEqual('true', self.browser.find_element_by_id('input-key').get_attribute('disabled'))
        self.assertEqual('true', self.browser.find_element_by_id('input-total_tickets').get_attribute('disabled'))
        idx = 0
        for field1 in ('year', 'month', 'day', 'hour', 'minute'):
            self.assertEqual(
                'true',
                self.browser.find_element_by_id('input-{}-{}'.format('book-start', field1)).get_attribute('disabled'))
            idx += 1