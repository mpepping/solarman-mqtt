FROM registry.access.redhat.com/ubi8/python-38:1-68

LABEL maintainer "Martijn Pepping <martijn.pepping@automiq.nl>"
LABEL org.opencontainers.image.source https://github.com/mpepping/solarman-mqtt

ADD . /opt/app-root/src/ 

RUN pip install -U "pip>=19.3.1" && \ 
    pip install -r requirements.txt

WORKDIR /opt/app-root/src

ENTRYPOINT ["python", "run.py"]
CMD ["-d"]
