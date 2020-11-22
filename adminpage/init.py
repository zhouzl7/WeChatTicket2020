# #!/usr/bin/env python
# # encoding: utf-8
# """
# @author: zhouzl
# @contact: zzl850783164@163.com
# @software:
# @file: init.py
# @time: 2020/11/22 13:08
# @desc:
# """
# import datetime
#
# from django.utils import timezone
# from django.contrib.auth.models import User as SystemUser
#
# from wechat.models import Activity, Ticket, User
#
#
# def init():
#     act = Activity.objects.create(id=130, name='act_published', key='key', place='place',
#                                   description='description',
#                                   start_time=timezone.now() + datetime.timedelta(1000),
#                                   pic_url="url",
#                                   end_time=timezone.now() + datetime.timedelta(2000),
#                                   book_start=timezone.now() - datetime.timedelta(500),
#                                   book_end=timezone.now() + datetime.timedelta(500),
#                                   total_tickets=1000, status=Activity.STATUS_PUBLISHED, remain_tickets=1000)
#     user1 = SystemUser.objects.create_user('user1', 'user1@test.com', '123456test')
#     user2 = SystemUser.objects.create_user('user2', 'user2@test.com', '123456test')
#     user3 = SystemUser.objects.create_user('user3', 'user3@test.com', '123456test')
#     User.objects.create(open_id='id1', system_user=user1)
#     User.objects.create(open_id='id2', system_user=user2)
#     User.objects.create(open_id='id3', system_user=user3)
#     Ticket.objects.create(email='user1@test.com', unique_id='11', activity=act, status=Ticket.STATUS_VALID)
#     Ticket.objects.create(email='user2@test.com', unique_id='12', activity=act, status=Ticket.STATUS_CANCELLED)
#     Ticket.objects.create(email='user3@test.com', unique_id='13', activity=act, status=Ticket.STATUS_USED)
