from pathlib import Path
import pymupdf
import re

import sys

print(sys.executable)

cwd = Path(__file__).resolve().parent

excessao_email = {"adm", "financeiro", "administrativo", "executivo"}
email_cortar = {"yahoo", "gmail", "outlook"}
print(cwd)

for pasta in cwd.iterdir():
    if pasta.is_dir():
        if "anoni_" in str(pasta):
            continue

        nome_pasta = "anoni_" + pasta.name
        data_dir = Path(cwd / nome_pasta)
        data_dir.mkdir(exist_ok=True)

for arquivos in cwd.rglob("*.pdf"):

    if"anoni_" in str(arquivos):
        continue

    eh_cpf = False

    relativo = arquivos.relative_to(cwd)

    nome_pasta = "anoni_" + relativo.parts[0]

    destino = cwd / nome_pasta / relativo.parts[1] / relativo.parts[2]

    destino.parent.mkdir(parents=True, exist_ok=True)

    doc = pymupdf.open(arquivos)

    for pagina in doc:

        texto_pagina = pagina.get_text()

        blocos = pagina.get_text_blocks()

        for bloco in blocos:
            texto = bloco[4]
            print(bloco)

            #NFS-e
            nome_completo = re.findall(r"PACIENTES?: (.*?)DADOS", texto, re.DOTALL)
            emails = re.findall(r"[a-z._-]+@[a-z.].+",texto)

            #email (Funciona em todos os e-mails)
            for email in emails:
                print("email encontrado")

                if any(item in email for item in email_cortar) and not any(item in email for item in excessao_email):
                    retangulos = pagina.search_for(email)
                    print("RETÂNGULOS:", retangulos)

                    for rect in retangulos:
                        pagina.add_redact_annot(rect, fill=(0, 0, 0))
                        print("TARJA EMAIL:", rect)

            # Pacientes - Algo específico na parte de baixo na NF
            if nome_completo:
                for nome in nome_completo:
                    print(repr(nome))
                    retangulos = pagina.search_for(nome)

                    for retangulo in retangulos:
                        pagina.add_redact_annot(retangulo, fill=(0, 0, 0))
                        print("Nome Anonimizado", retangulo)

        dados_da_operacao = re.search("DADOS DA OPERAÇÃO", texto_pagina)

        if dados_da_operacao:
            print("Comprovante Safra encontrado")

            eh_cpf = re.search(r"CPF/CNPJ Favorecido\n\d{3}\.\d{3}\.\d{3}\-\d{2}", texto_pagina)

            # Vê se tem um cpf no comprovante Safra
            if eh_cpf:
                print("Safra encontrado")

                area_favorecido = pymupdf.Rect(39.0, 129.67259216308594, 557.8221435546875, 153.995361328125)

                #encontra cpf
                cpf = re.search(r"\d{3}\.\d{3}\.\d{3}\-\d{2}", texto_pagina)
                if cpf:
                    print("CPF encontrado:", repr(cpf.group()))
                    retangulo = pagina.search_for(cpf.group(), clip=area_favorecido)

                    for rect in retangulo:
                        pagina.add_redact_annot(rect, fill=(0, 0, 0))
                        print("TARJA CPF:", rect)

                #encontra favorecido
                favorecido = re.search(r"Favorecido\n([A-Za-z ]+)", texto_pagina)
                print("Favorecido encontrado:", repr(favorecido.group(1)))
                retangulo = pagina.search_for(favorecido.group(1), clip=area_favorecido)
                for rect in retangulo:
                    pagina.add_redact_annot(rect, fill=(0, 0, 0))
                    print("TARJA favorecido:", rect)

                #encontra banco
                banco = re.search(r"Banco\n(\d{3})", texto_pagina)
                print("Banco:", banco.group(1))
                retangulo = pagina.search_for(banco.group(1), clip=area_favorecido)
                for rect in retangulo:
                    pagina.add_redact_annot(rect, fill=(0, 0, 0))
                    print("TARJA banco:", rect)

                #encontra agência
                agencia = re.search(r"Agência\n(\d{4})", texto_pagina)
                print("Agência:", agencia.group(1))
                retangulo = pagina.search_for(agencia.group(1), clip=area_favorecido)
                for rect in retangulo:
                    pagina.add_redact_annot(rect, fill=(0, 0, 0))
                    print("TARJA agência:", rect)

                #encontra conta corrente
                conta_corrente = re.search(r"Conta Corrente\n(\d{12}\-\d{1})", texto_pagina)
                print("Conta:", conta_corrente.group(1))
                retangulo = pagina.search_for(conta_corrente.group(1), clip=area_favorecido)

                for rect in retangulo:
                    pagina.add_redact_annot(rect, fill=(0, 0, 0))

                    print("TARJA conta:", rect)

        print("APLICANDO REDAÇÕES")
        pagina.apply_redactions()
        print("REDAÇÕES APLICADAS")

    doc.save(destino)
    print("SALVANDO:", destino)

    doc.close()