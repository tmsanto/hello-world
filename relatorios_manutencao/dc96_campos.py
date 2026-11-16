"""Estrutura do formulário DC-96 (Avaliação das condições da propriedade).

Cada item guarda o nome do campo correspondente no PDF oficial (AcroForm),
usado para preencher o formulário em PDF quando o modelo está em ./modelos.
"""

# Perguntas de texto, agrupadas pelas seções do formulário.
SECOES_PERGUNTAS = [
    ("INSTALAÇÕES", [
        ("q1", "Descreva brevemente toda a propriedade, a quantidade de prédios e o tamanho deles. "
               "As plantas baixas e os esquemas de ligação da propriedade estão atualizados? Se não, qual o motivo?"),
        ("q2", "Existem áreas nas instalações que têm problemas recorrentes, além da manutenção regular? "
               "Em caso afirmativo, quais são?"),
        ("q3", "Qual é a condição geral da propriedade e das instalações?"),
        ("q4", "A propriedade e as instalações estão sendo bem usadas para as atividades teocráticas de acordo "
               "com o que foi planejado?"),
    ]),
    ("PROGRAMA DE MANUTENÇÃO", [
        ("q5", "Todas as pendências resultantes da inspeção anterior foram resolvidas? Se não, qual o motivo?"),
        ("q6", "Os serviços de manutenção preventiva e as inspeções de segurança estão sendo feitos de acordo com a "
               "tabela anual do programa de manutenção? As congregações estão fazendo a manutenção regular nas "
               "áreas onde isso é necessário? Se não, qual o motivo?"),
        ("q7", "Os voluntários locais estão sendo treinados para que possam apoiar o programa?"),
        ("q8", "Há necessidade de mais instrução ou treinamento de manutenção para que os voluntários façam o "
               "trabalho com segurança? Em caso afirmativo, o que é recomendado?"),
    ]),
    ("OBSERVAÇÕES GERAIS", [
        ("q9", "Os responsáveis pela manutenção das instalações participaram desta avaliação e concordaram com as "
               "observações feitas nela? Se não, qual o motivo?"),
        ("q10", "Está sendo feito um registro das trocas (parciais ou completas) de elementos da instalação, desde a "
                "última vistoria? Em caso afirmativo, essas trocas foram informadas no DC-97?"),
    ]),
]
PERGUNTAS = [chave for _, itens in SECOES_PERGUNTAS for chave, _ in itens]

PERGUNTA_Q11 = ("Há no Salão do Reino algum dos problemas abaixo a ponto de prejudicar o ensino? "
                "Se sim, selecione e explique.")

# (chave, texto, campo da caixa no PDF, campo do comentário no PDF)
OPCOES_Q11 = [
    ("barulho", "Barulho excessivo", "Barulho excessivo", "q11.8.0.0"),
    ("temperatura", "Calor ou frio excessivo", "Calor ou frio excessivo", "q11.8.0.1"),
    ("circulacao", "Dificuldade de circulação (escadas ou piso muito inclinado)",
     "Dificuldade de circulação escadas ou piso muito", "q11.8.0.2"),
    ("assentos", "Assentos do auditório inadequados", "Assentos do auditório inadequados", "q11.8.0.3"),
    ("saidas", "Saídas de emergência inseguras (estreitas, insuficientes ou mal localizadas)",
     "Saídas de emergência inseguras estreitas", "q11.8.0.4"),
    ("audio_video", "Áudio e/ou vídeo ineficiente", "Áudio eou vídeo ineficiente", "q11.8.0.5"),
    ("banheiros", "Banheiros mal localizados (ex.: atrás do palco ou fora do prédio)",
     "Banheiros mal localizados ex atrás do palco ou", "q11.8.0.6"),
    ("outros", "Outros (faça os comentários necessários)", "Outros faça os comentários necessários", "q11.8.0.7"),
]

INSTRUCAO_CHECKLIST = ("Não marque os itens abaixo se houver alguma irregularidade. Insira o problema na lista de "
                       "pendências e escreva a solução recomendada e o nome da pessoa responsável por cuidar dele. "
                       "Caso o item não se aplique, apenas marque (x) no espaço, para indicar que ele foi verificado.")

