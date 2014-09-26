# makefile
# use with sudo and install pycharm please

install:
	wget https://bootstrap.pypa.io/get-pip.py
	python get-pip.py
	rm get-pip.py
	pip install flask
	pip install sqlalchemy
	pip install mongokit
	pip install pymongo
	apt-get install mongodb

run:
	python ./webapp/flaskr.py