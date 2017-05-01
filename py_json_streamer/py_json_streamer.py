"""
Flask service to demonstrate how a web browser can subscribe to streaming
channel updates.
"""
import time, json, traceback, string, re, uuid
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
    def generate(session_id):
        """
        Streaming helper function as per http://flask.pocoo.org/docs/0.12/patterns/streaming/

        Args:
            session_id (string): The session ID to retrieve from memcached

        Returns:
            json: Yields (streams) the updated values, or returns an error (stream breaks!)
        """
        counter = 0
        channels = json.loads(memcached_client.get(session_id))
        for key in channels:
            yield json.dumps({'ChannelValueUpdate': {'{}'.format(key): channels[key]}})
        while True:
            counter += 1
            channels = json.loads(memcached_client.get(session_id))
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
    session_id = request.cookies.get('SUBID')
    session_data = {}
    if session_id:
        try:
            session_data = json.loads(memcached_client.get(session_id))
        except:
            print('EXCEPTION CAUGHT: {}'.format(traceback.format_exc()))
    channels = {}
    for key in session_data:
        search_test = re.search(KEY_PATTERN, key)
        if search_test:
            if search_test.group(1) in CHANNEL_KEYS:
                channels[search_test.group(1)] = session_data[key]
    if not channels:
        return json.dumps({'Error': 'Use set_stream first'})
    #return Response(generate(channels), mimetype='application/json')
    return Response(generate(session_id), mimetype='application/json')


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
    session_id = request.cookies.get('SUBID')
    response = make_response('ok')
    if not session_id:
        session_id = uuid.uuid4().hex
        response.set_cookie('SUBID', value=session_id)
    data_dict = {}
    session_data = {}
    try:
        # session['CAN_STREAM'] = False
        data_dict = json.loads(request.data)
        if 'Stream' in data_dict:
            if isinstance(data_dict['Stream'], list):
                for part in data_dict['Stream']:
                    if part in CHANNEL_KEYS:
                        # key = 'KEY_{}'.format(part)
                        # value = memcached_client.get(part)
                        session_data['KEY_{}'.format(part)] = memcached_client.get(part)
                        # session[key] = memcached_client.get(part)
                        # session['CAN_STREAM'] = True
        if data_dict:
            memcached_client.set(session_id, json.dumps(session_data), time=600)
    except:
        print('Failed to load data: {}'.format(traceback.format_exc()))
        response = make_response('error')
    return response

# EOF