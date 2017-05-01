# An Example of Using Flask to Stream JSON

This is a sample application to demonstrate an implementation using [flask](http://flask.pocoo.org).

## Dependencies

Python:

* Flask
* [python3-memcached](https://pypi.python.org/pypi/python3-memcached/1.51)


Other:

* [Memcached](https://memcached.org) - Used to store values to channels we will subscribe to as well as the per session channel subscription information.
* [Oboe.js](http://oboejs.com) - Used to demonstrate the streaming features in a web browser

To inspect memcached, refer to [this useful page](https://www.darkcoding.net/software/memcached-list-all-keys/)

# Status

This project is still in early development, so please hang on while I complete the example to a working/usable state...

# Preparation

For command examples, I will be assuming you are using Linux or Mac OSX. Windows users will have to figure this out or you can submit your own steps to me to add to this README.

## Install memcached

Look at the memcached documentation in order to obtain a copy for your OS.

## Clone the repository and create a Python virtual environment

Assuming you are cloning to the `git` directory in your home directory, run the following commands:

	$ mkdir $HOME/git
	$ cd $HOME/git
	$ git clone https://github.com/nicc777/flask_service_streamer.git
	$ cd flask_service_streamer/
	$ virtualenv -p python3 venv

## Activate the Virtual Environment and Install Python Dependencies

Commands:

	$ . venv/bin/activate
	(venv)$ pip3 install Flask python3-memcached

## Start Memcached in a Separate Terminal

Command:

	$ memcached -vv

## Run the Initial Channel Preperation Script

Run the following command and press CTRL+C after a couple of seconds (you do not have to, but for the purpose of demonstrating the capabilities it is recommended):

	$ python3 py_json_streamer/random_value_updater.py

## Start the Flask App

Commands:

	$ export FLASK_APP=py_json_streamer/py_json_streamer.py
	$ flask run


