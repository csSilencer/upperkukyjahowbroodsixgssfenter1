FROM python:3

COPY --chown=root:root . /home/root/upperkuk/

WORKDIR /home/root/upperkuk
RUN pip install -r requirements.txt
ENTRYPOINT ["/home/root/upperkuk/docker_entrypoint.sh"]
