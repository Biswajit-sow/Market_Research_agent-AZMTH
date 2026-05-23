import traceback

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from services.db_service import DBService
from services.vector_service import VectorService
from services.ai_service import AIService
from services.analytics_service import AnalyticsService
from services.report_service import ReportService
import os

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}}, methods=["GET", "POST", "DELETE", "OPTIONS"])


db = DBService()
vector = VectorService()
ai = AIService()
analytics = AnalyticsService()
report = ReportService()

@app.route('/analyze', methods=['POST'])
def analyze_market():
    try:
        data    = request.json
        desc    = data.get('description')
        user_id = data.get('user_id', 'startup_founder_01')

        if not desc:
            return jsonify({"error": "No description provided"}), 400

        # 1. Market math
        math_data = analytics.calculate_market_size(desc)

        # 2. Vector DB internal knowledge
        internal_info = vector.find_internal_knowledge(desc)

        # 3. AI strategy generation
        analysis_text, web_sources = ai.generate_strategy(desc, internal_info, math_data)

        # 4. Full result — returned to frontend & used for PDF
        result_package = {
            "analysis":                 analysis_text,   # full text, not truncated
            "market_size":              math_data,
            "internal_knowledge_found": internal_info,
            "web_sources":              web_sources,
            "user_query":               desc,            # used by PDF cover page
        }

        # 5. Save to AstraDB — DBService handles truncation internally
        db.save_message(user_id, desc, result_package)

        # 6. Return full result to frontend
        return jsonify(result_package)

    except Exception as e:
        print("FULL ERROR:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
@app.route('/history/<user_id>', methods=['GET'])
def get_user_history(user_id):
    try:
        history = db.get_history(user_id)
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clear-history/<user_id>', methods=['DELETE'])
def clear_history(user_id):
    try:
        db.delete_user_history(user_id)
        return jsonify({"status": "success", "message": "History permanently deleted from Astra DB"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download-report', methods=['POST'])
def download():
    try:
        data = request.json
        text = data.get('analysis')
        
        
        path = report.create_pdf(text)
        
        return send_file(path, as_attachment=True)
    except Exception as e:
        
        print(f"Server PDF error: {e}")
        return jsonify({"error": str(e)}), 500

'''from services.report_service import ReportService

@app.route('/download-report', methods=['POST'])
def download():
    try:
        data          = request.json
        text          = data.get('analysis', '')
        product_title = data.get('product_title', 'Market Analysis')
        user_query    = data.get('user_query', '')  
        path = ReportService.create_pdf(text, product_title)  # ← static call

        return send_file(
            path,
            as_attachment=True,
            download_name=os.path.basename(path),
            mimetype='application/pdf'
        )
    except Exception as e:
        import traceback
        print("Server PDF error:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500'''
if __name__ == '__main__':
    app.run(debug=True, port=5000)