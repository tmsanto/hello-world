"""Relatórios de manutenção residencial.

Tipos de relatório:
- Relatório fotográfico (fotos por cômodo + pendências)
- Problemas encontrados (tabela de verificação)
- DC-96 – Avaliação das condições da propriedade

Os relatórios ficam salvos no banco (MySQL na hospedagem ou SQLite local),
fotos em disco, e podem ser reabertos, editados e baixados em Word (.docx).
A DC-96 também pode ser baixada no PDF oficial preenchido.
"""
import json
import os
import uuid
from datetime import date, datetime
from functools import wraps

from flask import (Flask, abort, flash, g, redirect, render_template, request,
                   send_file, send_from_directory, session, url_for)
from PIL import Image, ImageOps
from werkzeug.security import check_password_hash, generate_password_hash

import dc96_campos as dc96
import docx_builder
import pdf_dc96
from db import DATA_DIR, Banco, criar_tabelas

UPLOAD_DIR = os.path.join(DATA_DIR, "fotos")

COMODOS_PADRAO = [
    "Fachada da residência", "Entrada", "Sala de estar", "Cozinha",
    "Quarto", "Sanitário", "Escritório", "Lavanderia",
]
EXTENSOES_FOTO = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
FOTO_LADO_MAX = 1600  # px — reduz fotos de celular antes de salvar
TIPOS = {"fotografico": "Fotográfico", "problemas": "Problemas", "dc96": "DC-96"}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "troque-esta-chave")
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200 MB por envio

os.makedirs(UPLOAD_DIR, exist_ok=True)
criar_tabelas()


# --------------------------------------------------------------------------
# Banco de dados
# --------------------------------------------------------------------------
def get_db():
    if "db" not in g:
        g.db = Banco()
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def carregar_relatorio(rid, tipo=None):
    rel = get_db().execute("SELECT * FROM relatorios WHERE id = ?", (rid,)).fetchone()
    if rel is None or (tipo and rel["tipo"] != tipo):
        abort(404)
    return rel


def salvar_cabecalho(rid, tipo, bra, data_rel, responsavel, condicao=""):
    """Cria ou atualiza a linha em relatorios e devolve o id."""
    db = get_db()
    if rid:
        db.execute("UPDATE relatorios SET bra=?, data_relatorio=?, condicao_geral=?, responsavel=?, atualizado_em=? "
                   "WHERE id=?", (bra, data_rel, condicao, responsavel, agora(), rid))
        return rid
    cur = db.execute("INSERT INTO relatorios (tipo, bra, data_relatorio, condicao_geral, responsavel, criado_em, "
                     "atualizado_em) VALUES (?, ?, ?, ?, ?, ?, ?)",
                     (tipo, bra, data_rel, condicao, responsavel, agora(), agora()))
    return cur.lastrowid


# --------------------------------------------------------------------------
# Login simples (senha única definida em APP_PASSWORD)
# --------------------------------------------------------------------------
_SENHA_HASH = generate_password_hash(os.environ["APP_PASSWORD"]) if os.environ.get("APP_PASSWORD") else None


