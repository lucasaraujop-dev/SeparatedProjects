def ExisteClienteComCPF(cpfProcurado, listaCPFs):
    for cpf in listaCPFs:
        if cpf == cpfProcurado:
            return True
    return False

def PesquisaNomeDoClienteDeCPF(cpf, listaCPFs, listaNomes):
    for k in range(len(listaCPFs)):
        if listaCPFs[k] == cpf:
            return listaNomes[k]
    return "CPF não encontrado"

def ContaQuantidadeDeClientesComNome(nome, listaNomes):
    qtdeClientesComNome = 0
    for nomeCliente in listaNomes:
        if nomeCliente == nome:
            qtdeClientesComNome += 1
    return qtdeClientesComNome

def ImprimeClientes(listaCPFs, listaNomes):
    for k in range(len(listaCPFs)):
        print("CPF: ", listaCPFs[k], " Nome: ", listaNomes[k])

#PROGRAMA PRINCIPAL
n = int(input("Quantos clientes você quer cadastrar?: "))
listaCPFs = []
listaNomes = []
for k in range(n):
    cpf = input("Digite o CPF do cliente: ")
    listaCPFs.append(cpf)
    nome = input("Digite o nome do cliente: ")
    listaNomes.append(nome)
print("LISTA DOS CLIENTES CADASTRADOS")

for nome in listaNomes:
    print(nome)
cpfLido = input("Digite um CPF para pesquisar: ")
nomeEncontrado = PesquisaNomeDoClienteDeCPF(cpfLido, listaCPFs, listaNomes)
print("Nome: ", nomeEncontrado)

nomeLido = input("Digite um nome para pesquisar: ")
QuantidadeDeNomes = ContaQuantidadeDeClientesComNome(nomeLido, listaNomes)
print("Quantidade de Clientes com nome: ", nomeLido, "Encontrados: ", ContaQuantidadeDeClientesComNome)

ImprimeClientes(listaCPFs, listaNomes)