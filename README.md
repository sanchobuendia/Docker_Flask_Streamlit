# Docker Compose + Flask + Streamlit

docker-compose build 

docker-compose up 

#### run in detached mode using -d

docker-compose build -d

Initially, to run the Streamlit localy is more interesting to create a python venv and to install all packages that your application needs inside the venv. The purpose of this is to avoid conflicts with packages already installed on the machine.

## On MacOS

To create the python virtual environment first it is necessary to instal the virtualenv:

**pip install virtualenv**

after that, create a folder where the python venv will be installed:

**mkdir my_python_venv**

INSIDE my_project folder create a new virtualenv

**virtualenv env**

Activate virtualenv

**source env/bin/activate**

## On Windows 11

**mkdir my_python_venv**

INSIDE my_project folder create a new virtualenv

**py -m venv my_python_venv**

Activate virtualenv

**.\my_python_venv\Scripts\activate**

# Application structure

## Run localy

### Install requirements.txt 

Go to the application folder and install the requirements.txt 

pip install -r requirements.txt 

After that you can run the streamlit 

streamlit run app.py

The following message will appear

![image](images/link.png)

If the browser does not open automatically you must copy the link and place it in the browser.

# Using Streamlit Inside Docker Container

First of all it is necessary to have docker installed on the machine.

The first step is start the docker, after that we need to understand the Dockefile configuration. 

## docker 

docker build -t streamlitapp:latest .

docker run -p 8501:8501 streamlitapp:latest

## docker from Github

docker build github.com/sanchobuendia/Template_Streamlit.git 

## docker compose 

docker-compose build

docker-compose --verbose up






