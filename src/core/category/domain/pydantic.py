from typing import Annotated, Any, Type
from core.category.domain.entities import CategoryId
from core.shared.domain.value_objects import InvalidUuidException

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

class PydanticCategoryIdValidator:
    def __get_pydantic_core_schema__(
        self, source: Type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        # we can't call handler since it will fail for arbitrary types
        def validate(value: Any) -> Any:
            try:
                return value if isinstance(value, CategoryId) else CategoryId(value)
            except InvalidUuidException as ex:
                raise ValueError(str(ex)) from ex

        return core_schema.no_info_plain_validator_function(validate)

CategoryIdAnnotated = Annotated[CategoryId, PydanticCategoryIdValidator()]