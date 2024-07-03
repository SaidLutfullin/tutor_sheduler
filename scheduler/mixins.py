from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.utils.decorators import method_decorator


class TeacherRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_tutor:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied("Permission denied - user is not a teacher")