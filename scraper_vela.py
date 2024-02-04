import requests
from bs4 import BeautifulSoup
import pandas as pd

url_base = 'https://www.vaporo.com.br/air-care/vela'

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"}

nomes_lista = []
estrelas_lista = []
preco_lista = []
descricao_lista = []
link_produto_lista = []
pagina_atual = 1

while True:
    url_pagina_atual = f'{url_base}?pg={pagina_atual}'
    site = requests.get(url_pagina_atual, headers=headers)
    soup = BeautifulSoup(site.content, 'html.parser')

    paginafinal = soup.find('span', class_='page-next')

    # Se não houver link para a próxima página, sair do loop
    if not paginafinal:
        break


    procura = soup.find_all(['div', 'product'], class_=['product variant nb show-down', 'product nb show-down'])

    for item in procura:
        nomes = item.find('div', class_='product-name')
        estrelas_container = item.find('div', class_='list-star')

        #link_produto = soup.find('div', class_='product-name')
        link_produto_element = item.find('a', class_='space-image')
        if link_produto_element:
            link_produto = link_produto_element['href']
            # Fazer uma nova solicitação para a página do produto
            produto_site = requests.get(link_produto, headers=headers)
            produto_soup = BeautifulSoup(produto_site.content, 'html.parser')
            preco = produto_soup.find('span', {'data-app': 'product.price', 'id': 'variacaoPreco'})
            # Encontrar o elemento da descrição na página do produto
            descricao_element = produto_soup.find('div', class_='board_htm')

            # Se houver um elemento de descrição, extrair o texto até o primeiro <h3>
            if descricao_element:
                #descricao_texto = descricao_element.get_text(strip=True)
                descricao_texto = '\n'.join(
                    [p.get_text(strip=True) for p in descricao_element.find_all(['p', 'h3', 'h4'])])
                nomes_lista.append(nomes.text.strip())
                estrelas_lista.append(len(estrelas_container.find_all("div", class_="icon active")))
                preco_lista.append(preco.text.strip() if preco else "Preço não encontrado")
                descricao_lista.append(descricao_texto)
                link_produto_lista.append(link_produto)
            else:
                print("Descrição não encontrada")

            # Imprimir os detalhes


    pagina_atual += 1

dados = {
    'Nome do produto': nomes_lista,
    'Número de estrelas': estrelas_lista,
    'Preço do produto': preco_lista,
    'Descrição do produto': descricao_lista,
    'Link do produto': link_produto_lista
}

df = pd.DataFrame(dados)
df.to_excel('dados_produtos.xlsx', index=False)
print("Dados salvos com sucesso no arquivo 'dados_produtos.xlsx'")