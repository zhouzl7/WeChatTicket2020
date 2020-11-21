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
from django.test import TestCase, Client
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings

from adminpage.views import AdminLoginView
from codex.baseerror import PasswordError
from wechat.models import Activity, Ticket

import json
import datetime
import os


def create_superuser():
    User.objects.create_superuser('superuser', 'superuser@test.com', '123456test')


def create_act():
    Activity.objects.create(id=1, name='act_deleted', key='key', place='place',
                            description='description',
                            start_time=timezone.now() + datetime.timedelta(1000),
                            pic_url="url",
                            end_time=timezone.now() + datetime.timedelta(2000),
                            book_start=timezone.now() + datetime.timedelta(500),
                            book_end=timezone.now() + datetime.timedelta(800),
                            total_tickets=1000, status=Activity.STATUS_DELETED, remain_tickets=1000)
    Activity.objects.create(id=2, name='act_saved', key='key', place='place',
                            description='description',
                            start_time=timezone.now() + datetime.timedelta(1000),
                            pic_url="url",
                            end_time=timezone.now() + datetime.timedelta(2000),
                            book_start=timezone.now() + datetime.timedelta(500),
                            book_end=timezone.now() + datetime.timedelta(800),
                            total_tickets=1000, status=Activity.STATUS_SAVED, remain_tickets=1000)
    Activity.objects.create(id=3, name='act_published', key='key', place='place',
                            description='description',
                            start_time=timezone.now() + datetime.timedelta(1000),
                            pic_url="url",
                            end_time=timezone.now() + datetime.timedelta(2000),
                            book_start=timezone.now() - datetime.timedelta(500),
                            book_end=timezone.now() + datetime.timedelta(500),
                            total_tickets=1000, status=Activity.STATUS_PUBLISHED, remain_tickets=1000)


# 登录 API 4
class AdminLoginTest(TestCase):
    # 初始化
    def setUp(self):
        create_superuser()
        User.objects.create_user('user', 'user@test.com', '123456test')

    def test_get(self):
        c = Client()
        c.post('/api/a/login', {"username": "superuser", "password": "123456test"})
        response = c.get('/api/a/login').json()
        self.assertEqual(0, response['code'])

    def test_get_not_login(self):
        c = Client()
        response = c.get('/api/a/login').json()
        self.assertNotEqual(0, response['code'])

    # 路由测试
    def test_login_url(self):
        c = Client()
        response = c.post('/api/a/login', {"username": "superuser", "password": "123456test"})
        self.assertEqual(200, response.status_code)

    # superuser登录测试
    def test_superuser(self):
        c = Client()
        response = c.post('/api/a/login', {"username": "superuser", "password": "123456test"})
        self.assertEqual(0, json.loads(response.content.decode())['code'])

    # user登录测试
    def test_user(self):
        a_login = AdminLoginView()
        a_login.input = {
            'username': 'user',
            'password': '123456test'
        }
        self.assertRaises(PasswordError, a_login.post)

    # 密码错误测试
    def test_pwd_error(self):
        a_login = AdminLoginView()
        a_login.input = {
            'username': 'superuser',
            'password': 'test123456'
        }
        self.assertRaises(PasswordError, a_login.post)

    # 用户名无效测试
    def test_username_not_exit(self):
        a_login = AdminLoginView()
        a_login.input = {
            'username': 'null_user',
            'password': '123456test'
        }
        self.assertRaises(PasswordError, a_login.post)

    # 回退
    def tearDown(self):
        c = Client()
        c.post('/api/a/logout', content_type="application/json")


# 登出 API 5
class AdminLogoutTest(TestCase):
    # 初始化
    def setUp(self):
        create_superuser()

    # 登出测试
    def test_logout_not_login(self):
        c = Client()
        res = c.post('/api/a/logout', content_type="application/json")
        code = res.json()['code']
        self.assertNotEqual(0, code)

    # 登出测试
    def test_logout(self):
        c = Client()
        c.post('/api/a/login', {"username": "superuser", "password": "123456test"})
        res = c.post('/api/a/logout', content_type="application/json")
        code = res.json()['code']
        self.assertEqual(0, code)


