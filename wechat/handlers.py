# -*- coding: utf-8 -*-
#
from wechat.wrapper import WeChatHandler
import re
from django.core import signing
from django.conf import settings
from django.template.loader import render_to_string
from multiprocessing import Pool
from wechat.models import *
from django.utils import timezone
from django.utils.text import slugify
from wechat.models import User, Ticket
from adminpage.decorator import bind_required
from django.db import transaction
from pprint import pprint
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

__author__ = "Epsirom"


class ErrorHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，服务器现在有点忙，暂时不能给您答复 T T')


class DefaultHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，没有找到您需要的信息:(')


class HelpOrSubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('帮助', 'help') or self.is_event('scan', 'subscribe') or \
               self.is_event_click(self.view.event_keys['help'])

    def handle(self):
        return self.reply_single_news({
            'Title': self.get_message('help_title'),
            'Description': self.get_message('help_description'),
            'Url': self.url_help(),
        })


class UnbindOrUnsubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('解绑') or self.is_event('unsubscribe')

    def handle(self):
        if self.user.system_user is not None and self.user.system_user.is_active:
            self.user.system_user.is_active = False
            self.user.system_user = None
            self.user.save()
            return self.reply_text('解绑成功')

        else:
            return self.reply_text('尚未绑定，无需解绑')


class BindAccountHandler(WeChatHandler):

    def check(self):
        return self.is_text('绑定') or self.is_event_click(self.view.event_keys['account_bind'])

    def handle(self):
        if self.user.system_user is not None and self.user.system_user.is_active:
            return self.reply_text("已经绑定账号，无需再次绑定")
        else:
            self.user.to_active = True
            self.user.save()
            return self.reply_text("请输入清华邮箱地址进行绑定")


class EmailHandler(WeChatHandler):

    def check(self):
        return self.user.to_active

    def handle(self):
        if self.is_msg_type("text") and re.match(r'^.+@(|mails?\.)tsinghua\.edu\.cn$', self.input['Content']) is not None:
            user, created = SystemUser.objects.get_or_create(username=self.user.open_id)
            user.email=self.input['Content']
            user.is_active = False
            user.save()
            self.user.system_user = user
            self.user.to_active = False
            self.user.save()

            REGISTRATION_SALT = getattr(settings, 'REGISTRATION_SALT', 'registration')
            activation_key = signing.dumps(obj=getattr(user, user.USERNAME_FIELD), salt=REGISTRATION_SALT)
            context = {
                'activation_key': activation_key,
                'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                'site':{
                    'name': 'Wechat Ticket',
                    'domain':settings.SITE_DOMAIN.split('/')[-1]
                }
            }
            context.update({
                'user': user
            })
            email_body_template = 'registration/activation_email.txt'
            email_subject_template = 'registration/activation_email_subject.txt'
            subject = render_to_string(email_subject_template, context)
            if subject.endswith('\n'):
                subject = subject[:-1]
            message = render_to_string(email_body_template, context)
            pool = Pool()
            pool.apply_async(user.email_user, (subject, message, settings.DEFAULT_FROM_EMAIL))
            #user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)

            return self.reply_text('验证邮件已发出，请查收')
        else:
            return self.reply_text("请输入格式正确的清华邮箱")


class BookEmptyHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['book_empty'])

    def handle(self):
        return self.reply_text(self.get_message('book_empty'))


class OperatorHandler(WeChatHandler):

    def check(self):
        return self.is_msg_type('text') and (re.match(r'^[0123456789+-/*() ]+$', self.input['Content']) != None)

    def handle(self):
        try:
            value = eval(self.input['Content'])
        except ZeroDivisionError:
            value = "除零错误"
        except:
            value = "请输入格式正确的表达式"
        return self.reply_text(value)


