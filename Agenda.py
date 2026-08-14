------------------------------ ARQUIVO AgendaRioTinto.txt

Ana Luísa#666#Tambaú#13#Dezembro
Maria#888#Centro#9#Setembro
Ana Maria#222#Teste#6#Janeiro

------------------------------ ARQUIVO ProgramaAgenda.py

def leContatosDeArquivo(nomeArquivo):
  arquivo = open(nomeArquivo, 'r')
  # pega todos as linhas do arquivo
  # como uma lista de listas
  linhas = []
  for linha in arquivo:
      linhaLida = linha.strip().split("#")
      linhas.append(linhaLida)
  arquivo.close()
  return linhas

def gravaContatosEmArquivo(contatos, nomeArquivo):
  arquivo = open(nomeArquivo,'w')
  for nome, telefone, bairro, dia, mes in contatos:
      linha = nome + "#" + telefone + "#" + bairro + "#" + dia + "#"+ mes + "\n"
      arquivo.write(linha)
  arquivo.close()

def listaContatos(contatos):
    for linha in contatos:
      print("Nome:",linha[0],", Telefone:", linha[1], ", Bairro:", linha[2], ", Aniversário:",linha[3],"/",linha[4])


def listaContatosIniciadosCom(letra, contatos):
    print("CONTATOS COM PREFIXO:",letra)
    for nome, telefone, bairro, dia, mes in contatos:
        if (nome.upper()[0]== letra.upper()):
            print("Nome:", nome, ", Telefone:", telefone, ", Bairro:", bairro, ", Aniversário:", dia,"/",mes)
          
def pesquisaAniversarioDe(nomePesq, contatos):
  for nome, telefone, bairro, dia, mes in contatos:
    if (nomePesq==nome):
      print(dia,"/",mes)

  
#PROGRAMA PRINCIPAL
  
contatos = leContatosDeArquivo("AgendaRioTinto.txt")
numColunas = len(contatos[0])
numLinhas = len(contatos) 

print("Número de contatos lidos:",numLinhas)
print("Número de dados de cada contato:", numColunas)

acabou = False
while (not acabou):
    opcao = int(input("Digite uma opção:\n1.Listar contatos\n2.Pesquisar aniversario de...\n3.Pesquisar contatos do bairro\n4.Pesquisar aniversariantes do mês\n5.Cadastrar Contato\n6.Salvar dados\n7.Listar contatos com letra...\n8.Sair\n"))
    if (opcao == 1):
        listaContatos(contatos)
    elif (opcao == 2):
        nomePesq = input("Qual o nome a pesquisar?")
        pesquisaAniversarioDe(nomePesq, contatos)
    elif (opcao == 5):
        nome = input("Digite o nome da pessoa\n")
        telefone = input("Digite o telefone\n")
        bairro = input("Digite o bairro em que mora\n")
        diaAniversario = input("Digite o dia do aniversário\n")
        mesAniversario = input("Digite o mês do aniversário\n")
        contato = [nome, telefone, bairro, diaAniversario, mesAniversario]
        contatos.append(contato)
    elif (opcao ==6):
        gravaContatosEmArquivo(contatos, "AgendaRioTinto.txt")
    elif (opcao == 7):
        letra = input("Qual a letra a pesquisar?")
        listaContatosIniciadosCom(letra, contatos)
    elif (opcao ==8):
        acabou = True
print("FIM DO PROGRAMA. ATÉ MAIS")

-----------------------