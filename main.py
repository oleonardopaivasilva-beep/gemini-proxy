from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import json

app = Flask(__name__)
CORS(app, origins="*", allow_headers=["Content-Type"], methods=["GET", "POST", "OPTIONS"])

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

HTML_PAGE = open("/dev/stdin").read() if False else """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Gerador ML Premium</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f5f5f5;color:#1a1a1a;min-height:100vh}
.top{background:#fff;border-bottom:1px solid #e5e5e5;padding:16px 20px;position:sticky;top:0;z-index:10}
.top h1{font-size:16px;font-weight:600}
.top p{font-size:12px;color:#888;margin-top:2px}
.body{max-width:640px;margin:0 auto;padding:20px}
.card{background:#fff;border:1px solid #e5e5e5;border-radius:12px;padding:16px;margin-bottom:16px}
label{font-size:12px;color:#666;display:block;margin-bottom:5px;font-weight:500}
textarea,input[type=text]{width:100%;border:1px solid #e0e0e0;border-radius:8px;padding:10px 12px;font-size:14px;font-family:inherit;background:#fafafa;outline:none}
textarea{min-height:90px;resize:vertical}
textarea:focus,input:focus{border-color:#1a1a1a;background:#fff}
.field{margin-bottom:14px}
.upload{border:1.5px dashed #d0d0d0;border-radius:8px;padding:20px;text-align:center;cursor:pointer;position:relative;transition:border-color 0.2s}
.upload input{position:absolute;inset:0;opacity:0;cursor:pointer;width:100%;height:100%}
.upload.ok{border-color:#22c55e;background:#f0fdf4}
.upload p{font-size:13px;color:#888}
.upload.ok p{color:#16a34a;font-weight:500}
.preview{max-height:90px;border-radius:6px;margin-top:10px;display:none}
.btn{background:#1a1a1a;color:#fff;border:none;border-radius:10px;padding:14px;font-size:15px;font-weight:600;cursor:pointer;width:100%;transition:opacity 0.15s}
.btn:hover{opacity:0.85}
.btn:disabled{opacity:0.4;cursor:not-allowed}
.progress{height:4px;background:#e5e5e5;border-radius:2px;overflow:hidden;margin:12px 0 4px;display:none}
.progress-fill{height:100%;background:#1a1a1a;border-radius:2px;transition:width 0.4s}
.status{font-size:13px;color:#666;text-align:center;min-height:18px}
.status.err{color:#dc2626}
.tabs{display:flex;gap:8px;margin-bottom:14px}
.tab{flex:1;padding:8px;border-radius:8px;border:1px solid #e0e0e0;font-size:13px;font-weight:500;cursor:pointer;background:#fff;color:#666}
.tab.active{background:#1a1a1a;color:#fff;border-color:#1a1a1a}
.pane{display:none}
.pane.active{display:block}
.prompt-block{border:1px solid #e5e5e5;border-radius:8px;margin-bottom:10px;overflow:hidden}
.prompt-head{display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:#f9f9f9;border-bottom:1px solid #e5e5e5}
.prompt-head span{font-size:11px;font-weight:600;color:#444;text-transform:uppercase;letter-spacing:0.05em}
.copy-btn{font-size:12px;padding:3px 10px;border-radius:6px;border:1px solid #d0d0d0;background:#fff;cursor:pointer}
.prompt-text{padding:10px 12px;font-size:13px;line-height:1.6;color:#333}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.ic{background:#fff;border:1px solid #e5e5e5;border-radius:10px;padding:10px;text-align:center}
.ic img{width:100%;border-radius:6px;display:block}
.ic-label{font-size:10px;font-weight:600;color:#888;text-transform:uppercase;letter-spacing:0.05em;margin-top:6px}
.placeholder{height:120px;display:flex;align-items:center;justify-content:center;color:#aaa;font-size:12px;border-radius:6px;border:1px dashed #e0e0e0}
.err-box{height:120px;display:flex;align-items:center;justify-content:center;color:#dc2626;font-size:11px;border-radius:6px;border:1px dashed #fca5a5;padding:8px;text-align:center}
.dl{display:block;font-size:12px;color:#666;margin-top:5px;text-decoration:none}
.copy-all{width:100%;padding:10px;border-radius:8px;border:1px solid #e0e0e0;background:#fff;font-size:13px;cursor:pointer;margin-bottom:10px}
.copy-all:hover{background:#f5f5f5}
.spin{display:inline-block;width:12px;height:12px;border:2px solid #ccc;border-top-color:#1a1a1a;border-radius:50%;animation:sp 0.7s linear infinite;vertical-align:middle;margin-right:5px}
@keyframes sp{to{transform:rotate(360deg)}}
</style>
</head>
<body>
<div class="top"><h1>Gerador ML Premium</h1><p>Cole o produto + foto de referencia e receba 7 imagens prontas</p></div>
<div class="body">
  <div class="card">
    <div class="field">
      <label>Produto - link do anuncio ou descricao completa</label>
      <textarea id="produto" placeholder="Cole o link do Mercado Livre ou descreva o produto com todas as especificacoes..."></textarea>
    </div>
    <div class="field">
      <label>Foto de referencia do produto</label>
      <div class="upload" id="uploadArea">
        <input type="file" accept="image/*" onchange="handleFile(event)"/>
        <p id="uploadLabel">Toque aqui para selecionar a foto</p>
        <img id="preview" class="preview"/>
      </div>
    </div>
    <button class="btn" id="btnGerar" onclick="iniciar()">Gerar prompts e imagens</button>
    <div class="progress" id="prog"><div class="progress-fill" id="progFill" style="width:0%"></div></div>
    <p class="status" id="status"></p>
  </div>
  <div id="resultArea" style="display:none">
    <div class="tabs">
      <button class="tab active" id="tab-p" onclick="switchTab('p')">Prompts</button>
      <button class="tab" id="tab-i" onclick="switchTab('i')">Imagens</button>
    </div>
    <div class="pane active" id="pane-p">
      <button class="copy-all" onclick="copiarTodos()">Copiar todos os prompts</button>
      <div id="promptsList"></div>
    </div>
    <div class="pane" id="pane-i">
      <div class="grid" id="grid"></div>
    </div>
  </div>
</div>
<script>
const LABELS=['Imagem 1 - Capa branca','Imagem 1B - Capa ambientada','Imagem 2 - Beneficios','Imagem 3 - Tecnologia','Imagem 4 - Uso','Imagem 5 - Tecnica','Imagem 6 - Uso realista'];
const KEYS=['IMAGEM 1','IMAGEM 1B','IMAGEM 2','IMAGEM 3','IMAGEM 4','IMAGEM 5','IMAGEM 6'];
let prompts=[],refB64='',refMime='image/jpeg';

function handleFile(e){
  const f=e.target.files[0];if(!f)return;
  const r=new FileReader();
  r.onload=ev=>{
    const res=ev.target.result;
    refMime=f.type;refB64=res.split(',')[1];
    document.getElementById('uploadLabel').textContent=f.name;
    document.getElementById('uploadArea').classList.add('ok');
    const p=document.getElementById('preview');p.src=res;p.style.display='block';
  };r.readAsDataURL(f);
}
function switchTab(t){
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
  document.querySelectorAll('.pane').forEach(x=>x.classList.remove('active'));
  document.getElementById('tab-'+t).classList.add('active');
  document.getElementById('pane-'+t).classList.add('active');
}
function setSt(msg,err){const el=document.getElementById('status');el.className='status'+(err?' err':'');el.innerHTML=msg;}
function setProg(pct){document.getElementById('prog').style.display='block';document.getElementById('progFill').style.width=pct+'%';}

async function iniciar(){
  const produto=document.getElementById('produto').value.trim();
  if(!produto){setSt('Descreva o produto antes de continuar.',true);return;}
  if(!refB64){setSt('Adicione a foto de referencia.',true);return;}
  const btn=document.getElementById('btnGerar');
  btn.disabled=true;
  document.getElementById('resultArea').style.display='none';
  setProg(5);setSt('<span class="spin"></span>Gerando prompts...');
  try{
    const res=await fetch('/gerar-prompts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({produto})});
    if(!res.ok){const t=await res.text();throw new Error('HTTP '+res.status+': '+t);}
    const data=await res.json();
    if(data.error)throw new Error(data.error);
    prompts=parsePrompts(data.prompts);
    renderPrompts();renderGrid();
    document.getElementById('resultArea').style.display='block';
    setProg(15);
    await gerarImagens();
  }catch(e){setSt('Erro: '+e.message,true);btn.disabled=false;}
}

function parsePrompts(text){
  const map={};let cur=null;
  text.split('\\n').forEach(line=>{
    const t=line.trim();
    const found=['IMAGEM 1B','IMAGEM 1','IMAGEM 2','IMAGEM 3','IMAGEM 4','IMAGEM 5','IMAGEM 6'].find(k=>t===k||t===k+':'||t.startsWith(k+' -')||t.startsWith(k+' \u2014'));
    if(found){cur=found;map[found]='';}
    else if(cur&&t)map[cur]+=(map[cur]?'\\n':'')+t;
  });
  return KEYS.map(k=>map[k]||'');
}

function renderPrompts(){
  const list=document.getElementById('promptsList');list.innerHTML='';
  KEYS.forEach((k,i)=>{
    const d=document.createElement('div');d.className='prompt-block';
    d.innerHTML='<div class="prompt-head"><span>'+LABELS[i]+'</span><button class="copy-btn" onclick="copiar('+i+',this)">Copiar</button></div><div class="prompt-text" id="pt-'+i+'">'+(prompts[i]||'(nao gerado)')+'</div>';
    list.appendChild(d);
  });
}
function renderGrid(){
  const g=document.getElementById('grid');g.innerHTML='';
  LABELS.forEach((l,i)=>{
    const d=document.createElement('div');d.className='ic';d.id='ic-'+i;
    d.innerHTML='<div class="placeholder">Aguardando...</div><div class="ic-label">'+l+'</div>';
    g.appendChild(d);
  });
}

async function gerarImagens(){
  const btn=document.getElementById('btnGerar');
  for(let i=0;i<7;i++){
    setProg(15+Math.round((i/7)*82));
    setSt('<span class="spin"></span>Gerando '+LABELS[i]+'... ('+(i+1)+'/7)');
    const card=document.getElementById('ic-'+i);
    const ph=card.querySelector('.placeholder');if(ph)ph.textContent='Gerando...';
    try{
      const res=await fetch('/gerar-imagem',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt:prompts[i],refBase64:refB64,refMime:refMime})});
      if(!res.ok){const t=await res.text();throw new Error('HTTP '+res.status+': '+t.substring(0,100));}
      const data=await res.json();
      if(data.error)throw new Error(JSON.stringify(data.error).substring(0,120));
      const src='data:'+data.mimeType+';base64,'+data.data;
      card.innerHTML='<img src="'+src+'" alt="'+LABELS[i]+'"/><div class="ic-label">'+LABELS[i]+'</div><a href="'+src+'" download="ml_'+(i+1)+'.png" class="dl">Baixar</a>';
    }catch(e){
      card.innerHTML='<div class="err-box">'+e.message+'</div><div class="ic-label">'+LABELS[i]+'</div>';
    }
    await new Promise(r=>setTimeout(r,2000));
  }
  setProg(100);setSt('Todas as imagens geradas!');
  btn.disabled=false;switchTab('i');
}
function copiar(i,btn){
  navigator.clipboard.writeText(document.getElementById('pt-'+i).textContent).then(()=>{btn.textContent='Copiado!';setTimeout(()=>btn.textContent='Copiar',2000);});
}
function copiarTodos(){
  const all=LABELS.map((l,i)=>l.toUpperCase()+'\\n'+prompts[i]).join('\\n\\n---\\n\\n');
  navigator.clipboard.writeText(all).then(()=>{event.target.textContent='Copiado!';setTimeout(()=>event.target.textContent='Copiar todos os prompts',2000);});
}
</script>
</body>
</html>"""

