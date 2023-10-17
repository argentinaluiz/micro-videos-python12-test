from pydantic import BeforeValidator


StrNotEmpty = BeforeValidator(lambda v: None if v == '' else v)