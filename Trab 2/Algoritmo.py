import random
import math
import heapq
import time

#BLOCO DE CLASSES DO ESTADO E VARIÁVEIS
verticelist = []
entrada = []
passosSeq = []
populacao = []
listaCruzamento = []
tamPopulacao = 10
numTentativas = 0
solucaoBetter = True

class Vertice:
    def __init__(self, numero, cordenadaX, cordenadaY):
      self.numero = numero
      self.cordenadaX = cordenadaX
      self.cordenadaY = cordenadaY

class Solucao:
    caminho = []
    aptidao = -1

    def __lt__(self, other):
        return self.custo() < other.custo()

    def custo(self):
        global verticelist
        if (self.aptidao == -1):
            soma = 0
            for i in range(tamConjunto - 1):
                v1 = verticelist[self.caminho[i] - 1]
                v2 = verticelist[self.caminho[i + 1] - 1]
                soma += math.sqrt(((v1.cordenadaX - v2.cordenadaX) ** 2) +
                                  ((v1.cordenadaY - v2.cordenadaY) ** 2))
            v1 = verticelist[self.caminho[0] - 1]
            v2 = verticelist[self.caminho[tamConjunto - 1] -1]
            soma += math.sqrt(((v1.cordenadaX - v2.cordenadaX) ** 2) +
                              ((v1.cordenadaY - v2.cordenadaY) ** 2))
            self.aptidao = soma
        return self.aptidao

tamConjunto = int(input())
for i in range(tamConjunto):
    entrada = input()
    entrada.append(entrada)

for i in range(tamConjunto):
    vList = entrada[i].split()
    vertice = Vertice(int(vList[0]), float(vList[1]), float(vList[2]))
    verticelist.append(vertice)

for i in range(1, tamConjunto + 1):
    passosSeq.append(i)

#BLOCO DEFINIÇÃO DAS FUNÇOES
def geraPopulacao():
    global populacao
    
    for i in range(tamPopulacao):
        solucao = Solucao()
        solucao.caminho = passosSeq[:]
        random.shuffle(solucao.caminho)
        heapq.heappush(populacao, solucao)
        
    return populacao
    
def selectRota(pPopulacao):
    vRandom1 = random.randrange(tamPopulacao//2)
    vRandom2 = random.randrange(tamPopulacao//2)

    if pPopulacao[vRandom1].custo() < pPopulacao[vRandom2].custo():
        return pPopulacao[vRandom1].caminho
    else:
        return pPopulacao[vRandom2].caminho

def geraCruzamento(pSolucaoA, pSolucaoB):
    global tamPopulacao
    global tamConjunto
    
    listaCruzamento = []
    contador = 0
    qtGeracoes = int(tamPopulacao * 0.8)
    tamanhoCorte = int(tamConjunto * 0.95)
    while contador < qtGeracoes:

        novoCaminho = pSolucaoA[:tamanhoCorte]
        qtAdicionados = 0
        for i in pSolucaoB:
            if qtAdicionados == (tamConjunto - tamanhoCorte):
                break
            if i not in novoCaminho:
                novoCaminho.append(i)
                qtAdicionados += 1

        novoCaminho = mutacaoCaminho(novoCaminho) #Mutação
        cruzamento = Solucao()
        cruzamento.caminho = novoCaminho
        cruzamento = buscaLocal(cruzamento) #Busca Local - First Improvement
        listaCruzamento.append(cruzamento)
        contador += 1

    return listaCruzamento
    
def mutacaoCaminho(pCaminho):
    p1 = random.randrange(tamConjunto - 1)
    p2 = random.randrange(p1, tamConjunto - 1)
    pCaminho[p1], pCaminho[p2] = pCaminho[p2], pCaminho[p1]
    return pCaminho
    
def geraVizinho(pCaminho, pContador):
    caminho = pCaminho[:]
    (caminho[pContador], caminho[pContador +1]) = (caminho[pContador +1], caminho[pContador])
    return caminho

def buscaLocal(pCruzamento):
    i = 0
    vizinho = Solucao()
    for i in range(tamConjunto//2):
        vizinho.caminho = geraVizinho(pCruzamento.caminho, i)
        if vizinho.custo() < pCruzamento.custo():
            pCruzamento = vizinho
            break

    return pCruzamento

def atualizaPopulacao(pPopulacao, pListaCruzamento):
    global solucaoBetter
    global numTentativas

    for cruzamento in pListaCruzamento:
        maior = heapq.nlargest(1, pPopulacao)[0]
        menor = pPopulacao[0]

        custoCruzamento = cruzamento.custo()
        if (custoCruzamento < maior.custo()):
            pPopulacao.remove(maior)
            heapq.heappush(pPopulacao, cruzamento)
            heapq.heapify(pPopulacao)
            
            if (custoCruzamento < menor.custo()):
                numTentativas = 0
            else:
                numTentativas += 1
        else:
            numTentativas += 1

        if (numTentativas == 700):
            solucaoBetter = False

    return pPopulacao
        
def obtemMenor(pPopulacao):
    return pPopulacao[0].custo()

#BLOCO PROGRAMA PRINCIPAL
populacao = geraPopulacao()
while (solucaoBetter):
    #Avaliação e Seleção
    solucaoA = selectRota(populacao)
    solucaoB = selectRota(populacao)

    #Cruzamento
    listaCruzamento = geraCruzamento(solucaoA, solucaoB)

    #Atualização - Elitismo
    populacao = atualizaPopulacao(populacao, listaCruzamento)

print(obtemMenor(populacao))
