from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer
from core.cast_member.application.use_cases import (
    CreateCastMemberUseCase, DeleteCastMemberUseCase, GetCastMemberUseCase, ListCastMembersUseCase, UpdateCastMemberUseCase
)

from core.cast_member.infra.repositories import CastMemberInMemoryRepository
from django_app.cast_member_app.models import CastMemberDjangoRepository


class CastMemberContainer(DeclarativeContainer):
    cast_member_repository_in_memory = providers.Singleton( #type: ignore
        CastMemberInMemoryRepository) #type: ignore

    cast_member_repository_django_orm = providers.Singleton(
        CastMemberDjangoRepository)

    list_cast_members_use_case = providers.Singleton(
        ListCastMembersUseCase,
        cast_member_repo=cast_member_repository_django_orm
    )

    get_cast_member_use_case = providers.Singleton(
        GetCastMemberUseCase,
        cast_member_repo=cast_member_repository_django_orm
    )

    create_cast_member_use_case = providers.Singleton(
        CreateCastMemberUseCase,
        cast_member_repo=cast_member_repository_django_orm
    )

    update_cast_member_use_case = providers.Singleton(
        UpdateCastMemberUseCase,
        cast_member_repo=cast_member_repository_django_orm
    )

    delete_cast_member_use_case = providers.Singleton(
        DeleteCastMemberUseCase,
        cast_member_repo=cast_member_repository_django_orm
    )
