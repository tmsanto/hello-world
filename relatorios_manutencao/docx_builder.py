"""Geração dos relatórios em Word (.docx) com python-docx.

Se existir um modelo em ./modelos (relatorio_fotografico.docx ou
problemas_encontrados.docx), ele é usado como base: cabeçalho, rodapé,
logotipo, margens e estilos do modelo são mantidos e o corpo é
substituído pelo conteúdo do relatório. Sem modelo, o documento é
montado do zero com um cabeçalho simples.
"""
import io
import os
from datetime import datetime

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Emu, Pt, RGBColor
from PIL import Image

import dc96_campos

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELOS_DIR = os.path.join(BASE_DIR, "modelos")
FONTE = "Segoe UI"
COR_CABECALHO_TABELA = "D9E2F3"

PERGUNTA_CONDICAO = ("A residência apresenta alguma condição que possa comprometer a saúde dos "
                     "ocupantes, como presença de mofo, umidade excessiva, ventilação insuficiente "
                     "ou temperatura inadequada?")


# --------------------------------------------------------------------------
# Utilitários
# --------------------------------------------------------------------------
def _data_br(valor):
    try:
        return datetime.strptime(valor, "%Y-%m-%d").strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        return valor or ""


def _documento_base(nome_modelo, titulo_cabecalho, paisagem=False):
    caminho = os.path.join(MODELOS_DIR, nome_modelo) if nome_modelo else None
    if caminho and os.path.exists(caminho):
        doc = Document(caminho)
        body = doc.element.body
        for el in list(body):
            if el.tag != qn("w:sectPr"):
                body.remove(el)
        _fonte_padrao(doc)
        return doc

    doc = Document()
    _fonte_padrao(doc)
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    if paisagem:
        sec.orientation = WD_ORIENT.LANDSCAPE
        sec.page_width, sec.page_height = sec.page_height, sec.page_width
        sec.left_margin = sec.right_margin = Cm(1)
        sec.top_margin = sec.bottom_margin = Cm(1)
    else:
        sec.left_margin = sec.right_margin = Cm(1.9)
        sec.top_margin, sec.bottom_margin = Cm(1.5), Cm(1.75)
    p = sec.header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p.add_run(titulo_cabecalho)
    r.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = RGBColor(0x1F, 0x38, 0x64)
    _rodape_paginacao(sec.footer.paragraphs[0])
    return doc


def _fonte_padrao(doc):
    estilo = doc.styles["Normal"]
    estilo.font.name = FONTE
    estilo.font.size = Pt(10)
    estilo.element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), FONTE)


def _campo(paragrafo, instrucao):
    run = paragrafo.add_run()
    for tipo, texto in (("begin", None), (None, instrucao), ("separate", None), (None, "1"), ("end", None)):
        if tipo:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), tipo)
        elif texto == "1":
            el = OxmlElement("w:t")
            el.text = texto
        else:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = f" {texto} "
        run._r.append(el)


def _rodape_paginacao(p, prefixo=""):
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.add_run(prefixo + "Página ")
    _campo(p, "PAGE")
    p.add_run(" de ")
    _campo(p, "NUMPAGES")


def _bordas(tabela, cor="808080"):
    tbl_pr = tabela._tbl.tblPr
    bordas = OxmlElement("w:tblBorders")
    for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b = OxmlElement(f"w:{lado}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), "4")
        b.set(qn("w:space"), "0")
        b.set(qn("w:color"), cor)
        bordas.append(b)
    tbl_pr.append(bordas)


def _sombrear(celula, cor):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), cor)
    celula._tc.get_or_add_tcPr().append(shd)


def _nao_quebrar(linha):
    tr_pr = linha._tr.get_or_add_trPr()
    tr_pr.append(OxmlElement("w:cantSplit"))


def _repetir_cabecalho(linha):
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    linha._tr.get_or_add_trPr().append(el)


def _manter_com_proximo(paragrafo):
    paragrafo.paragraph_format.keep_with_next = True


def _largura_util(doc):
    sec = doc.sections[-1]
    return sec.page_width - sec.left_margin - sec.right_margin


def _texto_rotulo(doc, rotulo, valor, quebra=False):
    p = doc.add_paragraph()
    r = p.add_run(rotulo)
    r.bold = True
    if quebra:
        r.add_break()
    p.add_run(valor or "")
    return p


def _salvar(doc):
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf


