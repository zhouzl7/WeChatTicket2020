#!/usr/bin/env python
# encoding: utf-8
"""
@author: zhouzl
@contact: zzl850783164@163.com
@software: 
@file: unitTest.py
@time: 2020/11/21 17:25
@desc:
"""
from django.test import TestCase, Client
from wechat.models import Activity, User, Ticket
import xml.etree.ElementTree as etree
import json


test_open_id = '0247'
test_student_id = '2016013247'

url = '/wechat?signature=3e33bf9bd6c6cb24295d458d26237ac5bb79290a&timestamp=1540012665&nonce=1595522628&openid=0247'

book_xml_str = """
<xml>
    <ToUserName><![CDATA[toUser]]></ToUserName>
    <FromUserName><![CDATA[0247]]></FromUserName>
    <CreateTime>1540012625</CreateTime>
    <MsgType>text</MsgType>
    <MsgId>1293081923923912</MsgId>
    <Content><![CDATA[抢票 %s]]></Content>
</xml>
"""

withdraw_xml_str = """
<xml>
<ToUserName><![CDATA[toUser]]></ToUserName>
    <FromUserName><![CDATA[0247]]></FromUserName>
    <CreateTime>1540012632</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[退票 %s]]></Content>
    <MsgId>283218382818181</MsgId>
</xml> 
"""
act_available = {
    'id':1, 'name':'act1', 'key':'key1', 'place':'Hall', 'description':'available act', 'pic_url':'temp path',
    'start_time':'2018-11-10T20:00:00.000Z', 'end_time':'2018-11-12T20:00:00.000Z',
    'book_start':'2018-10-15T12:00:00.000Z', 'book_end':'2018-11-10T12:00:00.000Z',
    'total_tickets':1000, 'status':Activity.STATUS_PUBLISHED, 'remain_tickets':1000
}

act_pending = {
    'id':2, 'name':'act2', 'key':'key2', 'place':'Hall', 'description':'pending act', 'pic_url':'temp path',
    'start_time':'2018-11-10T20:00:00.000Z', 'end_time':'2018-11-12T20:00:00.000Z',
    'book_start':'2018-11-10T12:00:00.000Z', 'book_end':'2018-11-10T13:00:00.000Z',
    'total_tickets':1000, 'status':Activity.STATUS_PUBLISHED, 'remain_tickets':1000
}

act_bookended = {
    'id':3, 'name':'act3', 'key':'key3', 'place':'Hall', 'description':'ended act', 'pic_url':'temp path',
    'start_time':'2018-11-10T20:00:00.000Z', 'end_time':'2018-11-12T20:00:00.000Z',
    'book_start':'2018-10-01T12:00:00.000Z', 'book_end':'2018-10-01T13:00:00.000Z',
    'total_tickets':1000, 'status':Activity.STATUS_PUBLISHED, 'remain_tickets':1000
}

act_notickets = {
    'id':4, 'name':'act4', 'key':'key4', 'place':'Hall', 'description':'ended act', 'pic_url':'temp path',
    'start_time':'2018-11-10T20:00:00.000Z', 'end_time':'2018-11-12T20:00:00.000Z',
    'book_start':'2018-10-15T12:00:00.000Z', 'book_end':'2018-11-10T13:00:00.000Z',
    'total_tickets':1000, 'status':Activity.STATUS_PUBLISHED, 'remain_tickets':0
}


class BookTicketCase(TestCase):

    def setUp(self):
        User(open_id=test_open_id, student_id=test_student_id).save()
        self.cl = Client()
        Activity(**act_available).save()
        Activity(**act_pending).save()
        Activity(**act_bookended).save()
        Activity(**act_notickets).save()

    def tearDown(self):
        User.objects.all().delete()
        Activity.objects.all().delete()
        Ticket.objects.all().delete()

    def test_bookAvalible(self):
        res = self.cl.post(url, (book_xml_str % 'key1').encode('utf-8'), content_type='application/xml')
        res_str = res.content.decode('utf-8')
        root = etree.fromstring(res_str)
        self.assertEqual(root.find('Content').text, "成功！")
        self.assertEqual(999, Activity.objects.get(id=act_available['id']).remain_tickets)

    def test_bookTwice(self):
        self.cl.post(url, (book_xml_str % 'key1').encode('utf-8'), content_type='application/xml')
        res = self.cl.post(url, (book_xml_str % 'key1').encode('utf-8'), content_type='application/xml')
        res_str = res.content.decode('utf-8')
        root = etree.fromstring(res_str)
        self.assertEqual(root.find('Content').text, "您已经订过票了！")
        self.assertEqual(999, Activity.objects.get(id=act_available['id']).remain_tickets)

    def test_bookPending(self):
        res = self.cl.post(url, (book_xml_str % 'key2').encode('utf-8'), content_type='application/xml')
        res_str = res.content.decode('utf-8')
        root = etree.fromstring(res_str)
        self.assertEqual(root.find('Content').text, "抢票尚未开始！")
        self.assertEqual(1000, Activity.objects.get(id=act_pending['id']).remain_tickets)

    def test_bookEnded(self):
        res = self.cl.post(url, (book_xml_str % 'key3').encode('utf-8'), content_type='application/xml')
        res_str = res.content.decode('utf-8')
        root = etree.fromstring(res_str)
        self.assertEqual(root.find('Content').text, "抢票已经结束！")
        self.assertEqual(1000, Activity.objects.get(id=act_bookended['id']).remain_tickets)

    def test_noTickets(self):
        res = self.cl.post(url, (book_xml_str % 'key4').encode('utf-8'), content_type='application/xml')
        res_str = res.content.decode('utf-8')
        root = etree.fromstring(res_str)
        self.assertEqual(root.find('Content').text, "票已抢完！")
        self.assertEqual(0, Activity.objects.get(id=act_notickets['id']).remain_tickets)


