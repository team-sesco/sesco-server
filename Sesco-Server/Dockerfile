FROM python:3.10

ENV FLASK_APP=manage:application
ENV FLASK_CONFIG=production
ENV FLASK_ENV=production

COPY ./ /home/Sesco-Server/
WORKDIR /home/Sesco-Server/

RUN pip install --upgrade pip && \
	pip install -r requirements.txt

EXPOSE 5000

CMD ["gunicorn","-w","2", \
	"--bind","0.0.0.0:5000", \
	"--log-level", "debug", \
	"--access-logfile", "-", \
	"--access-logformat", "%(h)s [ACCESS] %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s '%(f)s' '%(a)s'", \
	"manage:application"]