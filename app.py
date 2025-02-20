from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/version.json')
def version():
    return jsonify(version="1.3.2")  # Retorna a versão mais recente

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6050)  # Executa o servidor na porta 5000
