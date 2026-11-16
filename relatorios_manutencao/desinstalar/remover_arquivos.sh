#!/usr/bin/env bash
# Remove do servidor os arquivos do app "Relatórios de Manutenção" (zip enviado e arquivos extraídos).
#
# Seguro por padrão:
#   - Só mexe em arquivos IDÊNTICOS aos do zip (conferidos pelo SHA-256). Um arquivo seu com o mesmo
#     nome (ex.: app.py ou templates/base.html do sistema do TM) é listado como DIFERENTE e fica onde está.
#   - Nada é apagado: os arquivos são MOVIDOS para ~/backup_remocao_relatorios_<data>.
#     Depois de conferir que o sistema está ok, apague essa pasta pelo Gerenciador de Arquivos.
#
# Uso (cPanel → Terminal):
#   bash remover_arquivos.sh /home/SEU_USUARIO/pasta_onde_extraiu            # só mostra o que faria
#   bash remover_arquivos.sh /home/SEU_USUARIO/pasta_onde_extraiu --remover  # move para o backup

set -u
PASTA="${1:-}"
MODO="${2:-}"
if [ -z "$PASTA" ] || [ ! -d "$PASTA" ]; then
  echo "Informe a pasta onde o zip foi extraído. Ex.: bash $0 /home/usuario/relatorios_manutencao"
  exit 1
fi
PASTA="$(cd "$PASTA" && pwd)"
if [ "$PASTA" = "$HOME" ] || [ "$PASTA" = "/" ]; then
  echo "Por segurança, informe a subpasta onde o zip foi extraído, não a pasta inicial."
  exit 1
fi
BACKUP="$HOME/backup_remocao_relatorios_$(date +%Y%m%d_%H%M%S)"
APLICAR=0; [ "$MODO" = "--remover" ] && APLICAR=1

mover() {  # $1 = caminho absoluto, $2 = caminho relativo para o backup
  if [ $APLICAR -eq 1 ]; then
    mkdir -p "$BACKUP/$(dirname "$2")" && mv "$1" "$BACKUP/$2"
  fi
}

movidos=0; diferentes=0
echo "Pasta: $PASTA"
[ $APLICAR -eq 1 ] && echo "Backup: $BACKUP" || echo "Modo SIMULAÇÃO: nada será movido. Rode de novo com --remover para aplicar."
echo

# 1) Arquivos extraídos do zip
while read -r hash arq; do
  [ -z "$arq" ] && continue
  alvo="$PASTA/$arq"
  [ -f "$alvo" ] || continue
  if [ "$(sha256sum "$alvo" | cut -d' ' -f1)" = "$hash" ]; then
    echo "REMOVER    $arq"; mover "$alvo" "extraidos/$arq"; movidos=$((movidos+1))
  else
    echo "DIFERENTE  $arq  (não é o do zip; mantido)"; diferentes=$((diferentes+1))
  fi