# 活动列表 API 6
class ActivityListTest(TestCase):
    # 初始化
    def setUp(self):
        create_superuser()
        create_act()

    # get测试
    def test_get_list(self):
        c = Client()
        c.post('/api/a/login', {"username": "superuser", "password": "123456test"})
        response = c.get('/api/a/activity/list/').json()
        self.assertEqual(0, response['code'])
        self.assertEqual(2, len(response['data']))

    # get测试
    def test_get_list_no_login(self):
        c = Client()
        response = c.get('/api/a/activity/list/').json()
        self.assertNotEqual(0, response['code'])

    # 回退
    def tearDown(self):
        Activity.objects.all().delete()
        c = Client()
        c.post('/api/a/logout', content_type="application/json")


# 创建活动 API 8
class CreateActivityTest(TestCase):
    def setUp(self):
        create_superuser()

    def tearDown(self):
        Activity.objects.all().delete()
        c = Client()
        c.post('/api/a/logout', content_type="application/json")

    def test_createActivity(self):
        act = {"name": "name", "key": "key", "place": "place", "description": "description", "picUrl": "picUrl",
               "startTime": timezone.make_aware(datetime.datetime(2018, 10, 28, 8, 0, 0, 0)),
               "endTime": timezone.make_aware(datetime.datetime(2018, 10, 28, 18, 0, 0, 0)),
               "bookStart": timezone.now(),
               "bookEnd": timezone.make_aware(datetime.datetime(2018, 10, 27, 18, 0, 0, 0)),
               "totalTickets": 1000, "status": Activity.STATUS_PUBLISHED}
        c = Client()
        c.post('/api/a/login', {"username": "superuser", "password": "123456test"})
        res = c.post('/api/a/activity/create', act).json()
        self.assertEqual(0, res['code'])
        self.assertEqual("place", Activity.objects.get(name='name').place)

    def test_createActivity_not_login(self):
        act = {"name": "name1", "key": "key1", "place": "place1", "description": "description1", "picUrl": "picUrl1",
               "startTime": timezone.make_aware(datetime.datetime(2018, 10, 28, 8, 0, 0, 0)),
               "endTime": timezone.make_aware(datetime.datetime(2018, 10, 28, 18, 0, 0, 0)),
               "bookStart": timezone.now(),
               "bookEnd": timezone.make_aware(datetime.datetime(2018, 10, 27, 18, 0, 0, 0)),
               "totalTickets": 1000, "status": Activity.STATUS_PUBLISHED}
        c = Client()
        res = c.post('/api/a/activity/create', act).json()
        self.assertNotEqual(0, res['code'])


# 删除活动 API 7
class ActivityDeleteTest(TestCase):
    def setUp(self):
        create_superuser()
        create_act()

    def tearDown(self):
        Activity.objects.all().delete()
        c = Client()
        c.post('/api/a/logout', content_type="application/json")

    # 删除存在的活动
    def test_delete_act_exited(self):
        self.assertEqual(Activity.STATUS_SAVED, Activity.objects.get(id=2).status)
        c = Client()
        c.post('/api/a/login', {"username": "superuser", "password": "123456test"})
        rep = c.post('/api/a/activity/delete/', {'id': 2}).json()
        self.assertEqual(Activity.STATUS_DELETED, Activity.objects.get(id=2).status)
        self.assertEqual(0, rep['code'])

    # 不登录删除活动
    def test_delete_act_not_login(self):
        c = Client()
        rep = c.post('/api/a/activity/delete/', {'id': 3}).json()
        self.assertEqual(Activity.STATUS_PUBLISHED, Activity.objects.get(id=3).status)
        self.assertNotEqual(0, rep['code'])

    # 正在订票中的活动不可删除
    def test_delete_act_booking(self):
        self.assertEqual(Activity.STATUS_PUBLISHED, Activity.objects.get(id=3).status)
        c = Client()
        c.post('/api/a/login', {"username": "superuser", "password": "123456test"})
        rep = c.post('/api/a/activity/delete/', {'id': 3}).json()
        self.assertNotEqual(0, rep['code'])

    # 删除已删除的活动
    def test_delete_act_deleted(self):
        c = Client()
        c.post('/api/a/login', {"username": "superuser", "password": "123456test"})
        rep = c.post('/api/a/activity/delete/', {'id': 1}).json()
        self.assertNotEqual(0, rep['code'])

    # 删除不存在的活动
    def test_delete_act_not_exited(self):
        c = Client()
        c.post('/api/a/login', {"username": "superuser", "password": "123456test"})
        rep = c.post('/api/a/activity/delete/', {'id': 40}).json()
        self.assertNotEqual(0, rep['code'])


