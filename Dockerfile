FROM python:3.9-slim
COPY . /myassistant
WORKDIR /myassistant
RUN chmod +x /myassistant/entrypoint.sh
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ENTRYPOINT [ "/myassistant/entrypoint.sh" ]