done <<'MANIFESTO'
1a08892dcfb4718f6d40dc3758298ed6826f34b796fcb15506bb1956058f4515  .gitignore
3e61101e5c7dcb8976ccd5663ed84411f2219cf21d30b9b046089b5fe43c6f25  README.md
4de955b1d0e68bc943512972c8ab767a9a62e0453d7d7044c138f5d5b3b44df1  app.py
e6a3145ef982f0360b8894428d54417135ba325f5c719660c2e47f2af300c76a  db.py
a6e3128cdc66581d36b924e865365ca6a4d34d29d706046f21b6749e7e8ed934  dc96_campos.py
cc914b6487b091b5a7a8b8f65f7500de3fe42d86fecb459be971a6ccd498b6aa  docx_builder.py
3208bcc7d50adee7c5ff07b1bc333b4740993bf57b02edfc4f8a00ec4444b9f1  modelos/LEIA-ME.md
7ecb78690851bf06cd888513e9de09038d513f8212b5b336efe5f660db225015  modelos/dc96.pdf
cc4015cef4683abc1a8f7ffefcd24def1b0aaa3c436b8b6867520d7652b16ec0  passenger_wsgi.py
722ee876bb6e831ac012a0ba7380e95ab62d5ca0488cfee26dacc7894dc32d46  pdf_dc96.py
61e97144a22e14372135c786e70e3f2fb9fdf59b93b4c2966d25165067a0e7d9  requirements.txt
3f401d52887ea57aaf8c35e8a34cf6a67edae9c133eaa9fe730ec9349ff2ca94  schema.sql
27d02372717694f2dcadf1a6f574d19801a9b1554ff0a61719aa52d9d66202a9  static/fotografico.js
d83e100de1cbc0fa747709c973a669d177d46e5e249455eeb7e7cf84a5f0629f  static/style.css
58448f201e610589f3af6fab68df1911df5ed7976f91eab86d1c559fd052bc0e  templates/base.html
eedc54ddd8aac9f6e8eff5316885f0af0947405b034c993778d8ab99e61b930d  templates/dc96.html
7785ba4b2c9ce7bda0f53e1a2a7414aeeb28468a7ff9eea21328b70c98c18294  templates/fotografico.html
d71ed7c2f4189a5c77c80d6ac599b3644275ffc2fc30555549e87e794b2e4334  templates/index.html
e8459375391814af9a7a57661e1c3ea5869c662057a1e3818cde08e052c733d9  templates/login.html
84306072b1ddaa198191c3f0919d4204583aa74dce5b105e338daf46e284891b  templates/problemas.html
MANIFESTO

# 2) Arquivos gerados quando o app rodou (cache do Python, banco SQLite, fotos de teste)
for arq in __pycache__/app.cpython-*.pyc __pycache__/db.cpython-*.pyc __pycache__/dc96_campos.cpython-*.pyc \
           __pycache__/docx_builder.cpython-*.pyc __pycache__/pdf_dc96.cpython-*.pyc __pycache__/passenger_wsgi.cpython-*.pyc \
           instance/relatorios.db instance/fotos/.manter; do
  for alvo in "$PASTA"/$arq; do
    [ -f "$alvo" ] || continue
    rel="${alvo#$PASTA/}"; echo "REMOVER    $rel"; mover "$alvo" "extraidos/$rel"; movidos=$((movidos+1))
  done
done
for alvo in "$PASTA"/instance/fotos/*.jpg; do
  [ -f "$alvo" ] || continue
  nome="$(basename "$alvo")"
  if [[ "$nome" =~ ^[0-9a-f]{32}\.jpg$ ]]; then
    echo "REMOVER    instance/fotos/$nome"; mover "$alvo" "extraidos/instance/fotos/$nome"; movidos=$((movidos+1))
  fi
done

# 3) O próprio zip, onde quer que esteja na sua conta (procurado pelo conteúdo, não pelo nome)
ZIPHASH="0f777d42c4120fcd2a3709de85421bfe3202e19c8c978d4da9855e60a5c8632b"
while IFS= read -r z; do
  if [ "$(sha256sum "$z" | cut -d' ' -f1)" = "$ZIPHASH" ]; then
    rel="${z#$HOME/}"; echo "REMOVER    ~/$rel  (zip enviado)"; mover "$z" "zips/$rel"; movidos=$((movidos+1))
  fi
done < <(find "$HOME" -maxdepth 6 -type f -name '*.zip' -size -2M ! -path "$HOME/backup_remocao_relatorios_*" 2>/dev/null)

# 4) Pastas que ficaram vazias
if [ $APLICAR -eq 1 ]; then
  for d in __pycache__ instance/fotos instance modelos static templates; do
    rmdir "$PASTA/$d" 2>/dev/null && echo "PASTA VAZIA REMOVIDA  $d"
  done
fi

echo
echo "Itens para remover: $movidos   Mantidos por serem diferentes: $diferentes"
if [ $diferentes -gt 0 ]; then
  echo "Atenção: arquivos DIFERENTES têm o mesmo nome dos do app. Se o zip foi extraído por cima do sistema do TM,"
  echo "eles podem ter sido substituídos e depois editados: confira esses arquivos antes de qualquer outra ação."
fi
[ $APLICAR -eq 1 ] && echo "Feito. Confira o sistema e depois apague $BACKUP." || true
