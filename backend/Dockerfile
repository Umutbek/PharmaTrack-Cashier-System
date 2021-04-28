FROM python:3.9
ENV PYTHONBUFFERED=1
WORKDIR /usr/src/app/backend
COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .
RUN chmod +x /usr/src/app/backend/