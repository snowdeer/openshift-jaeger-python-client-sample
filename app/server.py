import os
from flask import Flask, jsonify
import logging
import time
from jaeger_client import Config

HOST_NAME = os.environ.get('OPENSHIFT_APP_DNS', 'localhost')
APP_NAME = os.environ.get('OPENSHIFT_APP_NAME', 'flask')
IP = os.environ.get('OPENSHIFT_PYTHON_IP', '127.0.0.1')
PORT = int(os.environ.get('OPENSHIFT_PYTHON_PORT', 8080))
HOME_DIR = os.environ.get('OPENSHIFT_HOMEDIR', os.getcwd())

app = Flask(__name__)


log_level = logging.DEBUG
logging.getLogger('').handlers = []
logging.basicConfig(format='%(asctime)s %(message)s', level=log_level)

config = Config(
    config={ # usually read from some yaml config
        'sampler': {
            'type': 'const',
            'param': 1,
        },
        'logging': True,
    },  
    service_name='snowdeer-jaeger-python-client',
)
# this call also sets opentracing.tracer
tracer = config.initialize_tracer()

@app.route('/')
def index():
    #tracer = config.initialize_tracer()
    with tracer.start_span('TestSpan') as span:
        span.log_event('test message', payload={'life': 42})

        with tracer.start_span('ChildSpan', child_of=span) as child_span:
            span.log_event('down below')

    time.sleep(2)   # yield to IOLoop to flush the spans - https://github.com/jaegertracing/jaeger-client-python/issues/50
    #tracer.close()  # flush any buffered spans

    return jsonify({
        'purpose': 'Jaeger Tracing Test',
        'host_name': HOST_NAME,
        'app_name': APP_NAME,
        'ip': IP,
        'port': PORT,
        'home_dir': HOME_DIR
    })


@app.route('/hello/<name>')
def hello(name):
    #tracer = config.initialize_tracer()
    with tracer.start_span('Hello') as span:
        span.log_event('hello message', payload={'life': 42})

        with tracer.start_span(name, child_of=span) as child_span:
            span.log_event('down below')

    time.sleep(2)   # yield to IOLoop to flush the spans - https://github.com/jaegertracing/jaeger-client-python/issues/50
    #tracer.close()  # flush any buffered spans

    return 'Hello, {}'.format(name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
