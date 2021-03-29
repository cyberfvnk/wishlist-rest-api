import os
import requests
import time

BASE_URL = r'https://wishlist-flask-api.herokuapp.com/'

def tempo_decorrido(f):
    def wrapper():
        t0 = time.time()
        f()
        t1 = time.time()

        t = t1 - t0
 
        print(f"\nTempo decorrido: {t:.3f} segundos. \n")
    return wrapper


@tempo_decorrido
def put_itens():
    data = [{"item 1":{"desc": "descrição item 1"}},
            {"item 2":{"desc": "descrição item 2"}},
            {"item 3":{"desc": "descrição item 3"}}]

    for i,item in enumerate(data):
        for j in item:
            response = requests.put(BASE_URL + "wishlist/" + j, data[i][j])
            print(response, response.json())

@tempo_decorrido
def get_itens():
    data = ["item 1", "item 2","item 3"]

    for i in data:
        response = requests.get(BASE_URL + "wishlist/" + i)
        print(response, response.json())

@tempo_decorrido
def patch_itens():
    data = [{"item 1":{"desc": "nova descrição item 1"}},
            {"item 2":{"desc": "nova descrição item 2"}},
            {"item 3":{"desc": "nova descrição item 3"}}]

    for i,item in enumerate(data):
        for j in item:
            response = requests.patch(BASE_URL + "wishlist/" + j, data[i][j])
            print(response, response.json())

@tempo_decorrido
def patch_status():
    data = ["item 1", "item 2","item 3"]

    for i in data:
        response = requests.patch(BASE_URL + "wishlist/" + i + "/owned/")
        print(response, response.json())

@tempo_decorrido
def get_random():
        response = requests.get(BASE_URL + "wishlist/" + "random/")
        print(response, response.json())

@tempo_decorrido
def del_itens():
    data = ["item 1", "item 2","item 3"]

    for i in data:
        response = requests.delete(BASE_URL + "wishlist/" + i)
        print(response)


def teste_api():
    t0 = time.time()
    print("----------------------------------------------")
    """ 
    TESTE GET 
    """
    print("Teste 1: Tenta acessar 3 itens que não existem na lista \n \nStatus esperado: 404 (não encontrado)")
    get_itens()
    print("----------------------------------------------")
    """ 
    TESTE PUT 
    """
    print("Teste 2: Adiciona 3 itens que não existem na lista \n \nStatus esperado: 200 (sucesso)")
    put_itens()
    print("----------------------------------------------")
    print("Teste 3: Adiciona 3 itens que já existem na lista \n \nStatus esperado: 409 (item já existe)")
    put_itens()
    print("----------------------------------------------")
    """ 
    TESTE PATCH 
    """
    print("Teste 4: Altera a descrição de 3 itens que existem na lista \n \nStatus esperado: 200 (sucesso)")
    patch_itens()
    print("----------------------------------------------")
    print("Teste 5: Altera o status de 3 itens que existem na lista \n \nStatus esperado: 200 (sucesso)")
    patch_status()
    print("----------------------------------------------")
    """ 
    TESTE GET 
    """
    print("Teste 6: Tenta acessar 3 itens que existem na lista \n \nStatus esperado: 200 (sucesso)")
    get_itens()
    print("----------------------------------------------")
    """ 
    TESTE GET (RANDOM)
    """
    print("Teste 7: Acessa um item disponível aleatório da lista \n \nStatus esperado: 200 (sucesso)")
    get_random()
    print("----------------------------------------------")
    """ 
    TESTE DELETE
    """
    print("Teste 8: Deleta os 3 itens criados anteriormente \n \nStatus esperado: 204 (sucesso)")
    del_itens()
    print("----------------------------------------------")
    print("Teste 9: Deleta 3 itens que não existem na lista \n \nStatus esperado: 404 (item não encontrado)")
    del_itens()
    print("----------------------------------------------")
    """ 
    TESTE PATCH 
    """
    print("Teste 10: Altera a descrição de 3 itens que não existem na lista \n \nStatus esperado: 404 (item não encontrado)")
    patch_itens()
    print("----------------------------------------------")
    print("Teste 11: Altera o status de 3 itens que não existem na lista \n \nStatus esperado: 404 (item não encontrado)")
    patch_status()
    print("----------------------------------------------")
    t1 = time.time()
    t = t1 - t0
    t_ideal = 0.25*3*11
    print(f"\nTestes realizados: 11 \nTempo decorrido: {t:.3f} segundos.")