# --------------------------------------------------------------------------
# Relatório fotográfico
# --------------------------------------------------------------------------
def _tabela_fotos(doc, itens, pasta_fotos):
    if not itens:
        return
    largura = _largura_util(doc)
    larg_col = Emu(int(largura / 2))
    larg_img = Emu(int(larg_col - Cm(1)))
    alt_max = Cm(6.5)

    tabela = doc.add_table(rows=0, cols=2)
    tabela.alignment = WD_TABLE_ALIGNMENT.CENTER
    tabela.autofit = False
    _bordas(tabela)

    for i in range(0, len(itens), 2):
        par = itens[i:i + 2]
        linha_img = tabela.add_row()
        linha_leg = tabela.add_row()
        _nao_quebrar(linha_img)
        for j in range(2):
            c_img, c_leg = linha_img.cells[j], linha_leg.cells[j]
            c_img.width = c_leg.width = larg_col
            if j >= len(par):
                continue
            n, item = par[j]
            p = c_img.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            _manter_com_proximo(p)
            caminho = os.path.join(pasta_fotos, item["arquivo"]) if item["arquivo"] else None
            if caminho and os.path.exists(caminho):
                with Image.open(caminho) as im:
                    w, h = im.size
                larg, alt = larg_img, Emu(int(larg_img * h / w))
                if alt > alt_max:
                    larg, alt = Emu(int(alt_max * w / h)), alt_max
                p.add_run().add_picture(caminho, width=larg, height=alt)
            else:
                p.add_run("(sem foto)").italic = True
                p.paragraph_format.space_before = Cm(2)
                p.paragraph_format.space_after = Cm(2)
            pl = c_leg.paragraphs[0]
            pl.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pl.add_run(f"{n}. {item['legenda']}")
    doc.add_paragraph()


def relatorio_fotografico(rel, fotos, pasta_fotos):
    doc = _documento_base("relatorio_fotografico.docx", "Relatório fotográfico – Residências")

    _texto_rotulo(doc, "BRA: ", rel["bra"])
    _texto_rotulo(doc, "Data do relatório: ", _data_br(rel["data_relatorio"]))
    if rel["responsavel"]:
        _texto_rotulo(doc, "Responsável: ", rel["responsavel"])
    p = _texto_rotulo(doc, "Condição geral da residência:", f"{PERGUNTA_CONDICAO} ", quebra=True)
    resp = p.add_run(rel["condicao_geral"] or "")
    resp.bold = True

    comodos = [f for f in fotos if f["secao"] == "comodo"]
    pendencias = [f for f in fotos if f["secao"] == "pendencia"]

    _tabela_fotos(doc, list(enumerate(comodos, 1)), pasta_fotos)

    if pendencias:
        t = doc.add_paragraph()
        t.add_run("PENDÊNCIAS").bold = True
        _manter_com_proximo(t)
        t2 = doc.add_paragraph()
        t2.add_run("Notas 3 e 4").bold = True
        _manter_com_proximo(t2)
        _tabela_fotos(doc, list(enumerate(pendencias, 1)), pasta_fotos)

    return _salvar(doc)


# --------------------------------------------------------------------------
# Problemas encontrados
# --------------------------------------------------------------------------
COLUNAS_PROBLEMAS = [
    ("Quem fez a verificação", 2490),
    ("Problema Encontrado", 8709),
    ("Localização", 2268),
    ("Data da Conclusão", 2551),
]
LINHAS_MINIMAS = 15  # linhas em branco extras para completar à mão ou editar depois


def problemas_encontrados(rel, linhas):
    doc = _documento_base("problemas_encontrados.docx", "Problemas encontrados", paisagem=True)

    p = doc.add_paragraph()
    r = p.add_run("Problemas encontrados")
    r.bold = True
    r.font.size = Pt(14)
    info = doc.add_paragraph()
    info.add_run("BRA: ").bold = True
    info.add_run(rel["bra"] or "")
    info.add_run("     Data: ").bold = True
    info.add_run(_data_br(rel["data_relatorio"]))
    if rel["responsavel"]:
        info.add_run("     Responsável: ").bold = True
        info.add_run(rel["responsavel"])

    largura = _largura_util(doc)
    total_twips = sum(w for _, w in COLUNAS_PROBLEMAS)
    larguras = [Emu(int(largura * w / total_twips)) for _, w in COLUNAS_PROBLEMAS]

    tabela = doc.add_table(rows=1, cols=4)
    tabela.alignment = WD_TABLE_ALIGNMENT.CENTER
    tabela.autofit = False
    _bordas(tabela, "000000")
    cab = tabela.rows[0]
    _repetir_cabecalho(cab)
    for i, (titulo, _) in enumerate(COLUNAS_PROBLEMAS):
        c = cab.cells[i]
        c.width = larguras[i]
        _sombrear(c, COR_CABECALHO_TABELA)
        par = c.paragraphs[0]
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = par.add_run(titulo)
        run.bold = True
        run.font.size = Pt(12)

    dados = [(l["quem"], l["problema"], l["localizacao"], _data_br(l["data_conclusao"])) for l in linhas]
    dados += [("", "", "", "")] * max(0, LINHAS_MINIMAS - len(dados))
    for valores in dados:
        linha = tabela.add_row()
        _nao_quebrar(linha)
        linha.height = Cm(0.8)
        for i, v in enumerate(valores):
            c = linha.cells[i]
            c.width = larguras[i]
            par = c.paragraphs[0]
            if i == 3:
                par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            par.add_run(v)

    return _salvar(doc)


