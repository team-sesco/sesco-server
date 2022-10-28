FROM python:3.9-alpine as base

COPY ./ /home/Sesco-Server/
WORKDIR /home/Sesco-Server/

RUN apk update && \
	apk add --update --no-cache gcc libressl-dev \
	musl-dev libffi-dev jpeg-dev zlib-dev && \
	pip install --upgrade pip && \
	pip wheel --wheel-dir=/home/Sesco-Server/wheels -r requirements.txt

FROM python:3.9-alpine

ENV FLASK_APP=manage:application
ENV FLASK_CONFIG=production
ENV FLASK_ENV=production

COPY --from=base /home/Sesco-Server/ /home/Sesco-Server/

WORKDIR /home/Sesco-Server/

RUN apk update && \
	apk add --update --no-cache bash curl jpeg-dev && \
	mkdir /home/assets && \
	pip install --no-index \
	--find-links=/home/Sesco-Server/wheels \
	-r requirements.txt && \
	rm -rf /home/Sesco-Server/wheels

EXPOSE 5000

CMD ["gunicorn","-w","2", \
	"--bind","0.0.0.0:5000", \
	"--log-level", "debug", \
	"--access-logfile", "-", \
	"--access-logformat", "%(h)s [ACCESS] %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s '%(f)s' '%(a)s'", \
	"manage:application"]