FROM python:3.12.0-slim

RUN useradd -ms /bin/bash python

RUN pip install pdm

USER python

WORKDIR /home/python/app

RUN echo "source /home/python/app/.venv/bin/activate" >> ~/.bashrc

CMD [ "tail", "-f", "/dev/null" ]