from flask import Flask, render_template, request, jsonify, send_file
import os
import database
import generator

app = Flask(__name__)

# Criar pasta de saída se não existir
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'output')
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/filters', methods=['GET'])
def get_filters():
    try:
        filters = database.get_filters()
        return jsonify(filters)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search_sales', methods=['GET'])
def search_sales():
    query = request.args.get('q', '')
    empresa = request.args.get('empresa', '')
    obra = request.args.get('obra', '')
    
    if not query:
        return jsonify([])
    try:
        results = database.search_vendas(query, empresa, obra)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate_contract', methods=['POST'])
def generate_contract():
    data = request.json
    template_name = data.get('template')
    sale_id = data.get('sale_id')
    empresa = data.get('empresa')
    obra = data.get('obra')
    
    if not all([template_name, sale_id, empresa, obra]):
        return jsonify({"status": "error", "message": "Faltam parâmetros"}), 400
    
    try:
        # 1. Buscar dados detalhados
        details = database.get_venda_details(sale_id, empresa, obra)
        if not details:
            return jsonify({"status": "error", "message": "Venda não encontrada"}), 404
            
        # 2. Gerar arquivo Word
        template_path = os.path.join(os.path.dirname(__file__), 'templates', template_name)
        output_filename = f"Contrato_{sale_id}.docx"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        generator.generate_docx(template_path, details, output_path)
        
        return jsonify({
            "status": "success", 
            "message": "Contrato gerado com sucesso!",
            "file_url": f"/api/download/{output_filename}"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    path = os.path.join(OUTPUT_FOLDER, filename)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    # Usar porta 5000 por padrão
    app.run(debug=True, port=5000)
