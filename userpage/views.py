import requests
import re
from codex.baseerror import *
from codex.baseview import APIView
from wechat.models import *
import datetime


class ActivityDetail(APIView):
    def get(self):
        self.check_input('id')
        id = self.input['id']
        try:
            a = Activity.objects.get(id=id)
        except:
            raise ActivityNotFoundError("")
        if a.status != Activity.STATUS_PUBLISHED:
            raise ActivityNotPublishedError("")
        return {
            'startTime': a.start_time.timestamp(),
            'endTime': a.end_time.timestamp(),
            'bookStart': a.book_start.timestamp(),
            'bookEnd': a.book_end.timestamp(),
            'name': a.name,
            'key': a.key,
            'description': a.description,
            'place': a.place,
            'totalTickets': a.total_tickets,
            'picUrl': a.pic_url,
            'remainTickets': a.remain_tickets,
            'currentTime': datetime.datetime.now().timestamp()
        }


class TicketDetail(APIView):

    def get(self):
        self.check_input('openid')
        self.check_input('ticket')
        user = User.get_by_openid(self.input['openid'])
        try:
            ticket = Ticket.objects.get(email=user.system_user.email, unique_id=self.input['ticket'])
        except:
            raise TicketNotFoundError()
        return {
            'activityName': ticket.activity.name,
            'place': ticket.activity.place,
            'activityKey': ticket.activity.key,
            'uniqueId': ticket.unique_id,
            'startTime': ticket.activity.start_time.timestamp(),
            'endTime': ticket.activity.end_time.timestamp(),
            'currentTime': datetime.datetime.now().timestamp(),
            'status': ticket.status
        }
