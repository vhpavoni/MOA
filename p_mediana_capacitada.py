import math
import heapq
import random
import time
from copy import deepcopy

DEBUG = False


def pop_random(values):
    return values.pop(random.randrange(len(values)))


def get_random(values):
    return values[random.randrange(len(values))]


def distancia_euclidianea(p1, p2):
    xa, ya = p1
    xb, yb = p2
    return math.sqrt(math.pow((xa - xb), 2) + math.pow((ya - yb), 2))


class PriorityQueueIndividuo:
    def __init__(self, elements=[]):
        self.elements = []
        for element in elements:
            self.put(element)

    def empty(self):
        return len(self.elements) == 0

    def put(self, item):
        heapq.heappush(self.elements, item)

    def get(self):
        return heapq.heappop(self.elements)

    def peak(self, n):
        return heapq.nsmallest(n, self.elements)

    def size(self):
        return len(self.elements)


class Vertice:
    def __init__(self, coordenada, capacidade, demanda):
        self.coordenada = coordenada
        self.demanda = demanda
        self.capacidade = capacidade

    def __str__(self):
        return "Vertice({}, {}, {})".format(
            str(self.coordenada),
            str(self.capacidade),
            str(self.demanda)
        )

    def __repr__(self):
        return self.__str__()


class Mediana:
    def __init__(self, vertice, conjunto=set([])):
        self.vertice = vertice
        self.conjunto = conjunto
        self.__distancias = {}
        self.__demanda = 0
        self.__distancia_total = 0
        if len(conjunto) != 0:
            for v in conjunto:
                self.__demanda += v.demanda
                self.__distancia_total += self.distancia(self.vertice, v)

    def __str__(self):
        return "Mediana({}: {})".format(str(self.vertice), str(self.conjunto))

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.vertice == other.vertice
        return False

    def adicionar_vertice(self, v):
        self.conjunto.add(v)
        self.__demanda += v.demanda
        self.__distancia_total += self.distancia(self.vertice, v)

    def remover_vertice(self, v):
        self.conjunto.remove(v)
        self.__demanda -= v.demanda
        self.__distancia_total -= self.distancia(self.vertice, v)


    def capacidade(self, v1):
        return self.vertice.capacidade >= (self.demanda_atual() + v1.demanda)

    def demanda_atual(self):
        return self.__demanda

    def distancia(self, v1, v2):
        aresta = (v1, v2)
        if not aresta in self.__distancias:
            self.__distancias[aresta] = distancia_euclidianea(
                v1.coordenada, v2.coordenada)
        return self.__distancias[aresta]

    def distancia_total(self):
        return self.__distancia_total


class Individuo:
    def __init__(self, medianas=[]):
        self.medianas = medianas

    def fitness(self):
        aptidao = 0
        for mediana in self.medianas:
            aptidao += mediana.distancia_total()
        return aptidao

    def __lt__(self, other):
        return (self.fitness() < other.fitness())

    def __le__(self, other):
        return (self.fitness() > other.fitness())

    def __cmp__(self, other):
        return ((self.fitness() > other.fitness()) - (self.fitness() < other.fitness()))

    def __str__(self):
        return "Invididuo({}, {})".format(len(self.medianas), str(self.fitness()))

    def __repr__(self):
        return self.__str__()


class Populacao:
    def __init__(self, individuos=[]):
        self.individuos = PriorityQueueIndividuo(individuos)

    def __str__(self):
        return "População({})".format(self.individuos.size())

    def __repr__(self):
        return self.__str__()

    def melhor(self):
        return self.individuos.peak(1)[0]

    def tamanho(self):
        return self.individuos.size()

    def melhores(self, n):
        return self.individuos.peak(n)


