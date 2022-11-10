# SE. SCO SERVER

세스코 백엔드 API 서버



## Dependency

- python 3.9.x 이상

```shell
$ cd ~/
$ pip install -r sesco-server/requirement.txt
```



## Environments

```shell
Sesco_MONGODB_NAME="sesco"
Sesco_MONGODB_URI="mongodb://localhost:27017"
Sesco_SECRET_KEY="sesco-secret-key"

FLASK_APP="manage:application"
FLASK_CONFIG="development"
FLASK_ENV="development"

# 다음 값들은 다 임시 값 입니다.
Sesco_S3_ACCESS_KEY_ID="AKIATI3XF54RUQDZRCPI"
Sesco_S3_BUCKET_NAME="sesco-asset"
Sesco_S3_SECRET_ACCESS_KEY="DxbABmRWKuw4gYOEIb1883bNR9/pa31NZkI/Dmm12&Un"

GOOGLE_OAUTH_CLIENT_ID="3118462628120-qmv8pa3i1o2bo4usb1llksu3b1d7pmkh7.apps.googleusercontent.com"
GOOGLE_OAUTH_CLIENT_SECRET="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M"
GOOGLE_OAUTH_REDIRECT_URI="https://sesco.scof.link/api/auth/oauth/google"

KAKAO_OAUTH_CLIENT_ID="d111bl24u8bb1f1ihpiN1ih4p1s4b8"
KAKAO_OAUTH_CLIENT_SECRET="KH1bfwouAOBREOPI21835JKBLDFS"
KAKAO_OAUTH_REDIRECT_URI="https://sesco.scof.link/api/auth/oauth/kakao"

APPLE_OAUTH_TEAM_ID="G621H88H34"
APPLE_OAUTH_CLIENT_ID="me.sesco.serviceid"
APPLE_OAUTH_REDIRECT_URI="https://sesco.scof.link/api/auth/oauth/apple"
APPLE_OAUTH_KEY_ID="4Z195GR9H6"
APPLE_OAUTH_PRIVATE_KEY="Sesco-Server/Sesco-Server/apple-oauth.pem"
```



## Docker Image build

```
$ cd ~/
$ docker build --no-cache -t sesco .
```



## CLI Commands

```shell
// 연결된 DB 설정 초기화 커맨드
$ flask db-init
```