class WithdrawTicketCase(TestCase):
    def setUp(self):
        User(open_id=test_open_id, student_id=test_student_id).save()
        self.cl = Client()
        Activity(**act_available).save()
        Activity(**act_pending).save()
        Activity(**act_bookended).save()

    def tearDown(self):
        User.objects.all().delete()
        Activity.objects.all().delete()
        Ticket.objects.all().delete()

    def test_withdraw(self):
        test1 = self.cl.post(url, (book_xml_str % 'key1').encode('utf-8'), content_type='application/xml')
        print(etree.fromstring(test1.content.decode('utf-8')).find('Content').text)
        self.assertEqual(999, Activity.objects.get(id=act_available['id']).remain_tickets)

        res = self.cl.post(url, (withdraw_xml_str % 'key1').encode('utf-8'), content_type='application/xml')
        res_str = res.content.decode('utf-8')
        root = etree.fromstring(res_str)
        self.assertEqual(root.find('Content').text, "退票成功！")
        self.assertEqual(1000, Activity.objects.get(id=act_available['id']).remain_tickets)

    def test_withdrawTwice(self):
        test1 = self.cl.post(url, (book_xml_str % 'key1').encode('utf-8'), content_type='application/xml')
        print(etree.fromstring(test1.content.decode('utf-8')).find('Content').text)
        self.assertEqual(999, Activity.objects.get(id=act_available['id']).remain_tickets)

        test1 = self.cl.post(url, (withdraw_xml_str % 'key1').encode('utf-8'), content_type='application/xml')
        print(etree.fromstring(test1.content.decode('utf-8')).find('Content').text)
        self.assertEqual(1000, Activity.objects.get(id=act_available['id']).remain_tickets)

        res = self.cl.post(url, (withdraw_xml_str % 'key1').encode('utf-8'), content_type='application/xml')
        res_str = res.content.decode('utf-8')
        root = etree.fromstring(res_str)
        self.assertEqual(root.find('Content').text, "您已退过票了！")
        self.assertEqual(1000, Activity.objects.get(id=act_available['id']).remain_tickets)


class TicketDetailCase(TestCase):

    def setUp(self):
        User(open_id=test_open_id, student_id=test_student_id).save()
        self.cl = Client()
        Activity(**act_available).save()
        Activity(**act_pending).save()
        Activity(**act_bookended).save()

    def tearDown(self):
        User.objects.all().delete()
        Activity.objects.all().delete()
        Ticket.objects.all().delete()

    def test_valid_ticket(self):
        self.cl.post(url, (book_xml_str % 'key1').encode('utf-8'), content_type='application/xml')

        unique_id = Ticket.objects.get(student_id=test_student_id, activity=Activity.objects.get(id=act_available['id'])).unique_id
        pack = {"openid": test_open_id, "ticket": unique_id}
        res = self.client.get("/api/u/ticket/detail", pack)
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['data']['status'], 1)

    def test_invalid_ticket(self):
        self.cl.post(url, (book_xml_str % 'key1').encode('utf-8'), content_type='application/xml')
        self.cl.post(url, (withdraw_xml_str % 'key1').encode('utf-8'), content_type='application/xml')

        unique_id = Ticket.objects.get(student_id=test_student_id,activity=Activity.objects.get(id=act_available['id'])).unique_id
        pack = {"openid": test_open_id, "ticket": unique_id}
        res = self.client.get("/api/u/ticket/detail", pack)
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['data']['status'], 0)