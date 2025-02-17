FROM python:3.12
WORKDIR /Z-Technologies
COPY requirements.txt /Z-Technologies
RUN pip3 install --upgrade pip -r requirements.txt
COPY . /Z-Technologies
EXPOSE 5000