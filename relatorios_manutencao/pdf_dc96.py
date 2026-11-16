"""Preenche o PDF oficial da DC-96 (formulário AcroForm) com os dados salvos.

O modelo fica em modelos/dc96.pdf e não vai para o git. Qualquer DC-96 da
mesma versão (DC-96-T 01/25) serve: os valores já preenchidos são apagados
antes de gravar os novos.
"""
import io
import os
from datetime import datetime

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject

import dc96_campos as dc96

MODELO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modelos", "dc96.pdf")


def modelo_disponivel():
    return os.path.exists(MODELO)


def _data_br(valor):
    try:
        return datetime.strptime(valor, "%Y-%m-%d").strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        return valor or ""


def _valores(rel, d):
    texto = {
        "Endereço": d["endereco"],
        "Uso principal": d["uso_principal"],
        "N BRA": rel["bra"],
        "Avaliado por": rel["responsavel"],
        "Data": _data_br(rel["data_relatorio"]),
    }
    texto.update({q: d["respostas"].get(q, "") for q in dc96.PERGUNTAS})
    caixas = {}
    for chave, _, campo_caixa, campo_coment in dc96.OPCOES_Q11:
        marcado = chave in d["q11"]
        caixas[campo_caixa] = marcado
        texto[campo_coment] = d["q11"].get(chave, "") if marcado else ""
    for _, itens in dc96.CHECKLIST:
        for chave, _, campo in itens:
            caixas[campo] = chave in d["checklist"]
    for i in range(1, dc96.MAX_PENDENCIAS + 1):
        p = d["pendencias"][i - 1] if i <= len(d["pendencias"]) else None
        texto[f"Problema{i}"] = p["problema"] if p else ""
        texto[f"Solução recomendada{i}"] = p["solucao"] if p else ""
        for resp in dc96.RESPONSAVEIS:
            caixas[dc96.campo_pdf_responsavel(i, resp)] = bool(p and p["responsavel"] == resp)
    return texto, caixas


def _nome_completo(anot):
    partes, no = [], anot
    while no is not None:
        if "/T" in no:
            partes.append(str(no["/T"]))
        no = no.get("/Parent")
        no = no.get_object() if no is not None else None
    return ".".join(reversed(partes))


def _campo(anot):
    """Objeto do campo (o próprio widget ou o pai que guarda /V)."""
    return anot if "/T" in anot else anot["/Parent"].get_object()


def preencher(rel, dados):
    writer = PdfWriter(clone_from=PdfReader(MODELO))
    texto, caixas = _valores(rel, dados)
    for pagina in writer.pages:
        for ref in pagina.get("/Annots") or []:
            anot = ref.get_object()
            if anot.get("/Subtype") != "/Widget":
                continue
            nome = _nome_completo(anot)
            campo = _campo(anot)
            if nome in caixas:
                estados = [k for k in anot.get("/AP", {}).get("/N", {}).keys() if k != "/Off"]
                ligado = NameObject(estados[0] if estados else "/On")
                valor = ligado if caixas[nome] else NameObject("/Off")
                campo[NameObject("/V")] = valor
                anot[NameObject("/AS")] = valor
            elif nome in texto:
                campo[NameObject("/V")] = TextStringObject(texto[nome] or "")
                # remove a aparência antiga para o leitor redesenhar o texto novo
                if "/AP" in anot:
                    del anot["/AP"]
    writer.set_need_appearances_writer(True)
    buf = io.BytesIO()
    writer.write(buf)
    buf.seek(0)
    return buf
