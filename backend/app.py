from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from database import db, init_db
from models import Gift
import os
from dotenv import load_dotenv 
import time
import psycopg2
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor

app = Flask(__name__)

@app.route('/test')
def test():
    return "OK"

http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
http_request_duration_seconds = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
wishes_created_total = Counter('wishes_created_total', 'Total wishes created')

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    endpoint = request.endpoint or request.path
    http_requests_total.labels(method=request.method, endpoint=endpoint, status=response.status_code).inc()
    http_request_duration_seconds.labels(method=request.method, endpoint=endpoint).observe(duration)
    return response

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

otlp_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://localhost:4318')
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{otlp_endpoint}/v1/traces"))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
FlaskInstrumentor().instrument_app(app)

load_dotenv('.env')
print("DATABASE_URL:", os.getenv('DATABASE_URL'))

CORS(app, origins=["http://localhost:3000"])

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/giftdb')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/api/gifts', methods=['GET'])
def get_gifts():
    gifts = Gift.query.order_by(Gift.created_at.desc()).all()
    return jsonify([{
        'id': gift.id,
        'title': gift.title,
        'description': gift.description,
        'completed': gift.completed,
        'recipient': gift.recipient,
        'price': gift.price
    } for gift in gifts])

@app.route('/api/gifts', methods=['POST'])
def create_gift():
    data = request.json
    gift = Gift(
        title=data['title'],
        description=data.get('description', ''),
        recipient=data.get('recipient', ''),
        price=data.get('price', 0)
    )
    db.session.add(gift)
    db.session.commit()
    wishes_created_total.inc()
    return jsonify({'id': gift.id, 'message': 'Gift created successfully'}), 201

@app.route('/api/gifts/<int:gift_id>', methods=['PUT'])
def update_gift(gift_id):
    gift = Gift.query.get_or_404(gift_id)
    data = request.json
    
    if 'completed' in data:
        gift.completed = data['completed']
    if 'title' in data:
        gift.title = data['title']
    if 'description' in data:
        gift.description = data['description']
    if 'recipient' in data:
        gift.recipient = data['recipient']
    if 'price' in data:
        gift.price = data['price']
    
    db.session.commit()
    return jsonify({'message': 'Gift updated successfully'})

@app.route('/api/gifts/<int:gift_id>', methods=['DELETE'])
def delete_gift(gift_id):
    gift = Gift.query.get_or_404(gift_id)
    db.session.delete(gift)
    db.session.commit()
    return jsonify({'message': 'Gift deleted successfully'})

@app.route('/')
def index():
    return jsonify({
        'status': 'healthy',
        'service': 'gift-todo-backend',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True, port=5000)