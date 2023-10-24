
from pathlib import Path
from typing import Annotated, Any, List
from pydantic import BeforeValidator, UrlConstraints, Field, MySQLDsn
from pydantic.fields import FieldInfo
import os
from pydantic_core import Url
# import dj_database_url
from pydantic_settings import BaseSettings, DotEnvSettingsSource, PydanticBaseSettingsSource, SettingsConfigDict

_ENV_FOLDER = Path(__file__).resolve().parent.parent.parent / 'envs'

APP_ENV = os.getenv('APP_ENV')


def parse_list(value: Any):
    if not isinstance(value, str):
        return value
    return [
        app.strip() for app in value.splitlines() if app.strip() != ''
    ] if value else []


class MyDotEnvSettingsSource(DotEnvSettingsSource):
    def prepare_field_value(self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool) -> Any:
        return value


SQLiteDsn = Annotated[
    Url,
    UrlConstraints(
        allowed_schemes=[
            'sqlite',
        ],
    ),
]


class ConfigService(BaseSettings):

    model_config = SettingsConfigDict(
        # `.env.prod` takes priority over `.env`
        env_file=(f'{_ENV_FOLDER}/.env', f'{_ENV_FOLDER}/.env.{APP_ENV}'),
    )

    database_dsn: MySQLDsn | SQLiteDsn
    debug: bool = Field(default=False)
    installed_apps: Annotated[List[str], BeforeValidator(
        parse_list)] = Field(min_length=1, default=[])
    language_code: str = Field(default='en-us', min_length=1)
    middlewares_additional: Annotated[List[str], BeforeValidator(parse_list)] = [
    ]
    secret_key: str = Field(min_length=1)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            MyDotEnvSettingsSource(
                settings_cls, env_file=dotenv_settings.env_file),
            file_secret_settings
        )
        # init_settings, env_settings, dotenv_settings, file_secret_settings


config_service = ConfigService(
    # _env_file=(f'{_ENV_FOLDER}/.env', f'{_ENV_FOLDER}/.env.{APP_ENV}'), # type: ignore
)