# --------------------------------------------------------------------------
# DC-96 – Avaliação das condições da propriedade
# --------------------------------------------------------------------------
def _titulo_secao(doc, texto):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    r = p.add_run(texto)
    r.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = RGBColor(0x1F, 0x38, 0x64)
    _manter_com_proximo(p)
    return p


def _tabela_duas_colunas(doc, linhas, proporcao=0.5):
    """Tabela pergunta | resposta, no estilo do formulário."""
    largura = _largura_util(doc)
    l1 = Emu(int(largura * proporcao))
    l2 = Emu(int(largura - l1))
    tabela = doc.add_table(rows=0, cols=2)
    tabela.autofit = False
    _bordas(tabela, "A6A6A6")
    for esq, dir_ in linhas:
        linha = tabela.add_row()
        _nao_quebrar(linha)
        a, b = linha.cells
        a.width, b.width = l1, l2
        a.paragraphs[0].add_run(esq)
        b.paragraphs[0].add_run(dir_ or "")
    return tabela


def _caixa(marcado):
    return "☒" if marcado else "☐"


def dc96(rel, d):
    doc = _documento_base(None, "Avaliação das condições da propriedade")
    sec = doc.sections[0]
    sec.footer.paragraphs[0].text = ""
    _rodape_paginacao(sec.footer.paragraphs[0], "DC-96-T 01/25     ")

    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = t.add_run("AVALIAÇÃO DAS CONDIÇÕES DA PROPRIEDADE")
    r.bold = True
    r.font.size = Pt(14)

    _titulo_secao(doc, "DESCRIÇÃO DA PROPRIEDADE")
    _tabela_duas_colunas(doc, [
        ("Endereço", d["endereco"]),
        ("Uso principal", d["uso_principal"]),
        ("Nº BRA", rel["bra"]),
        ("Avaliado por", rel["responsavel"]),
        ("Data", _data_br(rel["data_relatorio"])),
    ], proporcao=0.25)

    n = 0
    for titulo, perguntas in dc96_campos.SECOES_PERGUNTAS:
        _titulo_secao(doc, titulo)
        linhas = []
        for chave, texto in perguntas:
            n += 1
            linhas.append((f"{n}. {texto}", d["respostas"].get(chave, "")))
        _tabela_duas_colunas(doc, linhas)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.add_run(f"11. {dc96_campos.PERGUNTA_Q11}").bold = True
    _manter_com_proximo(p)
    for chave, texto, _, _ in dc96_campos.OPCOES_Q11:
        marcado = chave in d["q11"]
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.6)
        p.paragraph_format.space_after = Pt(2)
        p.add_run(f"{_caixa(marcado)} {texto}")
        if marcado and d["q11"].get(chave):
            p.add_run(f" — {d['q11'][chave]}").italic = True

    _titulo_secao(doc, "LISTA DE VERIFICAÇÃO DE SEGURANÇA")
    instr = doc.add_paragraph(dc96_campos.INSTRUCAO_CHECKLIST)
    instr.runs[0].font.size = Pt(9)
    for grupo, itens in dc96_campos.CHECKLIST:
        g = doc.add_paragraph()
        g.paragraph_format.space_before = Pt(6)
        g.add_run(grupo).bold = True
        _manter_com_proximo(g)
        for chave, texto, _ in itens:
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.6)
            p.paragraph_format.first_line_indent = Cm(-0.6)
            p.paragraph_format.space_after = Pt(2)
            p.add_run(f"{_caixa(chave in d['checklist'])}  {texto}")

    _titulo_secao(doc, "PENDÊNCIAS")
    doc.add_paragraph("Anote os problemas encontrados e as devidas soluções. Marque a coluna apropriada para "
                      "indicar quem vai cuidar de cada pendência.").runs[0].font.size = Pt(9)
    largura = _largura_util(doc)
    pesos = [0.07, 0.38, 0.39, 0.08, 0.08]
    larguras = [Emu(int(largura * p_)) for p_ in pesos]
    tabela = doc.add_table(rows=1, cols=5)
    tabela.autofit = False
    _bordas(tabela, "000000")
    cab = tabela.rows[0]
    _repetir_cabecalho(cab)
    for i, titulo in enumerate(["Item", "Problema", "Solução recomendada", "Usuários", "LDC"]):
        c = cab.cells[i]
        c.width = larguras[i]
        _sombrear(c, COR_CABECALHO_TABELA)
        par = c.paragraphs[0]
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.add_run(titulo).bold = True
    pend = d["pendencias"]
    total = max(len(pend), 10)
    for i in range(total):
        p_ = pend[i] if i < len(pend) else None
        valores = [f"{i + 1}.", p_["problema"] if p_ else "", p_["solucao"] if p_ else "",
                   "✔" if p_ and p_["responsavel"] == "usuarios" else "",
                   "✔" if p_ and p_["responsavel"] == "ldc" else ""]
        linha = tabela.add_row()
        _nao_quebrar(linha)
        for j, v in enumerate(valores):
            c = linha.cells[j]
            c.width = larguras[j]
            par = c.paragraphs[0]
            if j in (0, 3, 4):
                par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            par.add_run(v)

    return _salvar(doc)
