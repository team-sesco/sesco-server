import requests


def authorize(
    client_id: str, 
    client_secret: str,
    redirect_uri: str, 
    code: str
):
    return requests.post(
        "https://kauth.kakao.com/oauth/token",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache",
        },
        data={
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "code": code,
        },
    ).json()


def get_userinfo(access_token: str):
    return requests.post(
        "https://kapi.kakao.com/v2/user/me",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache",
            "Authorization": "Bearer " + access_token
        },
    ).json()


if __name__ == "__main__":
    ...
