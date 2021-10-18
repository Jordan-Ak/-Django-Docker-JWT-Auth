# Django-Docker-JWT-Auth
A Django Docker project using Authentication with JSON Web Tokens

This project was made using a Docker Container with Django Rest Framework.

## Requirements
* Django == 3.2.8
* Django Rest Framework == 3.12.4
* Swagger (API Documentation)
* Simple JSON Web Tokens (Authentication)
* Docker == 20.10.8
* Docker-Compose == 1.29.2
* Postgres Database(SQL Database)
* Celery (Used for Asynchronous Tasks)
* RabbitMq (Messaging Broker Used for facilitating asynchronous tasks) == 3.9 Management

To run this server up do the following: 
* Create your virtual environment, then type in your command line
```bash
pip install requirements.txt
```
Then Create a ".env" file with the following parameters filled:
* SECRET_KEY= {Your Django secret key}
* export DEBUG = True
* POSTGRES_DB= {Name of your postgres database, at least the name you want it to be}
* POSTGRES_USER={Name of the postgres user}
* POSTGRES_PASSWORD={Password of the postgres user}
* POSTGRES_PORT={port the postgres database should use; default is 5432}
* RABBITMQ_DEFAULT_USER={Name you want to use for the rabbitmq user}
* RABBITMQ_DEFAULT_PASS={The password of the rabbitmq user}
* CELERY_BROKER_USER={Name Celery would use to authenticate into Rabbitmq, so in short the same name as the RABBITMQ_DEFAULT_USER}
* CELERY_BROKER_PASS={Password celery would use to authenticate into Rabbitmq, so in short the same password as RABBITMQ_DEFAULT_PASS}
* EMAIL_HOST_USER={The host user to use to send smtp mails using gmail}
* EMAIL_HOST_PASSWORD={The password of the host email user}

* Lastly type in your command line
```bash
docker-compose up
```
* The final command would take a short while and everything would be up and running.
* Note: The current settings used in this project are not suitable for production!

## Project Rundown
* This project uses Docker and the Django rest framework to create an authentication system that consists of: Login, Logout, password change, password reset, profile editing, and profile viewing.
* It also makes use of asynchronous processing to ensure users do not have to wait for tasks such as: sending a mail before going about their business.
* It also features the use of a production database Postgresql.

## Design Considerations

### Why Docker?
* In a nutshell Docker is a tool that makes deployment and sharing software easier.
* Docker allows software to behave the same way everywhere the software is used, irrespective of the Operating System, or the software package deficiencies the host has.
* The only requirement is that the host machine has Docker installed on it and an internet connection.

* There are multiple ways to use the Docker tool to build a project but in this project the Dockerfile and Docker-Compose were used.
* In the Dockerfile you state how the image to be used by Docker should be built(Stating the Base Image and the commands to create the image)
* Docker Compose makes using Docker easier; you just have to state the applications you want to use and as far as they're in the same service docker automatically links them.
* The only downside I would add to Docker is that it adds a little complexity to development but honestly that complexity is nothing compared to the benefits is provides, and it is easy to use once you get the hang of it.
* Also the initial times spent on creating builds are easily offset by the headaches that would have normally been faced in deployment.

### What are JSON Web Tokens?
* JSON Web Tokens a.k.a JWTs are tokens that are used for the authentication of a user. They allow the server to know who a particular user is.
* What makes JWTs so useful is that they allow a server to identify a user without having to check the database. Which means they make scaling up easier.
* JWTs come in pairs: The Access token and the Refresh token.
* The Access Token is what allows the server know who a particular user is. The refresh token is used to grant a new Access Token and refresh token.
* In this particular project only the refresh tokens are checked against a database to check if they have been used before or if they are blacklisted.
* The problem with JWTs are that even after a user logs out their token is still active. What this means is that unless the token is expired it will still be valid.
* And blacklisting access tokens defeats the purpose of JWTs in the first place because checking access tokens against a database to check validity makes it the same as Token Authentication (What JWTs came to solve).
* One of the solutions to the above dilemma is to give access tokens a short expiry time and the refresh token a longer expiry time. Then also blacklisting refresh tokens as they are used.

### Asynchronous Tasks and RabbitMq
* Celery is the go to package to use for asynchronous tasks in Django.
* The only possible time consuming task in this project is sending emails, and users do not have to wait for the emails to send to go about their business.
* Without asynchronousity it takes on average 0.2- 0.3 seconds for a user to receive a response after sending a mail. With asynchronosity a user receives that response in 0.04- 0.06 seconds.
* Another beautiful thing about it is that whether the task succeeds or fails the user can still go about their business without receiving a 500 internal error code.
* RabbitMq fits into the picture as the specific technology firstly because on failed tasks it still re-executes them automatically. This same guarantee is not assured with its competitor Redis.
* Secondly RabbitMq is the recommended technology for Celery.
* The interface also looks nice ha ha!

### Postgresql
* This is honestly the go to database for production. Using the default sql lite is not scalable.
* Pg Admin is absent in this project; I did not implement it however the PSQL tool is availalble. I personally even prefer using the PSQL tool.

### Project Workflow
* Okay Below I will condense how everything works together:

** A User goes to the sign up page and then creates a user. If everything the user typed is valid(The serializers make this check), a new user is created and a verification mail is sent to the user's email.
** Django and postgres are linked via the settings in the Project.Settings (in my case deli.settings).
** The process of sending the mail is sent to the celery worker, and the celery worker authenticates at the RabbitMq container which it uses to process and execute the task.
** Other processes such as Resetting the user password involves the same kind of workflow. the Tokens generated for email verificaition and password reset are stored in the database witih expiry times.

That's it for the Project explanations.
Later on when I review this code again I will provide a review on the code produced in this repository.




