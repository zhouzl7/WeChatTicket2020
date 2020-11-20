#!/usr/bin/env python
# encoding: utf-8
"""
@author: zhouzl
@contact: zzl850783164@163.com
@software: 
@file: tests_function.py
@time: 2020/11/20 20:38
@desc:
"""
from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver
import time
import json


def create_superuser():
    User.objects.create_superuser('superuser1', 'superuser@test.com', '123456test')


class FunctionTestWrapper(LiveServerTestCase):
    def setUp(self) -> None:
        create_superuser()
        self.browser = webdriver.Chrome()

    def tearDown(self) -> None:
        self.browser.quit()


class AdminLoginFunctionTest(FunctionTestWrapper):
    def test_valid_login(self):
        self.browser.get(self.live_server_url + '/a/login')
        inputUserName = self.browser.find_element_by_id('inputUsername')
        inputPassword = self.browser.find_element_by_id('inputPassword')
        login_button = self.browser.find_element_by_id('loginnow')

        inputUserName.clear()
        inputUserName.send_keys('superuser1')

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
        inputUserName.send_keys('superuser1')

        inputPassword.clear()
        inputPassword.send_keys('error_pwd')

        login_button.click()
        time.sleep(3)

        self.assertEqual(self.browser.find_element_by_id('alert').text, '用户名或密码错误')