# 上传图像 API 9
class UploadImageTest(TestCase):
    def setUp(self):
        create_superuser()

    def tearDown(self):
        c = Client()
        c.post('/api/a/logout', content_type="application/json")

    def test_upload_image(self):
        c = Client()
        c.post('/api/a/login', {"username": "superuser", "password": "123456test"})
        path = os.path.join(settings.BASE_DIR, 'static/cat.jpg')
        with open(path, 'rb') as img:
            res = c.post('/api/a/image/upload', {'image': img}).json()
        self.assertEqual(0, res['code'])

    def test_upload_image_not_login(self):
        c = Client()
        path = os.path.join(settings.BASE_DIR, 'static/cat.jpg')
        with open(path, 'rb') as img:
            res = c.post('/api/a/image/upload', {'image': img}).json()
        self.assertNotEqual(0, res['code'])


# 活动详情 API 10
class ActivityDetailTest(TestCase):
    def setUp(self):
        create_superuser()
        create_act()

    def tearDown(self):
        Activity.objects.all().delete()
        c = Client()
        c.post('/api/a/logout', content_type="application/json")

    def test_getDetail(self):
        c = Client()
        c.post('/api/a/login', {"username": "superuser", "password": "123456test"})
        res = c.get('/api/a/activity/detail', {'id': 2}).json()
        self.assertEqual(0, res['code'])
        self.assertEqual('act_saved', res['data']['name'])

    def test_getDetail_not_login(self):
        c = Client()
        res = c.get('/api/a/activity/detail', {'id': 2}).json()
        self.assertNotEqual(0, res['code'])

    def test_getDetail_deleted_act(self):
        c = Client()
        c.post('/api/a/login', {"username": "superuser", "password": "123456test"})
        res = c.get('/api/a/activity/detail', {'id': 1}).json()
        self.assertNotEqual(0, res['code'])

    def test_postDetail(self):
        act_changed_detail = {
            "id": 2,
            "name": 'changed',
            "key": 'changed',
            "place": 'changed',
            "description": 'changed',
            "start_time": timezone.now() + datetime.timedelta(1000),
            "end_time": timezone.now() + datetime.timedelta(2000),
            "book_start": timezone.now() - datetime.timedelta(500),
            "book_end": timezone.now() + datetime.timedelta(500),
            "total_tickets": 1000,
            "status": Activity.STATUS_SAVED,
            "remain_tickets": 1000,
            "pic_url": "changed"
        }
        c = Client()
        c.post('/api/a/login', {"username": "superuser", "password": "123456test"})
        self.assertEqual('act_saved', Activity.objects.get(id=2).name)
        res = c.post('/api/a/activity/detail', act_changed_detail).json()
        self.assertEqual('changed', Activity.objects.get(id=2).name)
        self.assertEqual(0, res['code'])

    # 已发布的活动不可修改name和place
    def test_postDetail_published(self):
        act_changed_detail = {
            "id": 3,
            "name": 'changed',
            "key": 'changed',
            "place": 'changed',
            "description": 'changed',
            "start_time": timezone.now() + datetime.timedelta(1000),
            "end_time": timezone.now() + datetime.timedelta(2000),
            "book_start": timezone.now() - datetime.timedelta(500),
            "book_end": timezone.now() + datetime.timedelta(500),
            "total_tickets": 1000,
            "status": Activity.STATUS_SAVED,
            "remain_tickets": 1000,
            "pic_url": "changed"
        }
        c = Client()
        c.post('/api/a/login', {"username": "superuser", "password": "123456test"})
        self.assertEqual('act_published', Activity.objects.get(id=3).name)
        res = c.post('/api/a/activity/detail', act_changed_detail).json()
        self.assertEqual('act_published', Activity.objects.get(id=3).name)
        self.assertNotEqual(0, res['code'])

    def test_postDetail_not_exist(self):
        act_changed_detail = {
            "id": 40,
            "name": 'changed',
            "key": 'changed',
            "place": 'changed',
            "description": 'changed',
            "start_time": timezone.now() + datetime.timedelta(1000),
            "end_time": timezone.now() + datetime.timedelta(2000),
            "book_start": timezone.now() - datetime.timedelta(500),
            "book_end": timezone.now() + datetime.timedelta(500),
            "total_tickets": 1000,
            "status": Activity.STATUS_SAVED,
            "remain_tickets": 1000,
            "pic_url": "changed"
        }
        c = Client()
        c.post('/api/a/login', {"username": "superuser", "password": "123456test"})
        res = c.post('/api/a/activity/detail', act_changed_detail).json()
        self.assertNotEqual(0, res['code'])

    def test_postDetail_not_login(self):
        act_changed_detail = {
            "id": 2,
            "name": 'changed',
            "key": 'changed',
            "place": 'changed',
            "description": 'changed',
            "start_time": timezone.now() + datetime.timedelta(1000),
            "end_time": timezone.now() + datetime.timedelta(2000),
            "book_start": timezone.now() - datetime.timedelta(500),
            "book_end": timezone.now() + datetime.timedelta(500),
            "total_tickets": 1000,
            "status": Activity.STATUS_SAVED,
            "remain_tickets": 1000,
            "pic_url": "changed"
        }
        c = Client()
        res = c.post('/api/a/activity/detail', act_changed_detail).json()
        self.assertNotEqual(0, res['code'])


