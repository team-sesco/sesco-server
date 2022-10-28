"""flask_validation_extended Validator Custom rules"""
import os
from datetime import datetime
from flask_validation_extended.rules import ValidationRule
from bson.objectid import ObjectId
from bson.errors import InvalidId
from json import loads


class ObjectIdValid(ValidationRule):
    """ObjectId Validation"""
    @property
    def types(self):
        return str

    def invalid_str(self):
        return "This isn't ObjectId Format."

    def is_valid(self, data) -> bool:
        try:
            ObjectId(data)
            return True
        except InvalidId:
            return False


class DatetimeFormatValid(ValidationRule):
    """YYY-MM-DD HH:MM:SS format validation"""
    @property
    def types(self):
        return str

    def invalid_str(self):
        return "This isn't YYYY-MM-DD Format."

    def is_valid(self, data) -> bool:
        try:
            datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
            return True
        except ValueError:
            return False


class ListValid(ValidationRule):
    """Character-List format validation"""
    @property
    def types(self):
        return str

    def invalid_str(self):
        return "This isn't Character-List (Ex, '[\"\", \"\"]') Format."

    def is_valid(self, data) -> bool:
        try:
            data = loads(data)
            if isinstance(data, list):
                for inst in data:
                    if not isinstance(inst, str):
                        return False
                return True
            return False
        except ValueError:
            return False


class StrDictListValid(ValidationRule):
    """Character-Dict-List format validation"""
    @property
    def types(self):
        return str

    def invalid_str(self):
        return "This isn't Character-Dict-List (Ex, '[{}, {}, {}]') Format."

    def is_valid(self, data) -> bool:
        try:
            data = loads(data)
        except ValueError:
            return False
        if isinstance(data, list):
            for inst in data:
                if not isinstance(inst, dict):
                    return False
            return True
        return False


class DictListValid(ValidationRule):
    """Dict-List format validation"""
    @property
    def types(self):
        return list

    def invalid_str(self):
        return "This isn't Dict-List (Ex, [{}, {}, {}]) Format."

    def is_valid(self, data) -> bool:
        if isinstance(data, list):
            for inst in data:
                if not isinstance(inst, dict):
                    return False
            return True
        return False
