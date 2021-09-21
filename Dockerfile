FROM registry.access.redhat.com/ubi8/python-38:1-68

ADD . /opt/app-root/src/ 

RUN pip install -U "pip>=19.3.1" && \ 
    pip install -r requirements.txt

WORKDIR /opt/app-root/src

ENTRYPOINT ["python", "run.py"]
CMD ["-d"]
