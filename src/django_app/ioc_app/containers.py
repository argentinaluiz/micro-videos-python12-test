from dependency_injector import containers
from dependency_injector.providers import Container as DIContainer

from core.category.infra.container import CategoryContainer


class Container(containers.DeclarativeContainer):

    category: CategoryContainer = DIContainer(CategoryContainer) # type: ignore

container = Container()