import heapq

## BLOCO CLASSE DO ESTADO E VARIÁVEIS ##
class Estado(object):
    matriz = []
    g = 0
    h = 0
    p = None
    identificador = 0

    def __lt__(self, other):
        return self.f() < other.f()
    
    def f(self):
        return self.g + self.h

A = [Estado()]
matrizEntrada = []
matrizFinal = [1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15, 4, 8, 12, 0]
dicionarioAbertos = {}
dicionarioFechados = {}

## BLOCO HEURISTÍCAS ##
def h1(estado): #Heurística 1
    qtPecasForaDoLugar = 0
    for i in range(16):
        if (estado.matriz[i] != matrizFinal[i]):
            qtPecasForaDoLugar = qtPecasForaDoLugar +1
            
    estado.h = qtPecasForaDoLugar

def h2(estado): #Heurística 2
    qntdPecasForaSeq = 0
    vetorPosicoes = [4, 8, 12, 13, 14, 11, 7, 3, 2, 1, 5, 9, 10, 6]
    
    for i in vetorPosicoes:
        if ((estado.matriz[i] +1) != estado.matriz[i +1]):
            qntdPecasForaSeq = qntdPecasForaSeq +1

    estado.h = qntdPecasForaSeq

def h3(estado): #Heurística 3
    matrizMap = [(0,0), (0,1), (0,2), (0,3),
                 (1,0), (1,1), (1,2), (1,3),
                 (2,0), (2,1), (2,2), (2,3),
                 (3,0), (3,1), (3,2), (3,3)]
    vetorPerfeito = [1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15, 4, 8, 12, 16]
    
    distRetangular = 0
    for i in range(16):
        if (estado.matriz[i] != vetorPerfeito[i]):
            posicaoCorreta = vetorPerfeito.index(estado.matriz[i])
            distRetangular = distRetangular + calculadistRetangular(matrizMap[i], matrizMap[posicaoCorreta])

    estado.h = distRetangular   

def calculadistRetangular(elementoA, elementoB):
    return (abs(elementoA[0] - elementoB[0]) + abs(elementoA[1] - elementoB[1]))

def h4(estado): #Heurística 4
    h1(estado)
    resultadoH1 = estado.h

    h2(estado)
    resultadoH2 = estado.h

    h3(estado)
    resultadoH3 = estado.h

    p1 = 0.1
    p2 = 0
    p3 = 0.9

    estado.h = ((p1 * resultadoH1) + (p2 * resultadoH2) + (p3 * resultadoH3)) 

def h5(estado): #Heurística 5
    h1(estado)
    resultadoH1 = estado.h

    h2(estado)
    resultadoH2 = estado.h

    h3(estado)
    resultadoH3 = estado.h

    estado.h = max(resultadoH1, resultadoH2, resultadoH3)

## BLOCO FUNÇÕES AUXILIARES ##
def r(estadoPai):    
    pos_zero = estadoPai.matriz.index(0)

    if ((pos_zero -4) >= 0): #Rotacao de Cima para Baixo
        rotacionaEstado(estadoPai, pos_zero, -4)
        
    if ((pos_zero +4) <= 15): #Rotacao de Baixo para Cima
        rotacionaEstado(estadoPai, pos_zero, +4)

    modPos = (pos_zero%4)
    if (modPos > 0): #Rotacao da Esquerda para Direita
        rotacionaEstado(estadoPai, pos_zero, -1)

    if (modPos < 3): #Rotacao da Direita para Esquerda
        rotacionaEstado(estadoPai, pos_zero, +1)

def rotacionaEstado(estadoOriginal, pos_zero, deslocamento):
    rotacao = estadoOriginal.matriz[:] #Copia a Matriz
    posTroca = (pos_zero + deslocamento)
    rotacao[pos_zero], rotacao[posTroca] = rotacao[posTroca], rotacao[pos_zero] #Troca os elementos

    idMatrizRotacao = calculaHash(rotacao)
    estadoExistente = obterEstado(dicionarioAbertos, idMatrizRotacao)
    posGPai = (estadoOriginal.g +1)
    if (estadoExistente != -1):
        if (estadoExistente.g > posGPai):
            estadoExistente.p = estadoOriginal
            estadoExistente.g = posGPai
            adicionaEstadoNoHeap(estadoExistente)
    else:
        estado = Estado()
        estado.matriz = rotacao
        estado.p = estadoOriginal
        estado.g = posGPai
        estado.identificador = idMatrizRotacao

        if (obterEstado(dicionarioFechados, idMatrizRotacao) == -1):
            h3(estado) #Calcula a heurística
            adicionaNoDicionario(dicionarioAbertos, estado)
            adicionaEstadoNoHeap(estado)

def adicionaEstadoNoHeap(estado):
    heapq.heappush(A, estado)

def menorEstadoAberto():
    return heapq.heappop(A)

def calculaHash(matrizEstado):
    return tuple(matrizEstado)

def adicionaNoDicionario(dicionario, estado):
    dicionario[estado.identificador] = estado

def removeDoDicionario(dicionario, estado):
    try:
        del dicionario[estado.identificador]
    except:
        pass

def obterEstado(dicionario, identificador):
    try:
        return dicionario[identificador]
    except:
        return -1

## BLOCO ALGORITMO A* ##
valores = input()
for x in valores.split():
    matrizEntrada.append(int(x))

A[0].matriz = matrizEntrada
A[0].identificador = calculaHash(matrizEntrada)
adicionaEstadoNoHeap(A[0])
idMatrizFinal = calculaHash(matrizFinal)

while True:

    v = menorEstadoAberto()
    if (v.identificador == idMatrizFinal):
        break

    removeDoDicionario(dicionarioAbertos, v)    
    adicionaNoDicionario(dicionarioFechados, v)

    r(v) #Calcula os sucessores

print(v.g)
