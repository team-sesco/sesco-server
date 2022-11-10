"""
# S3 Object Path
- 모든 S3 파일 저장 경로는 이곳에서 관리하도록 함.
- path 구조 및 코드 구조는 계속 고민중.
"""
from config import config

PATHS = {
    # 프로필 이미지
    'profile': "profile/%s",
    # 탐지 이미지
    'detection': "detection/%s",
    # 문의
    'help': "help/%s",
    # 언노운이 생기질 않길 바랍니다...
    'unknown': "unknown/%s",
}


def make_path(type: str, filename: str):
    if type not in PATHS:
        return PATHS['unknown'] % filename
    return PATHS[type] % filename