class AlgoritmoGenetico:
    def __init__(self, vertices, tamanho_populacao,
                 quantidade_torneio, maximo_geracoes, 
                 pcross_over, pmutacao, utilizar_busca_local,
                 limite_tempo):
        self.tamanho_populacao = tamanho_populacao
        self.vertices = vertices
        self.quantidade_torneio = quantidade_torneio
        self.maximo_geracoes = maximo_geracoes
        self.pcross_over = pcross_over
        self.pmutacao = pmutacao
        self.limite_tempo = limite_tempo
        self.utilizar_busca_local = utilizar_busca_local

    def parar(self):
        self.tempo_atual = time.time()        
        return ((self.geracao > self.maximo_geracoes)
                    or ((self.tempo_atual - self.inicio)  > self.limite_tempo))

    def gerar_populacao_inicial(self, numero_medianas):
        invididuos = []
        for j in range(self.tamanho_populacao):
            vertices = self.vertices[:]
            lista_medianas = []

            if(vertices):
                for i in range(numero_medianas):
                    vertice = vertices.pop(random.randrange(len(vertices)))
                    mediana = Mediana(vertice)
                    lista_medianas.append(mediana)

            indice = 0
            i = 0
            while(vertices and lista_medianas):
                v = vertices.pop(random.randrange(len(vertices)))

                if(lista_medianas[indice].capacidade(v)):
                    lista_medianas[indice].adicionar_vertice(v)

                i += 1
                indice = (i % len(lista_medianas))

            individuo = Individuo(lista_medianas)
            invididuos.append(individuo)
        return Populacao(invididuos)

    def executar_torneio(self, populacao):
        return populacao.melhores(self.quantidade_torneio)

    def gerar_individuo(self, medianas):
        for v in self.vertices:
            if v not in medianas:
                melhor_mediana = None
                melhor_distancia = 9999999
                for mediana in medianas:
                    distancia = distancia_euclidianea(
                        v.coordenada, mediana.vertice.coordenada)
                    if ((distancia < melhor_distancia)
                            and mediana.capacidade(v)):
                        melhor_distancia = distancia
                        melhor_mediana = mediana

                if melhor_mediana != None:
                    melhor_mediana.conjunto.add(v)

        return Individuo(medianas)

    def crossover(self, pai, mae):
        pai = deepcopy(pai)
        mae = deepcopy(mae)
        numero_medianas = len(pai.medianas)

        if (random.random() < self.pcross_over):            
            medianas_filho_1 = []
            medianas_filho_2 = []

            i = 0
            while(pai.medianas):
                m = pai.medianas.pop()
            
                if i == 0:
                    medianas_filho_1.append(m)
                else: 
                    medianas_filho_2.append(m)                        
                
                i = ((i + 1) % 2)

            i = 0
            while(mae.medianas):
                m = mae.medianas.pop()
                while m != None:
                    if (i == 0 
                            and (m not in medianas_filho_1)
                            and (len(medianas_filho_1) < numero_medianas)):
                        medianas_filho_1.append(m)
                        m = None
                    elif (m not in medianas_filho_2
                            and (len(medianas_filho_2) < numero_medianas)):
                        medianas_filho_2.append(m)
                        m = None
                
                i = ((i + 1) % 2)

            return (medianas_filho_1, medianas_filho_2)
        return (pai.medianas, mae.medianas)

    def mutacao(self, medianas):
        if (random.random() < self.pmutacao):
            medianas_mutacao = medianas[:]
            nova_mediana = Mediana(get_random(self.vertices))
            while (nova_mediana in medianas_mutacao):
                nova_mediana = Mediana(get_random(self.vertices))
            
            pop_random(medianas_mutacao)
            medianas_mutacao.append(nova_mediana)                                                
            return medianas_mutacao

        return medianas

    def reproduzir(self, selecionados):
        filhos = []
        size_selecionados = len(selecionados)
        #for i in range(0, size_selecionados):
        for _ in range(2):
            i = random.randrange(size_selecionados)
            pai = selecionados[i]
            if i == size_selecionados - 1:
                mae = selecionados[0]
            else:
                mae = selecionados[i + 1] if (i %
                                             2 == 0) else selecionados[i - 1]
            
            medianas_filho_1, medianas_filho_2 = self.crossover(pai, mae)
            medianas_filho_1 = self.mutacao(medianas_filho_1)
            medianas_filho_2 = self.mutacao(medianas_filho_2)
                        
            individuo_1 = self.gerar_individuo(medianas_filho_1)
            individuo_2 = self.gerar_individuo(medianas_filho_2)

            filhos.append(individuo_1)
            filhos.append(individuo_2)

            if len(filhos) >= self.tamanho_populacao:
                break

        return filhos

    def save_relatorio(self):
        f = open('relatorio.txt', 'w')
        self.relatorio = "[\n{}]".format(self.relatorio)
        f.write(self.relatorio)
        f.close()


    def busca_local(self, filho):        
        copia_filho = deepcopy(filho)        
        size_medianas = len(filho.medianas)
        for p in range(size_medianas):
            medianas = copia_filho.medianas[:]
            old = medianas.pop(p)                        
            for v in old.conjunto:
                old_conjunto = old.conjunto.copy()
                old_conjunto.remove(v)
                old_conjunto.add(old.vertice)
                new = Mediana(v, old_conjunto)
                medianas.append(new)

                new_individuo = Individuo(medianas)
                if new_individuo < filho:
                    return new_individuo
                
        return filho
    
    def solucionar(self, numero_medianas):        
        self.relatorio = ''
        self.inicio = time.time()
        self.geracao = 0    
        if len(self.vertices) <= 0:
            return False        
        
        populacao = self.gerar_populacao_inicial(numero_medianas)            
        melhor = populacao.melhor()        
        while not self.parar():
            self.geracao += 1            
            selecionados = self.executar_torneio(populacao)                                
            filhos = self.reproduzir(selecionados)                        
            queue = PriorityQueueIndividuo(filhos)            
            melhor_filho = queue.get()            
            if self.utilizar_busca_local:                
                melhor_filho = self.busca_local(melhor_filho)            

            if melhor_filho.fitness() < melhor.fitness():
                melhor = melhor_filho

            self.relatorio += "[{}, {}],\n".format(self.geracao, melhor.fitness())
            print("Melhor da geração {}:{}".format(self.geracao,melhor))
            populacao = Populacao(selecionados + filhos)                    
            
        self.save_relatorio()
        return melhor

