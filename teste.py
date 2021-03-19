import requests

BASE = r"http://127.0.0.1:5000/"

# data = [{"queijo":{"desc": "pacote de queijo embalado individualmente", "link": "blablabla"}},
#         {"sweater":{"desc": "sweater da jingolas"}},
#         {"coleira":{"desc": "coleirinha pro cachorro esquisito da olivia"}}]

# for i,item in enumerate(data):
#     for j in item:
#         response = requests.put(BASE + "itens/" + j, data[i][j])
#         print(response.json())

# input()

# response = requests.patch(BASE + "itens/sweater",{"desc":"sweater de florzinha que a jinsoul deu pra go won"})
# print(response.json())

# response = requests.delete(BASE + "itens/2")
# print(response)

# input("Aperte enter")

# response = requests.get(BASE + "itens/queijo")
# print(response.json())

# input("Aperte enter")

# response = requests.patch(BASE + "itens/queijo/obtido")
# print(response.json())

# input("Aperte enter")

# response = requests.get(BASE + "itens/queijo")
# print(response.json())