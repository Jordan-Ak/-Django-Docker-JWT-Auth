FROM python:3.9-slim-buster
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE 1 
WORKDIR /code
COPY requirements.txt /code

RUN pip install -r requirements.txt 
COPY . /code
#RUN python manage.py makemigrations && python manage.py migrate
#EXPOSE 8000

#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# A question I'm wondering is why do python projects copy the dependencies first before the bulk code
# In this same dockerfile everything was copied at once and produced the same size image and ran well as well
#The answer to this is so that building becomes faster because the dependencies change less than source code