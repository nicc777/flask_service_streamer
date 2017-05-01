"""
Flask service to demonstrate how a web browser can subscribe to streaming
channel updates.
"""
import time, json, traceback, string, re
from flask import Flask, jsonify, Response, request, make_response, session
from memcache import Client


app = Flask(__name__)
app.secret_key = 'my secret!'
memcached_client = Client(["127.0.0.1:11211"], debug=1)
CHANNEL_KEYS = string.ascii_uppercase
KEY_PATTERN = re.compile(r"^KEY_(\w)$")


@app.route('/')
def home_page():
    """
    Dummy home page returning nothing.
    """
    return ''


@app.route('/api/v1.0/stream', methods=['GET'])
def get_stream():
    """
    Command line test:

    $ curl -v --cookie-jar ~/tmp/curl.cookies \
      -b ~/tmp/curl.cookies -N                \
      http://localhost:5000/api/v1.0/stream
    """
    def generate(channels):
        """
        Streaming helper function as per http://flask.pocoo.org/docs/0.12/patterns/streaming/

        Args:
            channels (dict): Subscribed channels with their initial values

        Returns:
            json: Yields (streams) the updated values, or returns an error (stream breaks!)
        """
        counter = 0
        for key in channels:
            yield json.dumps({'ChannelValueUpdate': {'{}'.format(key): channels[key]}})
        while True:
            counter += 1
            if channels:
                for key in channels:
                    cached_value = memcached_client.get(key)
                    if cached_value != channels[key]:
                        channels[key] = cached_value
                        counter = 0
                        yield json.dumps({'ChannelValueUpdate': {'{}'.format(key): cached_value}})
            if counter > 9:
                counter = 0
                yield json.dumps({'Updates': None})
            time.sleep(1)
    channels = {}
    if 'CAN_STREAM' in session:
        if session['CAN_STREAM']:
            for key in session:
                search_test = re.search(KEY_PATTERN, key)
                if search_test:
                    if search_test.group(1) in CHANNEL_KEYS:
                        channels[search_test.group(1)] = session[key]
    if not channels:
        return json.dumps({'Error': 'Use set_stream first'})
    return Response(generate(channels), mimetype='application/json')


@app.route('/api/v1.0/set_stream', methods=['POST'])
def set_stream():
    '''
    Example (subscribe to value updates for streams A and B):
    $ curl -i --cookie-jar ~/tmp/curl.cookies     \
      -H "Content-Type: application/json"         \
      -X POST -d '{"Stream": ["A", "B"]}'         \
      http://localhost:5000/api/v1.0/set_stream

    We need the cookie jar for the get requests later...
    '''
    data_dict = {}
    try:
        session['CAN_STREAM'] = False
        data_dict = json.loads(request.data)
        if 'Stream' in data_dict:
            if isinstance(data_dict['Stream'], list):
                for p in data_dict['Stream']:
                    if p in CHANNEL_KEYS:
                        key = 'KEY_{}'.format(p)
                        session[key] = memcached_client.get(p)
                        session['CAN_STREAM'] = True
    except:
        print('Failed to load data: {}'.format(traceback.format_exc()))
        return 'error'
    return 'ok'

# EOF