if (__name__ == "__main__"):                    
    linhas = open('p3038_900.txt', 'r').readlines()
    primeiralinha = linhas.pop(0).split()
        
    numero_pontos = int(primeiralinha[0])
    numero_medianas = int(primeiralinha[1])        
    vertices = []

    while linhas:                        
        x, y, capacidade, demanda = linhas.pop(0).split()        
        vertices.append(Vertice((float(x), float(y)), float(capacidade), float(demanda)))
    
    # Parte para enviar
    # primeiralinha = input()
    # primeiralinha = primeiralinha.split()

    # numero_pontos   = int(primeiralinha[0])
    # numero_medianas = int(primeiralinha[1])

    # entrada = []
    # vertices = []

    # for i in range(numero_pontos):
    #     a = input()
    #     entrada.append(a)

    # for i in range(numero_pontos):
    #     vList = entrada[i].split()
    #     vertice = Vertice((float(vList[0]), float(vList[1])), int(vList[2]), int(vList[3]))
    #     vertices.append(vertice)            
    
    # random.seed(10)        
    tamanho_populacao = 1
    quantidade_torneio = 3
    maximo_geracoes = 2
    pcross_over = 0.98
    pmutacao = 0.10
    utilizar_busca_local = True
    limite_tempo = 300

    ag = AlgoritmoGenetico(        
        vertices,
        tamanho_populacao,
        quantidade_torneio,
        maximo_geracoes,
        pcross_over,
        pmutacao,
        utilizar_busca_local,
        limite_tempo
    )
        
    print(ag.solucionar(numero_medianas).fitness())

