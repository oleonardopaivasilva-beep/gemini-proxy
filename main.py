from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app, origins="*", allow_headers=["Content-Type"], methods=["GET", "POST", "OPTIONS"])

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    return response

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/gerar-imagem", methods=["POST", "OPTIONS"])
def gerar_imagem():
    if request.method == "OPTIONS":
        return jsonify({"ok": True})

    if not GEMINI_API_KEY:
        return jsonify({"error": "GEMINI_API_KEY não configurada"}), 500

    data = request.json
    prompt = data.get("prompt", "")
    ref_base64 = data.get("refBase64", "")
    ref_mime = data.get("refMime", "image/jpeg")

    if not prompt:
        return jsonify({"error": "Prompt vazio"}), 400

    parts = []
    if ref_base64:
        parts.append({"inlineData": {"mimeType": ref_mime, "data": ref_base64}})
    parts.append({"text": prompt})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp-image-generation:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {"responseModalities": ["image", "text"]}
    }

    try:
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        candidates = result.get("candidates", [])
        if not candidates:
            return jsonify({"error": "Nenhuma imagem gerada"}), 500
        for part in candidates[0].get("content", {}).get("parts", []):
            if "inlineData" in part:
                return jsonify({
                    "mimeType": part["inlineData"]["mimeType"],
                    "data": part["inlineData"]["data"]
                })
        return jsonify({"error": "Sem imagem na resposta do Gemini"}), 500
    except requests.exceptions.HTTPError as e:
        try:
            err_detail = e.response.json()
        except:
            err_detail = str(e)
        return jsonify({"error": str(err_detail)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/gerar-prompts", methods=["POST", "OPTIONS"])
def gerar_prompts():
    if request.method == "OPTIONS":
        return jsonify({"ok": True})

    if not GEMINI_API_KEY:
        return jsonify({"error": "GEMINI_API_KEY não configurada"}), 500

    data = request.json
    produto = data.get("produto", "")
    if not produto:
        return jsonify({"error": "Produto vazio"}), 400

    system = """Você é um Especialista em Geração de Prompts de Imagens Premium para Mercado Livre Brasil.
Analise o produto e gere exatamente 7 prompts técnicos executáveis por IA de imagem.

REGRAS:
- Nunca inventar dados técnicos não presentes na descrição
- Nunca repetir informações entre imagens
- Sempre em português PT-BR
- Responda APENAS com os 7 prompts no formato exato abaixo, sem explicações extras

IMAGEM 1
[prompt: fundo branco puro #FFFFFF, produto central 85% do frame, iluminação uniforme, sombra suave, realismo alto, sem textos, sem ícones, estilo clean premium e-commerce, 1200x1200]

IMAGEM 1B
[prompt: ambiente coerente com produto e público-alvo, fundo desfocado bokeh, produto destacado em primeiro plano, estética profissional, poucos elementos, sem textos, sem ícones, 1200x1200]

IMAGEM 2
[prompt: fundo claro compatível com a cor do produto, texto curto e técnico destacando benefícios, ícones 3D realistas mostrando o produto em miniatura realizando cada benefício, proibido ícone flat/genérico, 1200x1200]

IMAGEM 3
[prompt: fundo claro compatível, explica como o produto funciona, pode usar setas e diagramas, ícones 3D realistas com o produto em ação, 1200x1200]

IMAGEM 4
[prompt: fundo claro compatível, mostra ações reais do dia a dia com o produto, texto curto e direto, ícones 3D realistas com o produto em ação, 1200x1200]

IMAGEM 5
[prompt: fundo claro compatível, layout técnico em cards/blocos limpos, apenas dados presentes na descrição, ícones 3D com o produto, 1200x1200]

IMAGEM 6
[prompt: pessoa usando o produto, idade coerente com o público-alvo, ambiente compatível, 1200x1200]"""

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
    except requests.exceptions.HTTPError as e:
        try:
            err_detail = e.response.json()
        except:
            err_detail = str(e)
        return jsonify({"error": str(err_detail)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
