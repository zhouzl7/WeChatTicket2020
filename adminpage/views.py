from .decorator import admin_login_required
from codex.baseerror import *
from codex.baseview import APIView
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify
from operator import indexOf
from wechat.models import *
from wechat.views import CustomWeChatView
from WeChatTicket import settings
import datetime
import os


class ActivityList(APIView):
    def ActivityListItem(self, a):
        return {
            'startTime': a.start_time.timestamp(),
            'endTime': a.end_time.timestamp(),
            'bookStart': a.book_start.timestamp(),
            'bookEnd': a.book_end.timestamp(),
            'id': a.id,
            'name': a.name,
            'description': a.description,
            'place': a.place,
            'currentTime': datetime.datetime.now().timestamp(),
            'status': a.status
        }

    @admin_login_required
    def get(self):
        result = []
        for a in Activity.objects.all():
            if (a.status != Activity.STATUS_DELETED):
                result.append(self.ActivityListItem(a))
        return result


class ActivityDelete(APIView):
    @admin_login_required
    def post(self):
        self.check_input('id')
        Activity.objects.filter(
            id=self.input['id']
        ).update(
            status=Activity.STATUS_DELETED
        )

        return


class ActivityCreate(APIView):
    @admin_login_required
    def post(self):
        new_dict = {}
        keys = {
            'name': 'name',
            'key': 'key',
            'place': 'place',
            'description': 'description',
            'picUrl': 'pic_url',
            'startTime': 'start_time',
            'endTime': 'end_time',
            'bookStart': 'book_start',
            'bookEnd': 'book_end',
            'totalTickets': 'total_tickets',
            'status': 'status'
        }
        for key in keys:
            self.check_input(key)
            # all fields required
            new_dict[keys[key]] = self.input[key]
        new = Activity(**new_dict)

        new.remain_tickets = new.total_tickets
        new.save(force_insert=True)

        return new.id


class ActivityDetail(APIView):
    @admin_login_required
    def get(self):
        self.check_input('id')
        id = self.input['id']
        try:
            a = Activity.objects.get(id=id)
        except:
            raise ActivityNotFoundError("")
        return {
            'name': a.name,
            'key': a.key,
            'description': a.description,
            'startTime': a.start_time.timestamp(),
            'endTime': a.end_time.timestamp(),
            'place': a.place,
            'bookStart': a.book_start.timestamp(),
            'bookEnd': a.book_end.timestamp(),
            'totalTickets': a.total_tickets,
            'picUrl': a.pic_url,
            'bookedTickets': len(Ticket.objects.filter(activity=a, status=Ticket.STATUS_VALID)),
            'usedTickets': len(Ticket.objects.filter(activity=a, status=Ticket.STATUS_USED)),
            'currentTime': datetime.datetime.now().timestamp(),
            'status': a.status
        };

    @admin_login_required
    def post(self):
        self.check_input('id')
        id = self.input['id']

        try:
            old = Activity.objects.get(id=id)
            old_total_tickets = old.total_tickets
        except:
            raise ActivityNotFoundError("")

        new = {}
        keys = {
            'name': 'name',
            'place': 'place',
            'description': 'description',
            'picUrl': 'pic_url',
            'startTime': 'start_time',
            'endTime': 'end_time',
            'bookStart': 'book_start',
            'bookEnd': 'book_end',
            'totalTickets': 'total_tickets',
            'status': 'status',
        }
        for key in keys:
            if key in self.input:
                # all fields assumed optional and appliable
                new[keys[key]] = self.input[key]

        activity = Activity.objects.filter(id=id).update(**new)
        for a in activity:
            a.remain_tickets += int(self.input['total_tickets']) - old_total_tickets
            a.save()

        return


class AdminLogoutView(APIView):
    def post(self):
        logout(self.request)
        return


class ImageUpload(APIView):
    def get_filename(self, filename):
        stamp = str(int(datetime.datetime.now().timestamp() * 1000))
        name, ext = os.path.splitext(filename)
        return "".join([
            str(int(datetime.datetime.now().timestamp() * 1000)),
            "_",
            slugify(name),
            ext
        ])

    @admin_login_required
    def post(self):
        image = self.request.FILES['image']
        filename = self.get_filename(image.name)
        with open('static/upload/' + filename, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
        url = settings.CONFIGS['SITE_DOMAIN'] + '/upload/' + filename
        return url


class AdminLoginView(APIView):

    @admin_login_required
    def get(self):
        pass

    def post(self):
        self.check_input('username')
        self.check_input('password')

        user = authenticate(
            username=self.input['username'],
            password=self.input['password']
        )

        if user is not None and user.is_superuser:
            login(self.request, user)
            return
        raise PasswordError()


class ActivityMenu(APIView):
    activity_ids = []

    def activity_menu_item(self, a):
        try:
            index = indexOf(self.activity_ids, int(a.id)) + 1
        except:
            index = 0
        return {
            'id': a.id,
            'name': a.name,
            'menuIndex': index
        }

    @admin_login_required
    def get(self):
        self.activity_ids = CustomWeChatView.get_activity_ids()
        result = []
        for a in Activity.objects.all():
            if a.status == Activity.STATUS_PUBLISHED:
                result.append(self.activity_menu_item(a))
        return result

    @admin_login_required
    def post(self):
        activities = list()
        for id in self.input:
            activities.append(Activity.objects.get(id=id))
        CustomWeChatView.update_menu(activities)


class ActivityCheckin(APIView):
    @admin_login_required
    def post(self):
        self.check_input('actId')
        self.check_input('ticket');
        try:
            actId = self.input['actId']
            ticket = self.input['ticket']
            ticket = Ticket.objects.get(
                activity=actId,
                unique_id=self.input['ticket']
            )
        except ObjectDoesNotExist:
            raise TicketNotFoundError()

        ticket.status = Ticket.STATUS_USED
        ticket.save()
        return {
            'ticket': ticket.unique_id,
            'email': ticket.email
        }
