from flask import Flask, jsonify, request, render_template, Response
import logging
import cv2
import qrcode
import io
import config
from cloud_sync import CloudSync
# Matikan log bawaan flask agar terminal tidak kotor
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def start_web_server(main_app):
    app = Flask(__name__, template_folder='../templates')
    
    @app.route('/')
    def index():
        return render_template('index.html')
        
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
        
    @app.route('/api/validate', methods=['POST'])
    def validate():
        data = request.json
        if not data or 'items' not in data:
            return jsonify({'status': 'error', 'message': 'Invalid data'})
            
        validated_items = []
        validated_total = 0
        for it in data['items']:
            validated_items.append({
                'class_name': it['name'],
                'harga': it['price'],
                'bbox': [0,0,0,0],
                'confidence': 1.0
            })
            validated_total += it['price']
            
        main_app.validasi_via_web(validated_items, validated_total)
        return jsonify({'status': 'success'})

    @app.route('/api/confirm', methods=['POST'])
    def confirm():
        if main_app.transaction_state == 'PAYMENT':
            main_app.konfirmasi_pembayaran_via_web()
            return jsonify({'status': 'success'})
        return jsonify({'status': 'error', 'message': 'No pending payment'})
        
    @app.route('/api/tare', methods=['POST'])
    def tare():
        main_app.loadcell.tare()
        if main_app.transaction_state == 'NEEDS_CALIBRATION':
            main_app.transaction_state = 'IDLE'
        return jsonify({'status': 'success'})
        
    @app.route('/api/toggle_auto', methods=['POST'])
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
        writer.writerow(['ID Transaksi', 'Waktu', 'Daftar Menu', 'Total Harga (Rp)'])
        
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
            headers={"Content-disposition": "attachment; filename=riwayat_transaksi_warteg.csv"}
        )

    @app.route('/api/clear_transactions', methods=['POST'])
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
    def sync_cloud():
        # Proteksi keamanan Endpoint (API Key)
        auth_header = request.headers.get('Authorization')
        if not auth_header or auth_header != f"Bearer {config.API_KEY}":
            return jsonify({'status': 'error', 'message': 'Akses ditolak: API Key tidak valid'}), 401

        sync_module = CloudSync(
            db_lokal=main_app.db.db_name, 
            supabase_url=config.SUPABASE_URL, 
            supabase_key=config.SUPABASE_KEY
        )
        result = sync_module.sync_unpushed_transactions()
        return jsonify(result)

    app.run(host='0.0.0.0', port=5000, threaded=True, use_reloader=False)
