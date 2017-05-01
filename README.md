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

## Run the Initial Channel Preparation Script

Run the following command and press `CTRL+C` after a couple of seconds (you do not have to, but for the purpose of demonstrating the capabilities it is recommended):

	$ python3 py_json_streamer/random_value_updater.py

## Start the Flask App

Commands:

	$ export FLASK_APP=py_json_streamer/py_json_streamer.py
	$ flask run

## Start the Cache Updater Script

In another separate terminal, run the following command:

	$ cd $HOME/git/flask_service_streamer
	$ python3 py_json_streamer/random_value_updater.py

__Note__: To force no updates while the data is streamed to your client, you can press `CTRL+C` to stop this script and just restart it with the command above to resume updates.

# Command Line Testing

Assuming all steps under "Preparation" have been followed, you should now have three terminal windows open:

1. The Flask app listening on port 5000
2. The `memcached` program running in the foreground with verbose output
3. The `random_value_updater.py` script busy updating `memcached`

Now, open a fourth terminal.

## Subscribe to a number of channels:

Command:

	$ curl -v --cookie-jar ~/tmp/curl.cookies -b ~/tmp/curl.cookies -H "Content-Type: application/json" -X POST -d '{"Stream": ["X","Y","Z"]}' http://127.0.0.1:5000/api/v1.0/set_stream
	Note: Unnecessary use of -X or --request, POST is already inferred.
	*   Trying 127.0.0.1...
	* TCP_NODELAY set
	* Connected to 127.0.0.1 (127.0.0.1) port 5000 (#0)
	> POST /api/v1.0/set_stream HTTP/1.1
	> Host: 127.0.0.1:5000
	> User-Agent: curl/7.51.0
	> Accept: */*
	> Content-Type: application/json
	> Content-Length: 25
	> 
	* upload completely sent off: 25 out of 25 bytes
	* HTTP 1.0, assume close after body
	< HTTP/1.0 200 OK
	< Content-Type: text/html; charset=utf-8
	< Content-Length: 2
	* Added cookie SUBID="c79dd72bb0fa4e2b9c03601dbf0a8441" for domain 127.0.0.1, path /, expire 0
	< Set-Cookie: SUBID=c79dd72bb0fa4e2b9c03601dbf0a8441; Path=/
	< Server: Werkzeug/0.12.1 Python/3.6.1
	< Date: Mon, 01 May 2017 09:48:43 GMT
	< 
	* Curl_http_done: called premature == 0
	* Closing connection 0
	ok

## Get the Updates via Streaming JSON

Command:

	$ curl -v --cookie-jar ~/tmp/curl.cookies -b ~/tmp/curl.cookies -N http://127.0.0.1:5000/api/v1.0/stream
	*   Trying 127.0.0.1...
	* TCP_NODELAY set
	* Connected to 127.0.0.1 (127.0.0.1) port 5000 (#0)
	> GET /api/v1.0/stream HTTP/1.1
	> Host: 127.0.0.1:5000
	> User-Agent: curl/7.51.0
	> Accept: */*
	> Cookie: SUBID=c79dd72bb0fa4e2b9c03601dbf0a8441
	> 
	* HTTP 1.0, assume close after body
	< HTTP/1.0 200 OK
	< Content-Type: application/json
	< Connection: close
	< Server: Werkzeug/0.12.1 Python/3.6.1
	< Date: Mon, 01 May 2017 09:54:55 GMT
	< 
	{"X": 2, "Y": 85, "Z": 48}{"Updates": false}{"X": 0}{"Y": 0}{"Z": 0}{"X": 21}{"Y": 68}{"Y": 43}{"X": 49}{"Y": 37}{"Z": 54}

__Notes__: 

* Initially, the first `channels` ("X", "Y" and "Z") with their values (integers) will be displayed.
* Next, only updates to one or more of the channels will be displayed in separate JSON messages, but still within the same stream.
* If no updates are found within 10 seconds, a `{"Updates": false}` message will be streamed.
* The stream continues until you interrupt it with `CTRL+C`

# Web Browser JavaScript Testing

See `TODO`...

# TODO

I still need to implement the HTML page with the JavaScript to test `Oboe.js`