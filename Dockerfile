FROM python:3.11.6-slim

RUN apt update -y && apt install -y default-libmysqlclient-dev build-essential pkg-config

RUN useradd -ms /bin/bash python

RUN pip install pdm

USER python

WORKDIR /home/python/app

RUN echo "source /home/python/app/.venv/bin/activate" >> ~/.bashrc

CMD [ "tail", "-f", "/dev/null" ]