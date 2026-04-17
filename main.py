from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/gerar-imagem", methods=["POST"])
def gerar_imagem():
    if not GEMINI_API_KEY:
        return jsonify({"error": "GEMINI_API_KEY não configurada"}), 500

    data = request.json
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "Prompt vazio"}), 400

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp-image-generation:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["image", "text"]}
    }

    try:
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        result = resp.json()

        candidates = result.get("candidates", [])
        if not candidates:
            return jsonify({"error": "Nenhuma imagem gerada"}), 500

        parts = candidates[0].get("content", {}).get("parts", [])
        for part in parts:
            if "inlineData" in part:
                return jsonify({
                    "mimeType": part["inlineData"]["mimeType"],
                    "data": part["inlineData"]["data"]
                })

        return jsonify({"error": "Sem imagem na resposta"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/gerar-prompts", methods=["POST"])
def gerar_prompts():
    if not GEMINI_API_KEY:
        return jsonify({"error": "GEMINI_API_KEY não configurada"}), 500

    data = request.json
    produto = data.get("produto", "")
    if not produto:
        return jsonify({"error": "Produto vazio"}), 400

    system = """Você é um Especialista em Geração de Prompts de Imagens Premium para Mercado Livre Brasil.
Analise o produto e gere exatamente 7 prompts técnicos executáveis por IA de imagem.
REGRAS: Nunca inventar dados. Nunca repetir entre imagens. Sempre PT-BR. Responda APENAS com os prompts no formato abaixo.

IMAGEM 1
[prompt capa branca: fundo #FFFFFF, produto 85%, sem textos, sem ícones, 1200x1200]

IMAGEM 1B
[prompt capa ambientada: ambiente coerente, fundo desfocado, sem textos, 1200x1200]

IMAGEM 2
[prompt benefícios: fundo claro, texto curto, ícones 3D realistas com produto em ação, 1200x1200]

IMAGEM 3
[prompt tecnologia: fundo claro, como funciona, diagramas, ícones 3D com produto, 1200x1200]

IMAGEM 4
[prompt uso/aplicação: ações reais, fundo claro, ícones 3D com produto em ação, 1200x1200]

IMAGEM 5
[prompt técnico: cards/blocos, só dados reais do produto, ícones 3D, 1200x1200]

IMAGEM 6
[prompt uso realista: pessoa usando, idade coerente, ambiente compatível, 1200x1200]"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": system + "\n\nPRODUTO:\n" + produto}]}]
    }

    try:
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        return jsonify({"prompts": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
