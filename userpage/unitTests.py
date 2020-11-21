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
import datetime

from django.test import TestCase, Client
from django.utils import timezone
from django.contrib.auth.models import User as SystemUser

from wechat.models import User, Activity, Ticket
from adminpage.unitTests import create_act, create_superuser


# 学号绑定 API 1 (数据库无student_id字段，无法测试)

# 活动详情 API 2
class ActivityTest(TestCase):
    # 初始化
    def setUp(self):
        create_act()

    def tearDown(self):
        Activity.objects.all().delete()

    # 获取已删除活动的详情
    def test_get_deleted_act_detail(self):
        c = Client()
        res = c.get('/api/u/activity/detail', {'id': 1}).json()
        self.assertNotEqual(0, res['code'])

    # 获取未发布活动的详情
    def test_get_saved_act_detail(self):
        c = Client()
        res = c.get('/api/u/activity/detail', {'id': 2}).json()
        self.assertNotEqual(0, res['code'])

    # 获取发布活动的详情
    def test_get_published_act_detail(self):
        c = Client()
        res = c.get('/api/u/activity/detail', {'id': 3}).json()
        self.assertEqual(0, res['code'])
        self.assertEqual('act_published', res['data']['name'])


# 电子票详情 API 3
class TicketsTest(TestCase):
    # 初始化
    def setUp(self):
        act = Activity.objects.create(id=3, name='act_published', key='key', place='place',
                                      description='description',
                                      start_time=timezone.now() + datetime.timedelta(1000),
                                      pic_url="url",
                                      end_time=timezone.now() + datetime.timedelta(2000),
                                      book_start=timezone.now() - datetime.timedelta(500),
                                      book_end=timezone.now() + datetime.timedelta(500),
                                      total_tickets=1000, status=Activity.STATUS_PUBLISHED, remain_tickets=1000)
        user1 = SystemUser.objects.create_user('user1', 'user1@test.com', '123456test')
        user2 = SystemUser.objects.create_user('user2', 'user2@test.com', '123456test')
        user3 = SystemUser.objects.create_user('user3', 'user3@test.com', '123456test')
        User.objects.create(open_id='id1', system_user=user1)
        User.objects.create(open_id='id2', system_user=user2)
        User.objects.create(open_id='id3', system_user=user3)
        Ticket.objects.create(email='user1@test.com', unique_id='1', activity=act, status=Ticket.STATUS_VALID)
        Ticket.objects.create(email='user2@test.com', unique_id='2', activity=act, status=Ticket.STATUS_CANCELLED)
        Ticket.objects.create(email='user3@test.com', unique_id='3', activity=act, status=Ticket.STATUS_USED)

    def tearDown(self):
        Activity.objects.all().delete()
        User.objects.all().delete()
        Ticket.objects.all().delete()

    # 获取电子票的详情1
    def test_get_ticket_detail_valid(self):
        c = Client()
        res = c.get('/api/u/ticket/detail', {'openid': 'id1', 'ticket': '1'}).json()
        self.assertEqual(0, res['code'])
        self.assertEqual('act_published', res['data']['activityName'])

    # 获取电子票的详情2
    def test_get_ticket_detail_cancelled(self):
        c = Client()
        res = c.get('/api/u/ticket/detail', {'openid': 'id2', 'ticket': '2'}).json()
        self.assertEqual(0, res['code'])
        self.assertEqual('act_published', res['data']['activityName'])

    # 获取电子票的详情3
    def test_get_ticket_detail_used(self):
        c = Client()
        res = c.get('/api/u/ticket/detail', {'openid': 'id3', 'ticket': '3'}).json()
        self.assertEqual(0, res['code'])
        self.assertEqual('act_published', res['data']['activityName'])

    # 获取不属于你的电子票的详情
    def test_get_ticket_detail_not_yours(self):
        c = Client()
        res = c.get('/api/u/ticket/detail', {'openid': 'id2', 'ticket': '1'}).json()
        self.assertNotEqual(0, res['code'])

