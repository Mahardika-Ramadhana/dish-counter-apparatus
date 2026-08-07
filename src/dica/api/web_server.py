from flask import Flask, jsonify, request, render_template, Response
import logging
import cv2
import qrcode
import io
import numpy as np
import dica.core.config as config
from dica.db.cloud_sync import CloudSync
# Matikan log bawaan flask agar terminal tidak kotor
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


from functools import wraps

def create_app(main_app):
    app = Flask(__name__, template_folder='templates')

    def require_api_key(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or auth_header != f"Bearer {config.API_KEY}":
                return jsonify({'status': 'error', 'message': 'Akses ditolak: API Key tidak valid'}), 401
            return f(*args, **kwargs)
        return decorated

    @app.route('/')
    def index():
        return render_template('index.html', api_key=config.API_KEY)

    @app.route('/customer')
    def customer():
        return render_template('customer.html')

    @app.route('/api/status')
    def status():
        items_data = []
        for item in main_app.current_detections:
            items_data.append({
                'name': item['class_name'],
                'price': item.get('harga', 0)
            })

        return jsonify({
            'state': main_app.transaction_state,
            'total_price': main_app.current_total_price,
            'items': items_data,
            'weight': main_app.current_weight,
            'auto_validate': main_app.auto_validate,
            'has_occlusion': getattr(main_app.detector, 'has_occlusion', False)
        })

    @app.route('/api/image')
    def image():
        if main_app.last_drawn_frame_bgr is not None:
            ret, jpeg = cv2.imencode('.jpg', main_app.last_drawn_frame_bgr)
            if ret:
                return Response(jpeg.tobytes(), mimetype='image/jpeg')
        return Response(b'', mimetype='image/jpeg')

    @app.route('/api/image_raw')
    def image_raw():
        if hasattr(main_app, 'last_raw_frame_bgr') and main_app.last_raw_frame_bgr is not None:
            ret, jpeg = cv2.imencode('.jpg', main_app.last_raw_frame_bgr)
            if ret:
                return Response(jpeg.tobytes(), mimetype='image/jpeg')
        return Response(b'', mimetype='image/jpeg')

    @app.route('/api/remote_snapshot', methods=['POST'])
    @require_api_key
    def remote_snapshot():
        """ Endpoint untuk menerima gambar dari perangkat eksternal (seperti ESP32)
            jika sistem dideploy sebagai Cloud AI.
        """
        if 'image' not in request.files:
            return jsonify({'status': 'error', 'message': 'No image provided'}), 400
        
        file = request.files['image']
        npimg = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'status': 'error', 'message': 'Invalid image format'}), 400
            
        # Put frame into the queue to be processed by AI thread
        import queue
        if main_app.sm.trigger_processing():
            if not main_app.frame_queue.empty():
                try:
                    main_app.frame_queue.get_nowait()
                except queue.Empty:
                    pass
            # Atas = frame eksternal, Samping = None
            main_app.last_raw_frame_bgr = frame.copy()
            main_app.frame_queue.put((frame, None))
            return jsonify({'status': 'success', 'message': 'Frame queued for inference'})
        
        return jsonify({'status': 'error', 'message': 'Machine is not IDLE'}), 429


    @app.route('/api/validate', methods=['POST'])
    @require_api_key
    def validate():
        data = request.json
        if not data or 'items' not in data:
            return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

        validated_items = []
        validated_total = 0
        try:
            for it in data['items']:
                name = str(it.get('name', 'Unknown'))
                price = int(it.get('price', 0))

                if price < 0:
                    return jsonify({'status': 'error', 'message': 'Harga tidak valid'}), 400

                validated_items.append({
                    # Batasi panjang string (Mencegah XSS payload besar)
                    'class_name': name[:50],
                    'harga': price,
                    'bbox': [0, 0, 0, 0],
                    'confidence': 1.0
                })
                validated_total += price
        except (ValueError, TypeError):
            return jsonify({'status': 'error', 'message': 'Format data tidak valid'}), 400

        main_app.validasi_via_web(validated_items, validated_total)
        return jsonify({'status': 'success'})

    @app.route('/api/confirm', methods=['POST'])
    @require_api_key
    def confirm():
        if main_app.transaction_state == 'PAYMENT':
            main_app.konfirmasi_pembayaran_via_web()
            return jsonify({'status': 'success'})
        return jsonify({'status': 'error', 'message': 'No pending payment'})

    @app.route('/api/tare', methods=['POST'])
    @require_api_key
    def tare():
        main_app.loadcell.tare()
        if main_app.transaction_state == 'NEEDS_CALIBRATION':
            main_app.transaction_state = 'IDLE'
        return jsonify({'status': 'success'})

    @app.route('/api/toggle_auto', methods=['POST'])
    @require_api_key
    def toggle_auto():
        main_app.auto_validate = not main_app.auto_validate
        return jsonify({'status': 'success', 'auto_validate': main_app.auto_validate})

    @app.route('/api/qr')
    def qr_code():
        # Generate QR code that points to this server (seller dashboard)
        ip = request.host.split(':')[0]
        url = f'http://{ip}:5000'
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return Response(buf.read(), mimetype='image/png')

    @app.route('/api/export_transactions')
    def export_transactions():
        import csv
        transactions = main_app.db.get_all_transactions()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            ['ID Transaksi', 'Waktu', 'Daftar Menu', 'Total Harga (Rp)'])

        for t in transactions:
            writer.writerow([
                t['id'],
                t['timestamp'],
                ", ".join(t['items']),
                t['total_harga']
            ])

        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={
                "Content-disposition": "attachment; filename=riwayat_transaksi_warteg.csv"}
        )

    @app.route('/api/clear_transactions', methods=['POST'])
    @require_api_key
    def clear_transactions():
        main_app.db.clear_transactions()
        return jsonify({'status': 'success'})

    @app.route('/laporan')
    def laporan():
        return render_template('dashboard.html', api_key=config.API_KEY)

    @app.route('/api/transactions')
    def api_transactions():
        transactions = main_app.db.get_all_transactions()
        return jsonify(transactions)

    @app.route('/api/sync_cloud', methods=['POST'])
    @require_api_key
    def sync_cloud():
        sync_module = CloudSync(
            db_lokal=main_app.db.db_name,
            supabase_url=config.SUPABASE_URL,
            supabase_key=config.SUPABASE_KEY
        )
        result = sync_module.sync_unpushed_transactions()
        return jsonify(result)

    return app

def start_web_server(main_app):
    app = create_app(main_app)
    app.run(host='0.0.0.0', port=5000, threaded=True, use_reloader=False)
