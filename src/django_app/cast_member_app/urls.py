
from django.urls import path
from django_app.cast_member_app.api import CastMemberController
from django_app.ioc_app.containers import container


def __init_cast_member_controller():
    return {
        'create_use_case': container.cast_member.create_cast_member_use_case,
        'list_use_case': container.cast_member.list_cast_members_use_case,
        'get_use_case': container.cast_member.get_cast_member_use_case,
        'update_use_case': container.cast_member.update_cast_member_use_case,
        'delete_use_case': container.cast_member.delete_cast_member_use_case,
    }


urlpatterns = [
    path('cast-members/', CastMemberController.as_view(
        **__init_cast_member_controller()
    )),
    path('cast-members/<cast_member_id>/', CastMemberController.as_view(
        **__init_cast_member_controller()
    )),
]