def login_obrigatorio(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if _SENHA_HASH and not session.get("logado"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapper


@app.route("/login", methods=["GET", "POST"])
def login():
    if not _SENHA_HASH:
        return redirect(url_for("index"))
    if request.method == "POST":
        if check_password_hash(_SENHA_HASH, request.form.get("senha", "")):
            session["logado"] = True
            destino = request.args.get("next", "")
            return redirect(destino if destino.startswith("/") and not destino.startswith("//") else url_for("index"))
        flash("Senha incorreta.", "erro")
    return render_template("login.html")


@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("login"))


# --------------------------------------------------------------------------
# Fotos
# --------------------------------------------------------------------------
def salvar_foto(arquivo):
    """Salva a foto enviada (corrigindo rotação e reduzindo tamanho). Retorna o nome do arquivo."""
    if not arquivo or not arquivo.filename:
        return None
    ext = os.path.splitext(arquivo.filename)[1].lower()
    if ext not in EXTENSOES_FOTO:
        flash(f"Arquivo ignorado (formato não suportado): {arquivo.filename}", "erro")
        return None
    nome = f"{uuid.uuid4().hex}.jpg"
    try:
        img = Image.open(arquivo.stream)
        img = ImageOps.exif_transpose(img)
        img.thumbnail((FOTO_LADO_MAX, FOTO_LADO_MAX))
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.save(os.path.join(UPLOAD_DIR, nome), "JPEG", quality=85)
    except Exception:
        flash(f"Não foi possível ler a imagem: {arquivo.filename}", "erro")
        return None
    return nome


def apagar_arquivo(nome):
    if nome:
        caminho = os.path.join(UPLOAD_DIR, nome)
        if os.path.exists(caminho):
            os.remove(caminho)


@app.route("/fotos/<path:nome>")
@login_obrigatorio
def foto(nome):
    return send_from_directory(UPLOAD_DIR, nome)


# --------------------------------------------------------------------------
# Páginas
# --------------------------------------------------------------------------
@app.route("/")
@login_obrigatorio
def index():
    busca = request.args.get("q", "").strip()
    tipo = request.args.get("tipo", "")
    sql = "SELECT * FROM relatorios WHERE 1=1"
    params = []
    if busca:
        sql += " AND (bra LIKE ? OR responsavel LIKE ?)"
        params += [f"%{busca}%", f"%{busca}%"]
    if tipo in TIPOS:
        sql += " AND tipo = ?"
        params.append(tipo)
    sql += " ORDER BY atualizado_em DESC"
    relatorios = get_db().execute(sql, params).fetchall()
    return render_template("index.html", relatorios=relatorios, busca=busca, tipo=tipo, tipos=TIPOS)


# ---- Relatório fotográfico ------------------------------------------------
@app.route("/fotografico/novo", methods=["GET", "POST"])
@app.route("/fotografico/<int:rid>", methods=["GET", "POST"])
@login_obrigatorio
def fotografico(rid=None):
    db = get_db()
    rel = carregar_relatorio(rid, "fotografico") if rid else None

    if request.method == "POST":
        rid = salvar_cabecalho(rid, "fotografico", request.form.get("bra", "").strip(),
                               request.form.get("data_relatorio", ""), request.form.get("responsavel", "").strip(),
                               request.form.get("condicao_geral", "").strip())

        existentes = {f["id"]: f for f in db.execute("SELECT * FROM fotos WHERE relatorio_id=?", (rid,)).fetchall()}
        mantidos = set()
        ordem = {"comodo": 0, "pendencia": 0}
        f = request.form
        for chave, secao, foto_id, legenda, remover in zip(
                f.getlist("item_chave"), f.getlist("item_secao"), f.getlist("item_id"),
                f.getlist("item_legenda"), f.getlist("item_remover_foto")):
            if secao not in ordem:
                continue
            novo_arquivo = salvar_foto(request.files.get(f"item_foto_{chave}"))
            atual = existentes.get(int(foto_id)) if foto_id.isdigit() else None
            arquivo = atual["arquivo"] if atual else None
            if (novo_arquivo or remover == "1") and arquivo:
                apagar_arquivo(arquivo)
                arquivo = None
            arquivo = novo_arquivo or arquivo
            legenda = legenda.strip()
            if not arquivo and not legenda:
                continue
            ordem[secao] += 1
            if atual:
                db.execute("UPDATE fotos SET secao=?, ordem=?, legenda=?, arquivo=? WHERE id=?",
                           (secao, ordem[secao], legenda, arquivo, atual["id"]))
                mantidos.add(atual["id"])
            else:
                db.execute("INSERT INTO fotos (relatorio_id, secao, ordem, legenda, arquivo) VALUES (?,?,?,?,?)",
                           (rid, secao, ordem[secao], legenda, arquivo))
        for fid, ft in existentes.items():
            if fid not in mantidos:
                apagar_arquivo(ft["arquivo"])
                db.execute("DELETE FROM fotos WHERE id=?", (fid,))
        db.commit()
        flash("Relatório salvo.", "ok")
        if request.form.get("acao") == "word":
            return redirect(url_for("baixar_word", rid=rid))
        return redirect(url_for("fotografico", rid=rid))

    if rel:
        fotos = db.execute("SELECT * FROM fotos WHERE relatorio_id=? ORDER BY secao, ordem", (rid,)).fetchall()
        comodos = [dict(x) for x in fotos if x["secao"] == "comodo"]
        pendencias = [dict(x) for x in fotos if x["secao"] == "pendencia"]
    else:
        comodos = [{"id": "", "legenda": n, "arquivo": None} for n in COMODOS_PADRAO]
        pendencias = []
    return render_template("fotografico.html", rel=rel, comodos=comodos, pendencias=pendencias,
                           hoje=date.today().isoformat())


# ---- Problemas encontrados -----------------------------------------------
@app.route("/problemas/novo", methods=["GET", "POST"])
@app.route("/problemas/<int:rid>", methods=["GET", "POST"])
@login_obrigatorio
def problemas(rid=None):
    db = get_db()
    rel = carregar_relatorio(rid, "problemas") if rid else None

    if request.method == "POST":
        rid = salvar_cabecalho(rid, "problemas", request.form.get("bra", "").strip(),
                               request.form.get("data_relatorio", ""), request.form.get("responsavel", "").strip())
        db.execute("DELETE FROM problemas WHERE relatorio_id=?", (rid,))
        f = request.form
        ordem = 0
        for quem, prob, loc, conc in zip(f.getlist("quem"), f.getlist("problema"),
                                         f.getlist("localizacao"), f.getlist("data_conclusao")):
            if not (prob.strip() or loc.strip()):
                continue
            ordem += 1
            db.execute("INSERT INTO problemas (relatorio_id, ordem, quem, problema, localizacao, data_conclusao) "
                       "VALUES (?,?,?,?,?,?)", (rid, ordem, quem.strip(), prob.strip(), loc.strip(), conc))
        db.commit()
        flash("Relatório salvo.", "ok")
        if request.form.get("acao") == "word":
            return redirect(url_for("baixar_word", rid=rid))
        return redirect(url_for("problemas", rid=rid))

    linhas = db.execute("SELECT * FROM problemas WHERE relatorio_id=? ORDER BY ordem", (rid,)).fetchall() if rel else []
    return render_template("problemas.html", rel=rel, linhas=linhas, hoje=date.today().isoformat())


# ---- DC-96 – Avaliação das condições da propriedade ------------------------
def carregar_dc96(rid):
    """Devolve (relatorio, dados) com respostas, q11, checklist e pendências já decodificados."""
    db = get_db()
    rel = carregar_relatorio(rid, "dc96")
    extra = db.execute("SELECT * FROM dc96 WHERE relatorio_id=?", (rid,)).fetchone()
    pend = db.execute("SELECT * FROM dc96_pendencias WHERE relatorio_id=? ORDER BY ordem", (rid,)).fetchall()
    dados = {
        "endereco": extra["endereco"] if extra else "",
        "uso_principal": extra["uso_principal"] if extra else "",
        "respostas": json.loads(extra["respostas"]) if extra else {},
        "q11": json.loads(extra["q11"]) if extra else {},
        "checklist": set(json.loads(extra["checklist"])) if extra else set(),
        "pendencias": [dict(p) for p in pend],
    }
    return rel, dados


@app.route("/dc96/novo", methods=["GET", "POST"])
@app.route("/dc96/<int:rid>", methods=["GET", "POST"])
@login_obrigatorio
def dc96_form(rid=None):
    db = get_db()
    if rid:
        rel, dados = carregar_dc96(rid)
    else:
        rel, dados = None, {"endereco": "", "uso_principal": "Salão do Reino", "respostas": {}, "q11": {},
                            "checklist": set(), "pendencias": []}

    if request.method == "POST":
        f = request.form
        rid = salvar_cabecalho(rid, "dc96", f.get("bra", "").strip(), f.get("data_relatorio", ""),
                               f.get("responsavel", "").strip())
        respostas = {q: f.get(q, "").strip() for q in dc96.PERGUNTAS}
        q11 = {k: f.get(f"q11_coment_{k}", "").strip() for k, *_ in dc96.OPCOES_Q11 if f.get(f"q11_{k}")}
        checklist = [c for c in dc96.CHAVES_CHECKLIST if f.get(f"chk_{c}")]
        valores = (f.get("endereco", "").strip(), f.get("uso_principal", "").strip(),
                   json.dumps(respostas, ensure_ascii=False), json.dumps(q11, ensure_ascii=False),
                   json.dumps(checklist), rid)
        if db.execute("SELECT 1 FROM dc96 WHERE relatorio_id=?", (rid,)).fetchone():
            db.execute("UPDATE dc96 SET endereco=?, uso_principal=?, respostas=?, q11=?, checklist=? "
                       "WHERE relatorio_id=?", valores)
        else:
            db.execute("INSERT INTO dc96 (endereco, uso_principal, respostas, q11, checklist, relatorio_id) "
                       "VALUES (?,?,?,?,?,?)", valores)
        db.execute("DELETE FROM dc96_pendencias WHERE relatorio_id=?", (rid,))
        ordem = 0
        for prob, sol, resp in zip(f.getlist("pend_problema"), f.getlist("pend_solucao"), f.getlist("pend_responsavel")):
            if not (prob.strip() or sol.strip()) or ordem >= dc96.MAX_PENDENCIAS:
                continue
            ordem += 1
            db.execute("INSERT INTO dc96_pendencias (relatorio_id, ordem, problema, solucao, responsavel) "
                       "VALUES (?,?,?,?,?)", (rid, ordem, prob.strip(), sol.strip(),
                                              resp if resp in dc96.RESPONSAVEIS else ""))
        db.commit()
        flash("DC-96 salva.", "ok")
        acao = f.get("acao")
        if acao == "word":
            return redirect(url_for("baixar_word", rid=rid))
        if acao == "pdf":
            return redirect(url_for("baixar_pdf_dc96", rid=rid))
        return redirect(url_for("dc96_form", rid=rid))

    return render_template("dc96.html", rel=rel, d=dados, campos=dc96, hoje=date.today().isoformat(),
                           pdf_disponivel=pdf_dc96.modelo_disponivel())


@app.route("/dc96/<int:rid>/pdf")
@login_obrigatorio
def baixar_pdf_dc96(rid):
    rel, dados = carregar_dc96(rid)
    if not pdf_dc96.modelo_disponivel():
        flash("O PDF oficial não está disponível: coloque o modelo em branco em modelos/dc96.pdf.", "erro")
        return redirect(url_for("dc96_form", rid=rid))
    buf = pdf_dc96.preencher(rel, dados)
    return send_file(buf, as_attachment=True, download_name=f"BRA{nome_seguro(rel)} - DC-96.pdf",
                     mimetype="application/pdf")


# ---- Word / exclusão ------------------------------------------------------
def nome_seguro(rel):
    return "".join(c for c in rel["bra"] if c.isalnum() or c in "-_") or str(rel["id"])


@app.route("/relatorio/<int:rid>/word")
@login_obrigatorio
def baixar_word(rid):
    db = get_db()
    rel = carregar_relatorio(rid)
    bra = nome_seguro(rel)
    if rel["tipo"] == "fotografico":
        fotos = db.execute("SELECT * FROM fotos WHERE relatorio_id=? ORDER BY secao, ordem", (rid,)).fetchall()
        buf = docx_builder.relatorio_fotografico(rel, fotos, UPLOAD_DIR)
        nome = f"Relatorio_fotografico_{bra}_{rel['data_relatorio']}.docx"
    elif rel["tipo"] == "dc96":
        _, dados = carregar_dc96(rid)
        buf = docx_builder.dc96(rel, dados)
        nome = f"BRA{bra} - DC-96_{rel['data_relatorio']}.docx"
    else:
        linhas = db.execute("SELECT * FROM problemas WHERE relatorio_id=? ORDER BY ordem", (rid,)).fetchall()
        buf = docx_builder.problemas_encontrados(rel, linhas)
        nome = f"Problemas_encontrados_{bra}_{rel['data_relatorio']}.docx"
    return send_file(buf, as_attachment=True, download_name=nome,
                     mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")


@app.route("/relatorio/<int:rid>/excluir", methods=["POST"])
@login_obrigatorio
def excluir(rid):
    db = get_db()
    carregar_relatorio(rid)
    for ft in db.execute("SELECT arquivo FROM fotos WHERE relatorio_id=?", (rid,)).fetchall():
        apagar_arquivo(ft["arquivo"])
    for tabela in ("fotos", "problemas", "dc96", "dc96_pendencias"):
        db.execute(f"DELETE FROM {tabela} WHERE relatorio_id=?", (rid,))
    db.execute("DELETE FROM relatorios WHERE id=?", (rid,))
    db.commit()
    flash("Relatório excluído.", "ok")
    return redirect(url_for("index"))


@app.template_filter("data_br")
def data_br(valor):
    try:
        return datetime.strptime(valor, "%Y-%m-%d").strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        return valor or ""


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
