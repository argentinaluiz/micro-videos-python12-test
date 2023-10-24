from dataclasses import dataclass, field
from typing import Dict, List, cast


@dataclass(slots=True, kw_only=True)
class Notification:
    errors: Dict[str, List[str] | str] = field(default_factory=dict)

    def add_error(self, error: str, _field: str | None = None):
        if _field:
            errors = cast(List[str], self.errors.get(_field, []))
            if error not in errors:
                errors.append(error)
            self.errors[_field] = errors
        else:
            self.errors[error] = error

    def copy_errors(self, notification: 'Notification'):
        for _field, value in notification.errors.items():
            self.set_error(value, _field)

    def set_error(self, error: str | List[str], _field: str | None = None):
        if _field:
            self.errors[_field] = error if isinstance(error, list) else [error]
        else:
            if isinstance(error, list):
                for value in error:
                    self.errors[value] = value
                return
            self.errors[error] = error

    def has_errors(self):
        return len(self.errors) > 0
