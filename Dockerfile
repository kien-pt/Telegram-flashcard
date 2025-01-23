FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.10 python3.10-venv python3.10-dev python3-pip libgl1-mesa-glx && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

WORKDIR /flashcard

COPY /requirements.txt .

RUN python3 -m venv /opt/flashcard/venv && \
    . /opt/flashcard/venv/bin/activate && \
    pip install --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["/opt/flashcard/venv/bin/python", "main.py"]