# (grupo, [(chave, texto, campo no PDF)])
CHECKLIST = [
    ("Segurança contra incêndio", [
        ("inc_extintores", "Os extintores de incêndio estão instalados nas saídas principais e em todos os outros locais "
         "exigidos por lei? Eles têm a etiqueta de teste e inspeção anual fixada neles?",
         "Os extintores de incêndio estão instalados nas saídas principais e em todos os outros locais exigidos por lei"),
        ("inc_mangueiras", "As mangueiras e os borrifadores (sprinklers) estão em bom estado?",
         "As mangueiras e os borrifadores sprinklers estão em bom estado"),
        ("inc_alarmes", "Os alarmes e os detectores de incêndio (fumaça, chama ou temperatura), se houver, estão "
         "funcionando perfeitamente? Em caso de modificações no prédio, os alarmes e os detectores foram adaptados de "
         "acordo com as alterações feitas?",
         "Os alarmes e os detectores de incêndio fumaça chama ou temperatura se houver estão funcionando"),
        ("inc_cozinhas", "Há detectores de incêndio nas cozinhas das residências? Os fornos, dutos, exaustores e filtros "
         "estão limpos, sem gordura e sujeira?",
         "Há detectores de incêndio nas cozinhas das residências Os fornos dutos exaustores e filtros estão limpos"),
        ("inc_cortafogo", "Os compartimentos corta-fogo do prédio têm portas corta-fogo nas rotas de fuga? Essas portas "
         "se fecham sozinhas? Elas se fecham por completo ou existe alguma brecha?",
         "Os compartimentos cortafogo do prédio têm portas cortafogo nas rotas de fuga Essas portas se fecham"),
        ("inc_lampadas", "As lâmpadas de emergência foram testadas e estão funcionando? O tempo de duração das baterias "
         "(autonomia) é suficiente? As baterias têm menos de cinco anos de vida?",
         "As lâmpadas de emergência foram testadas e estão funcionando O tempo de duração das baterias"),
        ("inc_saidas", "Todas as saídas estão desobstruídas e sinalizadas de acordo com o que a lei exige?",
         "Todas as saídas estão desobstruídas e sinalizadas de acordo com o que a lei exige"),
        ("inc_antipanico", "As portas de saída têm barras antipânico (se isso for obrigatório) e são abertas com facilidade?",
         "As portas de saída têm barras antipânico se isso for obrigatório e são abertas com facilidade"),
        ("inc_inflamaveis", "É preciso descartar as tintas e outros líquidos inflamáveis após o uso se não for mais "
         "necessário usá-los. Se for preciso armazenar algum líquido, ele deve permanecer na embalagem original. Sempre "
         "que possível, deve-se usar materiais de limpeza e tintas não inflamáveis e à base de água, e evitar "
         "embalagens de aerossol.",
         "É preciso descartar as tintas e outros líquidos inflamáveis após o uso se não for mais necessário usálos Se for"),
        ("inc_quadros", "As salas com quadros elétricos e as salas de máquinas têm algum material combustível, incluindo "
         "ferramentas e equipamentos a gás? As áreas com material combustível armazenado, incluindo o sótão, têm "
         "detectores de incêndio e estão divididas em compartimentos (onde isso for exigido por lei)?",
         "As salas com quadros elétricos e as salas de máquinas têm algum material combustível incluindo fer"),
        ("inc_dutos", "Os dutos de aquecimento estão isolados de material inflamável, e a manutenção desses dutos é "
         "feita regularmente por alguém qualificado?",
         "Os dutos de aquecimento estão isolados de material inflamável e a manutenção desses dutos é feita"),
        ("inc_fiscal", "Um fiscal licenciado inspecionou, dentro do período correto, as instalações e os equipamentos "
         "elétricos e a gás, e deu o atestado de segurança (onde isso for exigido por lei)?",
         "Um fiscal licenciado inspecionou dentro do período correto as instalações e os equipamentos elétricos e a"),
        ("inc_plano_fuga", "Existe um plano de fuga caso as saídas não sejam tão facilmente identificáveis (ou se isso "
         "for exigido por lei)?",
         "Existe um plano de fuga caso as saídas não sejam tão facilmente identificáveis ou se isso for exigido por lei"),
    ]),
    ("Prevenção contra escorregões, tropeções e quedas", [
        ("que_degraus", "Os degraus e as rampas têm superfícies antiderrapantes? Há corrimãos? Em caso afirmativo, eles "
         "estão bem fixos?",
         "Os degraus e as rampas têm superfícies antiderrapantes Há corrimãos Em caso afirmativo eles estão bem"),
        ("que_vidros", "As janelas, as portas de vidro e os vitrôs são de vidro laminado (à prova de estilhaçamento) ou "
         "de outro tipo de vidro de segurança como, por exemplo, vidro temperado?",
         "As janelas as portas de vidro e os vitrôs são de vidro laminado à prova de estilhaçamento ou de outro tipo de"),
        ("que_panos", "Os panos de chão e as placas com aviso de piso escorregadio estão sempre à mão para serem usados "
         "quando necessário?",
         "Os panos de chão e as placas com aviso de piso escorregadio estão sempre à mão para serem usados"),
        ("que_tapetes", "Os tapetes da entrada estão em boas condições, sem pontas enroladas e colocados de um jeito que "
         "não deslizem?",
         "Os tapetes da entrada estão em boas condições sem pontas enroladas e colocados de um jeito que que"),
        ("que_circulacao", "As áreas de circulação (estacionamentos e calçadas) estão em boas condições e sem perigos em "
         "potencial?",
         "As áreas de circulação estacionamentos e calçadas estão em boas condições e sem perigos em"),
        ("que_irregulares", "As superfícies irregulares (degraus perto de portas ou calçadas) estão devidamente "
         "sinalizadas indicando o risco de queda?",
         "As superfícies irregulares degraus perto de portas ou calçadas estão devidamente sinalizadas indicando o"),
        ("que_iluminacao", "A iluminação da área externa, incluindo a área de estacionamento, está adequada?",
         "A iluminação da área externa incluindo a área de estacionamento está adequada"),
        ("que_gelo", "As ferramentas e os produtos apropriados para tirar gelo e neve de calçadas e estacionamentos "
         "estão num lugar de fácil acesso?",
         "As ferramentas e os produtos apropriados para tirar gelo e neve de calçadas e estacionamentos estão num lugar"),
    ]),
    ("Prevenção contra danos em geral", [
        ("dan_dc85", "O formulário Análise de riscos em serviços no Salão do Reino (DC-85) está sendo usado e preenchido "
         "corretamente?",
         "O formulário Análise de riscos em serviços no Salão do Reino DC85 está sendo usado e preenchido"),
        ("dan_epi", "Os equipamentos necessários para fazer a manutenção estão disponíveis? Exemplo: óculos de proteção, "
         "capacetes e luvas? (andaimes e equipamento de proteção contra quedas são necessários apenas em grandes "
         "instalações)",
         "Os equipamentos necessários para fazer a manutenção estão disponíveis Exemplo óculos de proteção"),
        ("dan_quimicos", "Os produtos de limpeza e outros produtos químicos perigosos estão guardados em um lugar seguro, "
         "fora do alcance de crianças?",
         "Os produtos de limpeza e outros produtos químicos perigosos estão guardados em um lugar seguro fora do"),
        ("dan_buracos", "Há na propriedade algum buraco, fio ou outra coisa que possa ferir alguém, mesmo que seja um "
         "intruso?",
         "Há na propriedade algum buraco fio ou outra coisa que possa ferir alguém mesmo que seja um intruso"),
        ("dan_telhado", "O telhado, os drenos e as calhas são limpos com regularidade, estão em bom estado de "
         "conservação e sem sinais de vazamento?",
         "O telhado os drenos e as calhas são limpos com regularidade estão em bom estado de conservação e sem"),
        ("dan_umidade", "Há algum sinal de umidade em porões, partes escondidas de paredes externas, tetos, banheiros, "
         "entre outros que podem ficar mofados e causar danos?",
         "Há algum sinal de umidade em porões partes escondidas de paredes externas tetos banheiros entre"),
        ("dan_cupins", "Foi feita a inspeção anual de cupins?", "Foi feita a inspeção anual de cupins"),
        ("dan_co_radonio", "É feita de forma regular a checagem dos alarmes de detecção de monóxido de carbono e de "
         "radônio? Os alarmes estão funcionando corretamente? (se isso for obrigatório na propriedade)",
         "É feita de forma regular a checagem dos alarmes de detecção de monóxido de carbono e de radônio Os"),
        ("dan_primeiros_socorros", "Há no local um kit completo de primeiros socorros (se a lei exigir)? Todos os itens "
         "do kit estão dentro da validade?",
         "Há no local um kit completo de primeiros socorros se a lei exigir Todos os itens do kit estão dentro da"),
    ]),
]
CHAVES_CHECKLIST = [c for _, itens in CHECKLIST for c, _, _ in itens]

MAX_PENDENCIAS = 25
RESPONSAVEIS = {"usuarios": "Usuários", "ldc": "LDC"}


def campo_pdf_responsavel(linha, responsavel):
    """Caixa Usuários/LDC da linha (1..25) no PDF. O PDF não tem p1.24: a linha 25 usa p1.25."""
    grupo = linha - 1 if linha <= 24 else 25
    return f"p1.{grupo}.{0 if responsavel == 'usuarios' else 1}"