@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    return response

@app.route("/", methods=["GET"])
def index():
    return HTML_PAGE, 200, {"Content-Type": "text/html; charset=utf-8"}

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/gerar-imagem", methods=["POST", "OPTIONS"])
def gerar_imagem():
    if request.method == "OPTIONS":
        return jsonify({"ok": True})
    if not GEMINI_API_KEY:
        return jsonify({"error": "GEMINI_API_KEY nao configurada"}), 500
    data = request.json
    prompt = data.get("prompt", "")
    ref_base64 = data.get("refBase64", "")
    ref_mime = data.get("refMime", "image/jpeg")
    if not prompt:
        return jsonify({"error": "Prompt vazio"}), 400

    # Usar Imagen 4 Fast com endpoint predict
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-fast-generate-001:predict?key={GEMINI_API_KEY}"
    
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1}
    }

    # Se tiver imagem de referencia, usar gemini-2.0-flash-exp-image-generation
    if ref_base64:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp-image-generation:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"role": "user", "parts": [
                {"inlineData": {"mimeType": ref_mime, "data": ref_base64}},
                {"text": prompt}
            ]}],
            "generationConfig": {"responseModalities": ["image", "text"]}
        }
        try:
            resp = requests.post(url, json=payload, timeout=60)
            resp.raise_for_status()
            result = resp.json()
            for part in result.get("candidates", [{}])[0].get("content", {}).get("parts", []):
                if "inlineData" in part:
                    return jsonify({"mimeType": part["inlineData"]["mimeType"], "data": part["inlineData"]["data"]})
            return jsonify({"error": "Sem imagem na resposta", "raw": str(result)[:300]}), 500
        except requests.exceptions.HTTPError as e:
            try: err_detail = e.response.json()
            except: err_detail = str(e)
            # Fallback para Imagen 4 Fast sem referencia
            pass
        except Exception as e:
            pass

    # Imagen 4 Fast (sem referencia ou fallback)
    try:
        url2 = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-fast-generate-001:predict?key={GEMINI_API_KEY}"
        payload2 = {"instances": [{"prompt": prompt}], "parameters": {"sampleCount": 1}}
        resp2 = requests.post(url2, json=payload2, timeout=60)
        resp2.raise_for_status()
        result2 = resp2.json()
        predictions = result2.get("predictions", [])
        if predictions and "bytesBase64Encoded" in predictions[0]:
            return jsonify({"mimeType": "image/png", "data": predictions[0]["bytesBase64Encoded"]})
        return jsonify({"error": "Sem imagem", "raw": str(result2)[:300]}), 500
    except requests.exceptions.HTTPError as e:
        try: err_detail = e.response.json()
        except: err_detail = str(e)
        return jsonify({"error": str(err_detail)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/gerar-prompts", methods=["POST", "OPTIONS"])
def gerar_prompts():
    if request.method == "OPTIONS":
        return jsonify({"ok": True})
    if not GEMINI_API_KEY:
        return jsonify({"error": "GEMINI_API_KEY nao configurada"}), 500
    data = request.json
    produto = data.get("produto", "")
    if not produto:
        return jsonify({"error": "Produto vazio"}), 400

    system = """Voce e um Especialista em Geracao de Prompts de Imagens Premium para Mercado Livre Brasil.
Analise o produto e gere exatamente 7 prompts tecnicos executaveis por IA de imagem.
REGRAS: Nunca inventar dados. Nunca repetir entre imagens. Sempre PT-BR. Responda APENAS com os 7 prompts no formato abaixo, sem explicacoes.

IMAGEM 1
[fundo branco puro #FFFFFF, produto central 85% do frame, iluminacao uniforme, sombra suave, realismo alto, sem textos, sem icones, estilo clean premium e-commerce, 1200x1200]

IMAGEM 1B
[ambiente coerente com produto e publico-alvo, fundo desfocado bokeh, produto destacado em primeiro plano, sem textos, sem icones, 1200x1200]

IMAGEM 2
[fundo claro compativel com a cor do produto, texto curto tecnico de beneficios, icones 3D realistas mostrando o produto em miniatura realizando cada beneficio, proibido icone flat, 1200x1200]

IMAGEM 3
[fundo claro compativel, explica como funciona e aplicacao, setas e diagramas, icones 3D com produto em acao, 1200x1200]

IMAGEM 4
[fundo claro compativel, acoes reais do dia a dia com o produto, texto curto, icones 3D com produto em acao, 1200x1200]

IMAGEM 5
[fundo claro compativel, layout tecnico em cards/blocos, apenas dados reais da descricao, icones 3D com produto, 1200x1200]

IMAGEM 6
[pessoa usando o produto, idade coerente com publico-alvo, ambiente compativel, 1200x1200]"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"role": "user", "parts": [{"text": system + "\n\nPRODUTO:\n" + produto}]}]}
    try:
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        return jsonify({"prompts": text})
    except requests.exceptions.HTTPError as e:
        try: err_detail = e.response.json()
        except: err_detail = str(e)
        return jsonify({"error": str(err_detail)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
