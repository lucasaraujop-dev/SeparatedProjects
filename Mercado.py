carrinho = []
valortotal = 0.0
produtos = ["Arroz", "Feijão", "Macarrão", "Óleo", "Açúcar"]
preços = [10.00, 8.00, 5.00, 7.00, 4.00]

while True:
    print("\n--------Mercado--------")
    print("[1] Adicionar produto ao carrinho")
    print("[2] Ver carrinho")
    print("[3] Finalizar compra")
    print("[4] Sair")

    escolha = input("Escolha uma opção: ")

    if escolha == "1":
        print("\nProdutos disponíveis:")
        for index, produto in enumerate(produtos, start=1):
            print(f"{index}. {produto} - R${preços[index-1]:.2f}")
        produto_escolhido = int(input("Digite o número do produto que deseja adicionar: "))
        quantidade = int(input("Digite a quantidade: "))
        valor_produto = preços[produto_escolhido - 1] * quantidade
        carrinho.append(f"{produtos[produto_escolhido - 1]} - x{quantidade}")
        valortotal += valor_produto
        print(f"Produto adicionado: {produtos[produto_escolhido - 1]}, Quantidade: x{quantidade}")

    elif escolha == "2":
        if not carrinho:
            print("O carrinho está vazio.")
        else:
            print("\nCarrinho:")
            for index, item in enumerate(carrinho, start=1):
                print(f"{index}. {item}")
            print(f"Valor total da compra: R${valortotal:.2f}")

    elif escolha == "3":
        if not carrinho:
            print("O carrinho está vazio. Adicione produtos antes de finalizar a compra.")
        else:
            print("\nFinalizando compra...")
            print("Itens comprados:")
            for item in carrinho:
                print(f"- {item}")
            print(f"Valor total a pagar: R${valortotal:.2f}")
            metodo_pagamento = input("Escolha o método de pagamento (Cartão/Dinheiro): ").lower()
            if metodo_pagamento == "cartão":
                print("Pagamento realizado com cartão. Obrigado pela compra!")
            elif metodo_pagamento == "dinheiro":
                cedulas = float(input("Digite o valor em dinheiro: R$"))
                if cedulas < valortotal:
                    print("Valor insuficiente. Por favor, insira um valor maior ou igual ao total da compra.")
                else:
                    troco = cedulas - valortotal
                    if troco > 0:
                        print(f"Troco a ser devolvido: R${troco:.2f}")
                print("Pagamento realizado em dinheiro. Obrigado pela compra!")
            print("Obrigado por comprar conosco!")
            break