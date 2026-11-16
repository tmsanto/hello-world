# Relatórios de Manutenção (sistema do TM)

App web (Python/Flask + HTML/CSS/JS) para preencher, salvar e consultar, por BRA:

1. **DC-96 – Avaliação das condições da propriedade**
   - Descrição da propriedade (endereço, uso principal, nº BRA, avaliado por, data)
   - Perguntas 1 a 10 (Instalações, Programa de manutenção, Observações gerais)
   - Pergunta 11: 8 opções marcáveis, cada uma com explicação
   - Lista de verificação de segurança: 30 itens em 3 grupos, com contador e botão
     "+ Pendência" que já cria a pendência a partir do item com irregularidade
   - Pendências: até 25 itens com problema, solução recomendada e quem cuida (Usuários/LDC)
   - Saída em **Word** e no **PDF oficial da DC-96 preenchido**
2. **Relatório fotográfico**: fotos por cômodo + pendências (Notas 3 e 4), saída em Word.
3. **Problemas encontrados**: quem verificou, problema, localização, data de conclusão, saída em Word.

## Banco de dados

- **Hospedagem**: MySQL/MariaDB. Defina `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` (e `DB_PORT` se não for 3306).
  A estrutura está em `schema.sql` (importe pelo phpMyAdmin). O app também cria as tabelas sozinho se não existirem.
- **No computador**: sem `DB_HOST`, usa SQLite em `instance/relatorios.db`.

## Instalar na hospedagem cPanel (Hostinger, HostGator, Locaweb etc.)

1. **Banco**: cPanel → *Bancos de dados MySQL* → crie o banco e o usuário, dê todos os privilégios ao usuário nesse banco.
2. **Tabelas**: phpMyAdmin → selecione o banco → *Importar* → envie `schema.sql`.
3. **App**: cPanel → *Setup Python App* → *Create Application*
   - Python 3.10 ou mais novo
   - *Application root*: `relatorios_manutencao`
   - *Application startup file*: `passenger_wsgi.py` · *Entry point*: `application`
4. **Arquivos**: Gerenciador de arquivos → abra a pasta `relatorios_manutencao` → envie o zip → *Extrair*.
5. **Variáveis** (em *Environment variables* do app):
   `DB_HOST=localhost`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `APP_PASSWORD` (senha de acesso),
   `SECRET_KEY` (texto aleatório longo).
6. No app Python, clique em *Run Pip Install* → `requirements.txt` (ou rode `pip install -r requirements.txt`
   no terminal do ambiente virtual) e depois *Restart*.

As fotos ficam em `instance/fotos/` dentro da pasta do app. Faça backup dessa pasta e do banco.

## Rodar no computador

```bash
cd relatorios_manutencao
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py            # http://localhost:5000
```

## Variáveis de ambiente

| Variável | Para quê |
|---|---|
| `APP_PASSWORD` | Senha de acesso. **Defina em produção**, sem ela o app fica aberto. |
| `SECRET_KEY` | Chave da sessão (texto aleatório longo). |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Conexão MySQL. Sem `DB_HOST`, usa SQLite. |
| `DATA_DIR` | Pasta das fotos e do SQLite (padrão: `./instance`). |
