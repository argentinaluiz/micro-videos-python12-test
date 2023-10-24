

from typing import Any, Dict
from django_app.config import ConfigService, config_service
from pydantic import ValidationError
import pytest

valid_data = config_service.model_dump()


def _all_params_except(*keys: str) -> Dict[str, Any]:
    return {k: valid_data[k] for k in valid_data if k not in keys}


class TestConfigService:

    @pytest.mark.parametrize('params,loc,msg', [
        pytest.param(
            _all_params_except('database_dsn'), 'database_dsn', 'Field required', id='without database_dsn'),
        pytest.param(
            {**valid_data, 'database_dsn': None}, 'database_dsn',
            'URL input should be a string or URL', id='database_dsn=None'),
        pytest.param(
            {**valid_data, 'database_dsn': ''}, 'database_dsn',
            'Input should be a valid URL, input is empty', id='database_dsn=""'),
        pytest.param(
            {**valid_data, 'database_dsn': 1}, 'database_dsn',
            'URL input should be a string or URL', id='database_dsn=1'),
        pytest.param(
            {**valid_data, 'database_dsn': 'fake_url'}, 'database_dsn',
            'Input should be a valid URL, relative URL without a base', id='database_dsn=fake_url'),
    ])
    def test_invalidation_database_dsn(self, params: Dict[str, Any], loc: str, msg: str):
        with pytest.raises(ValidationError) as exc_info:
            ConfigService(**params, _env_file=None)  # type: ignore
        assert exc_info.value.errors()[0]['loc'][0] == loc
        assert exc_info.value.errors()[0]['msg'] == msg

    @pytest.mark.parametrize('params,loc,msg', [
        pytest.param({**valid_data, 'debug': {}}, 'debug',
                     'Input should be a valid boolean', id='debug={}'),
        pytest.param({**valid_data, 'debug': 'aaaa'}, 'debug',
                     'Input should be a valid boolean, unable to interpret input', id='debug=aaaa'),
    ])
    def test_invalidation_debug(self, params: Dict[str, Any], loc: str, msg: str):
        with pytest.raises(ValidationError) as exc_info:
            ConfigService(**params, _env_file=None) # type: ignore
        assert exc_info.value.errors()[0]['loc'][0] == loc
        assert exc_info.value.errors()[0]['msg'] == msg

    @pytest.mark.parametrize('params,loc,msg', [
        pytest.param({**valid_data, 'installed_apps': {}}, 'installed_apps',
         'Input should be a valid list', id='installed_apps={}'),
        pytest.param({**valid_data, 'installed_apps': 1},
         'installed_apps', 'Input should be a valid list', id='installed_apps=1'),
    ])
    def test_installed_apps(self, params: Dict[str, Any], loc: str, msg: str):
        with pytest.raises(ValidationError) as exc_info:
            ConfigService(**params, _env_file=None) # type: ignore
        assert exc_info.value.errors()[0]['loc'][0] == loc
        assert exc_info.value.errors()[0]['msg'] == msg

    @pytest.mark.parametrize('params,loc,msg', [
        pytest.param({**valid_data, 'language_code': {}}, 'language_code',
         'Input should be a valid string', id='language_code={}'),
        pytest.param({**valid_data, 'language_code': 1},
         'language_code', 'Input should be a valid string', id='language_code=1'),
        pytest.param({**valid_data, 'language_code': ''},
         'language_code', 'String should have at least 1 characters', id='language_code=""'),
    ])
    def test_language_code(self, params: Dict[str, Any], loc: str, msg: str):
        with pytest.raises(ValidationError) as exc_info:
            ConfigService(**params, _env_file=None) # type: ignore
        assert exc_info.value.errors()[0]['loc'][0] == loc
        assert exc_info.value.errors()[0]['msg'] == msg

    @pytest.mark.parametrize('params,loc,msg', [
        pytest.param({**valid_data, 'middlewares_additional': {}}, 'middlewares_additional',
         'Input should be a valid list', id='middlewares_additional={}'),
        pytest.param({**valid_data, 'middlewares_additional': 1},
         'middlewares_additional', 'Input should be a valid list', id='middlewares_additional=1'),
    ])
    def test_middlewares_additional(self, params: Dict[str, Any], loc: str, msg: str):
        with pytest.raises(ValidationError) as exc_info:
            ConfigService(**params, _env_file=None) # type: ignore
        assert exc_info.value.errors()[0]['loc'][0] == loc
        assert exc_info.value.errors()[0]['msg'] == msg

    @pytest.mark.parametrize('params,loc,msg', [
        pytest.param({**valid_data, 'secret_key': {}}, 'secret_key',
         'Input should be a valid string', id='secret_key={}'),
        pytest.param({**valid_data, 'secret_key': 1},
         'secret_key', 'Input should be a valid string', id='secret_key=1'),
        pytest.param({**valid_data, 'secret_key': ''},
         'secret_key', 'String should have at least 1 characters', id='secret_key=""'),
    ])
    def test_secret_key(self, params: Dict[str, Any], loc: str, msg: str):
        with pytest.raises(ValidationError) as exc_info:
            ConfigService(**params, _env_file=None) # type: ignore
        assert exc_info.value.errors()[0]['loc'][0] == loc
        assert exc_info.value.errors()[0]['msg'] == msg