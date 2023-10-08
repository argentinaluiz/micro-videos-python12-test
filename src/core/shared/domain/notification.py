from dataclasses import dataclass, field
from typing import List
from pydantic import ValidationError

@dataclass(slots=True, kw_only=True)
class Notification:
    errors: List[ValidationError] = field(default_factory=list)

    def add_error(self, error: ValidationError):
        self.errors.append(error)

    def has_errors(self):
        return len(self.errors) > 0

    def copy_errors(self, notification: 'Notification'):
        self.errors.extend(notification.errors)
