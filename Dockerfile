FROM python:3.12.10

WORKDIR /src

COPY . /src

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000
EXPOSE 8501

CMD ["bash"]