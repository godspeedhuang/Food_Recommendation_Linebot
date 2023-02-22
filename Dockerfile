FROM ubuntu:latest

# ADD . /Docker

WORKDIR /app
ADD . /app


# Install python 3.9 and other softwares
RUN apt-get update -y 
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y apt-utils python3.9 python3-pip vim git nano dos2unix wget curl locales sudo

# Update pip3
RUN DEBIAN_FRONTEND=noninteractive pip3 install --upgrade pip

# Change time zone
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata
RUN TZ=Asia/Taipei \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata

# Install required python modules
RUN pip3 install -r requirements.txt

CMD python3 app.py