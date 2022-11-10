from string import ascii_letters
from random import choice
from faker import Faker
from faker.providers import internet


def get_fake():
    fake = Faker('ko_KR')
    fake.add_provider(internet)
    return fake


def snake2pascal(string: str):
    """String Convert: snake_case to PascalCase"""
    return (
        string
        .replace("_", " ")
        .title()
        .replace(" ", "")
    )


def pascal2snake(string: str):
    """String Convert: PascalCase to snake_case"""
    return ''.join(
        word.title() for word in string.split('_')
    )


def get_random_id(length=15):
    """Get Random String for Identification"""
    string_pool = ascii_letters + "0123456789"
    rand_string = [choice(string_pool) for _ in range(length)]
    return "".join(rand_string)


def remove_none_value(document: dict):
    """입력받은 dict의 None value 데이터를 제거한채 반환"""
    keys = list(document.keys())
    for key in keys:
        if document[key] is None:
            del document[key]
    return document