# 菜单测试 API 11
class MenuTest(TestCase):
    def setUp(self):
        create_superuser()
        create_act()

    def tearDown(self):
        Activity.objects.all().delete()
        c = Client()
        c.post('/api/a/logout', content_type="application/json")

    def test_getMenu(self):
        c = Client()
        c.post('/api/a/login', {"username": "superuser", "password": "123456test"})
        res = c.get('/api/a/activity/menu').json()
        self.assertEqual(0, res['code'])

    def test_getMenu_not_login(self):
        c = Client()
        res = c.get('/api/a/activity/menu').json()
        self.assertNotEqual(0, res['code'])

    def test_postMenu(self):
        c = Client()
        c.post('/api/a/login', {"username": "superuser", "password": "123456test"})
        res = c.post('/api/a/activity/menu', {2: 2, 3: 3}).json()
        self.assertEqual(0, res['code'])

    def test_postMenu_not_login(self):
        c = Client()
        res = c.post('/api/a/activity/menu', {2: 2, 3: 3}).json()
        self.assertNotEqual(0, res['code'])


# 检票 API 12
class CheckinTest(TestCase):
    # 初始化
    def setUp(self):
        create_superuser()
        act = Activity.objects.create(id=1, name='act_published', key='key', place='place',
                                      description='description',
                                      start_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 8, 0, 0, 0)),
                                      pic_url="url",
                                      end_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 18, 0, 0, 0)),
                                      book_start=timezone.now(),
                                      book_end=timezone.make_aware(datetime.datetime(2018, 10, 27, 18, 0, 0, 0)),
                                      total_tickets=1000, status=Activity.STATUS_PUBLISHED, remain_tickets=1000)
        Ticket.objects.create(unique_id='1', activity=act, status=Ticket.STATUS_CANCELLED)
        Ticket.objects.create(unique_id='2', activity=act, status=Ticket.STATUS_USED)
        Ticket.objects.create(unique_id='3', activity=act, status=Ticket.STATUS_VALID)

    # 回退
    def tearDown(self):
        Ticket.objects.all().delete()
        Activity.objects.all().delete()
        c = Client()
        c.post('/api/a/logout', content_type="application/json")

    # 未登录检票
    def test_checkin_vaild_not_login(self):
        c = Client()
        res = c.post('/api/a/activity/checkin', {'actId': 1, 'ticket': '3'}).json()
        self.assertNotEqual(0, res['code'])

    # 正常检票
    def test_checkin_vaild(self):
        c = Client()
        c.post('/api/a/login', {"username": "superuser", "password": "123456test"})
        res = c.post('/api/a/activity/checkin', {'actId': 1, 'ticket': '3'}).json()
        self.assertEqual('3', res['data']['ticket'])
        self.assertEqual(0, res['code'])

    # 已用票检票
    def test_checkin_used(self):
        c = Client()
        c.post('/api/a/login', {"username": "superuser", "password": "123456test"})
        res = c.post('/api/a/activity/checkin', {'actId': 1, 'ticket': '2'}).json()
        self.assertNotEqual(0, res['code'])

    # 退票检票
    def test_checkin_cancelled(self):
        c = Client()
        c.post('/api/a/login', {"username": "superuser", "password": "123456test"})
        res = c.post('/api/a/activity/checkin', {'actId': 1, 'ticket': '1'}).json()
        self.assertNotEqual(0, res['code'])
