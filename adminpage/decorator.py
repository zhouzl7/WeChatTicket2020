from codex.baseerror import AuthenticationError


def admin_login_required(function=None):
    def wrapper(obj, *args, **kwargs):
        if obj.request.user.is_superuser:
            return function(obj, *args, **kwargs)
        raise AuthenticationError()

    return wrapper


def bind_required(function=None):
    def wrapper(obj, *args, **kwargs):
        if obj.user.system_user is not None:
            return function(obj, *args, **kwargs)
        return obj.reply_text("请先绑定（可输入绑定进行邮箱绑定）")

    return wrapper