class ActivityListHandler(WeChatHandler):
    def check(self):
        return self.is_text('抢啥') or self.is_event_click(self.view.event_keys['book_what'])

    def handle(self):
        activities = Activity.objects.filter(
            status = Activity.STATUS_PUBLISHED,
            book_end__gt=timezone.now()
        ).order_by('book_start')[:10]
        articles = []
        if len(activities) == 0:
            return self.reply_text('暂无活动')

        for activity in activities:
            articles.append({
                'Title': activity.name,
                'Description': activity.description,
                'Url': settings.CONFIGS['SITE_DOMAIN'] + '/u/activity/?id=' + str(activity.id),
                'PicUrl': activity.pic_url
            })
        return self.reply_news(articles)


class BookActivityHandler(WeChatHandler):
    def check(self):
        #import pdb; pdb.set_trace()
        return self.is_msg_type('event') and (self.input['Event'] == 'CLICK') and (self.input['EventKey'].startswith(self.view.event_keys['book_header']))

    def handle(self):

        # 权限检查 @binding_required
        user = User.objects.get(open_id = self.input['FromUserName'])
        if (user.system_user is None) or (not user.system_user.is_active):
            return self.reply_text("请先绑定清华邮箱。回复“绑定”以开始。")

        # 取输入字段
        email = user.system_user.email
        eventKey = self.input['EventKey']
        actId = int(eventKey[17:]) # 17 == len(self.view.event_keys['book_header'])
        timestamp = self.input['CreateTime']

        # 已抢到票数量检查
        n = Ticket.objects.filter(
            status   = Ticket.STATUS_VALID,
            email    = email,
            activity = actId
        ).count()
        if n >= 1:
            return self.reply_text("一人只能抢一张，不要太贪心哟！")

        # 减库存
        with transaction.atomic():
            activity = Activity.objects.only("remain_tickets").select_for_update().get(id=actId)
            remainTickets = activity.remain_tickets
            if remainTickets > 0:
                activity.remain_tickets = remainTickets - 1
                activity.save()
        if remainTickets <= 0:
            return self.reply_text("没票了，你来晚啦 :(")

        # 生成票
        ticket = Ticket(
            email     = email,
            activity  = activity,
            status    = Ticket.STATUS_VALID,
            unique_id = slugify("-".join([
                str(actId),
                email,
                timestamp
            ]))
            #TODO: salted hashing
        )
        ticket.save()
        return self.reply_text("抢票成功！")


class ReturnTicketHandler(WeChatHandler):

    def check(self):
        return self.is_text_command('退票')

    def handle(self):
        activity_keys = self.input['Content'].split()[1:]
        if len(activity_keys) == 0:
            return self.reply_text('请按如下格式输入要退票的活动： 退票 活动名称')
        reply_msg = ''
        for activity_key in activity_keys:
            # 查票
            try:
                # 取消票
                with transaction.atomic():
                    ticket = Ticket.objects.select_for_update().get(
                        email=self.user.system_user.email,
                        activity__key=activity_key,
                        status=Ticket.STATUS_VALID
                    )
                    ticket.status = Ticket.STATUS_CANCELLED
                    ticket.save()

                # 加库存
                with transaction.atomic():
                    activity = Activity.objects.select_for_update().get(id=ticket.activity.id)
                    activity.remain_tickets += 1
                    activity.save()

                reply_msg += activity_key + '：退票成功\n'

            except ObjectDoesNotExist:
                reply_msg += activity_key+'：退票失败,你没有该活动的票，无需退票\n'

        return self.reply_text(reply_msg + '[微笑]')


class TicketListHandler(WeChatHandler):
    def check(self):
        return self.is_text("查票") or self.is_event_click(self.view.event_keys['get_ticket'])

    @bind_required
    def handle(self):
        tickets = Ticket.objects.filter(
            email=self.user.system_user.email,
            status=Ticket.STATUS_VALID,
            activity__end_time__gt=timezone.now()
        ).order_by('activity__start_time')[:10]
        articles = []
        if len(tickets) == 0:
            return self.reply_text('暂无电子票')
        for ticket in tickets:
            articles.append({
                'Title': "“{}”活动的电子票".format(ticket.activity.name),
                'Description': ticket.activity.description,
                'Url': settings.CONFIGS['SITE_DOMAIN'] + '/u/ticket/?openid=' + self.user.open_id + '&ticket=' + ticket.unique_id,
                'PicUrl': ''
            })
        return self.reply_news(articles)
