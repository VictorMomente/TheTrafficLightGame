
#******************************* TRABALHO SISTEMAS OPERACIONAIS ***********************************
#********************************    THREADS E SEMÁFOROS   ****************************************
#****************************************** 2019 **************************************************
#**************************** VICTOR HENRIQUE MOMENTÉ - 10734279 **********************************
#******************************* MURILO KAZUMI - 10818988 *****************************************
#******************************** JOÃO ALVES - 10734237 *******************************************


import pygame, random, time, threading, wave, sys
from pygame.locals import *
from threading import Thread, Lock

#Definição do tamanho da tela
largura = 900;
altura = 446;
fps = 60;

#Inicializando biblioteca
pygame.init()

#limitando o fps que o carrinho anda
clock = pygame.time.Clock(); 

#Limite da linha horizontal
linhaHorizonal = 354;

#Limite da linha vertical
linhaVertical = 155;

#Cordenada do sinal verde
cordenadaHorizontal = (358, 228);

#Cordenada do sinal vermelho
cordenadaVertical = (439, 157);

#Definindo tela 
tela = pygame.display.set_mode((largura, altura));

#Setando cenário
startMenu = pygame.image.load('arquivos/startMenu1.jpg');
aboutMenu = pygame.image.load('arquivos/aboutMenu1.jpg');
ImagemFundo = pygame.image.load('arquivos/cenario1.jpg');
sinalVerde = pygame.image.load('arquivos/sinal_verde.png');
sinalVermelho = pygame.image.load('arquivos/sinal_vermelho.png');
carros = ['arquivos/car1_horizontal.png', 'arquivos/car2_horizontal.png', 'arquivos/car3_horizontal.png']

# Pontuação do jogador
font = pygame.font.SysFont('comicsans', 30, True);
score = 0

#Booleano para controlar os sinais
abertoHorizontal = 1;

#Lista que vai armazenar os carrinhos horizontais
carrinhosH = [];

#Lista que vai armazenar os carrinhos horizontais
carrinhosV = [];

# Organizar a quantidade de carros tanto na vertical quanto na horizontal
qtddHorizontal = 0;
qtddVertical = 0;

# Variável que dita se a região crítica está sendo acessada. 1 = livre, 0 = ocupada
semaphore = 1; # igual a 0 recurso sendo utilizado, igual a 1 recurso livre

#regiãoCritica contém as cordenadas x e y da região crítica
#Entre 380 e 523 no eixo X. Entre 180 e 323 no eixo Y. 
regiaoCritica = [(379, 523), (180, 323)]; 

# Propriedade lock proveniente de threading que pode "trancar" uma thread.
lock = threading.Lock();

# variável que controla as a execução das threads
reset = 1;

# variável que diz se o jogador perdeu
perdeu = 0;

# música que vai tocar
music = 'arquivos/TrafficSound.wav'
musicLose = 'arquivos/lose.wav'

#----------------------------------Classe do carrinho--------------------------------------
class carroVertical(pygame.sprite.Sprite):
    
    #---------------------------------Construtor-------------------------------------------
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #Imagem do carrinho tem 45x26
        #centerx + 13 = a rect.right
        #centery + 23 = rect.bottom

        #Verifica se o carrinho está no jogo
        self.ativo = 1;

        #Setando a lataria do Carro        
        self.corDoCarro = random.randint(1, 3);
        if (self.corDoCarro == 1):
            self.imagemCarro = pygame.image.load('arquivos/car1_vertical.png');    
        elif (self.corDoCarro == 2):
            self.imagemCarro = pygame.image.load('arquivos/car2_vertical.png');
        elif (self.corDoCarro == 3):
            self.imagemCarro = pygame.image.load('arquivos/car3_vertical.png');

        #Propriedades do carrinho
        #Setando retângulo na imagem do carrinho
        self.rect = self.imagemCarro.get_rect();

        #Posição que o carro nasce. Centerx = 355 é o limite da linha
        self.rect.centerx = largura/2 - 10;  
        self.rect.centery = -45;

        #Booleano indicando se o carro está em movimento
        self.freiando = 0;

        #Velocidade de movimento
        self.velocidadeMaxima = 3;

        #Velocidade atual
        self.velocidadeAtual = self.velocidadeMaxima;
    #--------------------------------------------------------------------------------------

    #----------------------------------Métodos---------------------------------------------

    def posicaoY(self):
        return self.rect.bottom;

    #Põe o carro na tela
    def aparecer(self, superfice):                      
        #"blit" coloca o elemento na tela, e diz que ele é o "retângulo"
        superfice.blit(self.imagemCarro, self.rect)  

    def verificaMovimento(self):
        #Se tiver parado, volta a andar.
        if (self.freiando == 1):
            self.freiando = 0;
            self.velocidadeAtual = self.velocidadeMaxima;
        #Se tiver andando, freia. Somente se tiver antes da Linha
        elif (self.rect.centery < linhaVertical):
            self.freiando = 1;
    
    #Função usada para reativar o carrinho que está parado
    def acelera(self):
        self.freiando = 0;
        self.velocidadeAtual = self.velocidadeMaxima;

    #movimentação horizontal
    def movimentacao(self):
        global linhaVertical;
        global qtddVertical;
        #A movimentação é bloqueada assim que o carrinho passa da tela. 60 é o tamanho de px.
        if (self.rect.bottom <= altura + 60 and self.freiando != 1):   
            #Caso o carrinho esteja na tela, ele se movimenta/ Conjunto com "clock" 
            self.rect.bottom += self.velocidadeAtual
        #Caso seja acionado pra freiar e a velocidade ainda não seja 0
        elif (self.freiando == 1 and self.velocidadeAtual > 0):
            if (self.rect.centery < linhaVertical):
                self.rect.bottom += self.velocidadeAtual;
            else:    
                #freia
                self.velocidadeAtual = 0;
                linhaVertical -= 60;
        #Caso o carrinho tenha passado da tela ele é morto
        elif (self.rect.bottom >= altura + 60 and self.ativo == 1):
            carrinhosV.pop();
            qtddVertical -= 1;
    #--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------

# Classe para os carrinhos horizontais
class carroHorizontal(pygame.sprite.Sprite):
    
    #---------------------------------Construtor-------------------------------------------
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #Imagem do carrinho tem 45x26
        #centerx + 13 = a rect.right
        #centery + 23 = rect.bottom

        #Verifica se o carrinho está no jogo
        self.ativo = 1;

        #Setando a lataria do Carro        
        self.corDoCarro = random.randint(1, 3);
        if (self.corDoCarro == 1):
            self.imagemCarro = pygame.image.load('arquivos/car1_horizontal.png');    
        elif (self.corDoCarro == 2):
            self.imagemCarro = pygame.image.load('arquivos/car2_horizontal.png');
        elif (self.corDoCarro == 3):
            self.imagemCarro = pygame.image.load('arquivos/car3_horizontal.png');

        #Propriedades do carrinho
        #Setando retângulo na imagem do carrinho
        self.rect = self.imagemCarro.get_rect();

        #Posição que o carro nasce. Centerx = 354 é o limite da linha 
        self.rect.centerx = -45;  
        self.rect.centery = altura/2 + 11;

        #Booleano indicando se o carro está em movimento
        self.freiando = 0;

        #Velocidade de movimento
        self.velocidadeMaxima = 5;

        #Velocidade atual
        self.velocidadeAtual = self.velocidadeMaxima;
        
    #--------------------------------------------------------------------------------------

    #----------------------------------Métodos---------------------------------------------

    def posicaoX(self):
        return self.rect.right;

    #Põe o carro na tela
    def aparecer(self, superfice):                      
        #"blit" coloca o elemento na tela, e diz que ele é o "retângulo"
        superfice.blit(self.imagemCarro, self.rect)  

    def verificaMovimento(self):
        #Se tiver parado, volta a andar.
        if (self.freiando == 1):
            self.freiando = 0;
            self.velocidadeAtual = self.velocidadeMaxima;
        #Se tiver andando, freia. Somente se tiver antes da Linha
        elif (self.rect.centerx <= linhaHorizonal):
            self.freiando = 1;
    
    #Função usada para reativar o carrinho que está parado
    def acelera(self):
        self.freiando = 0;
        self.velocidadeAtual = self.velocidadeMaxima;

    #movimentação horizontal
    def movimentacao(self):
        global linhaHorizonal
        global qtddHorizontal;
        #A movimentação é bloqueada assim que o carrinho passa da tela. 60 é o tamanho de px.
        if (self.rect.right <= largura + 60 and self.freiando != 1):   
            #Caso o carrinho esteja na tela, ele se movimenta/ Conjunto com "clock" 
            self.rect.right += self.velocidadeAtual
        #Caso seja acionado pra freiar e a velocidade ainda não seja 0
        elif (self.freiando == 1 and self.velocidadeAtual > 0):
            if (self.rect.centerx < linhaHorizonal):
                self.rect.right += self.velocidadeAtual;
            else:    
                #freia
                self.velocidadeAtual = 0;
                linhaHorizonal -= 75;
        #Caso o carrinho tenha passado da tela ele é morto
        elif (self.rect.right >= largura + 60 and self.ativo == 1):
            #Retira o último carrinho 
            carrinhosH.pop();
            qtddHorizontal -= 1;
    #--------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------

#Função da Thread horizontal
def ruaHorizontal():
    global qtddHorizontal;
    global qtddVertical;
    global regiaoCritica;
    global semaphore;
    global reset;
    global score;
    global perdeu;

    #conta quantos carros estão parados
    contParados = 0;

    # timerGerador é o número que o auxGerador tem que chegar para gerar um novo carro
    timerGerador = random.randint(1, 3);

    # auxGerador nada mais é que um contador de segundos
    auxGerador = 0;
    
    #--------------Laço de repetição do game-----------
    while True:

        # se perdeu, fica num loop infinito até recomeçar o jogo
        while (perdeu == 1):
            if (perdeu == 0):
                break;

        # se o jogador resetou o jogo
        if (reset == 0 and len(carrinhosH) > 0):
            for k in range(len(carrinhosH)):
                carrinhosH.pop();
                qtddHorizontal = 0;
                # espera que a outra rua seja resetada antes de continuar
                if (qtddVertical == 0):
                    reset = 1;


        clock.tick(fps);
        # a cada segundo o auxGerador incrementa. 
        # Quanto menor o número menor que 1000, mais chances de vir carrinho
        if (pygame.time.get_ticks()%1000 > 982): 
            auxGerador += 1;
        
        # se deu o tanto de segundos necessários, nasce um novo carrinho
        if (auxGerador == timerGerador):
            timerGerador = random.randint(1, 2);
            auxGerador = 0;
            #Insere o carrinho no primeiro da lista, suporta no máximo 5
            if (len(carrinhosH) < 5):
                #Criando os objeetos dos carrinho.
                carrinhosH.insert(0, carroHorizontal());
                #aumenta a quantidade de carro
                qtddHorizontal += 1;

        # atualiza o cenário
        tela.blit(ImagemFundo, (0,0));

        #atualizando score
        text = font.render('Pontos: ' + str(score), 1, (255, 0, 0))
        tela.blit(text, (10,5));

        #Verificando os sinais no momento
        if (abertoHorizontal == 1):
            tela.blit(sinalVerde, cordenadaHorizontal);
            tela.blit(sinalVermelho, cordenadaVertical);
        else:
            tela.blit(sinalVerde, cordenadaVertical);
            tela.blit(sinalVermelho, cordenadaHorizontal);
        
        # Se tem carrinho andando, ele irá entrar no for e fazer os mecânismos
        if (len(carrinhosH) > 0): 
            for i in range(len(carrinhosH)):
                
                #----------------------------------Semáforo--------------------------------------
                # Verifica se pode entrar na região crítica e trocar para o sinal verde
                # o lock tranca a thread para não deixar que a outra thread acesse o semaphore
                lock.acquire();
                try:
                    # verifica se o sinal vertical está aberto
                    # porque ele só pode acessar a região crítica (alterar o semaphore)
                    # se o sinal estiver aberto
                    if (abertoHorizontal == 1):    
                        semaphore = 1;
                        for j in range(len(carrinhosH)):    
                            # Analisando regiaoCritica. Se semáforo já tiver valendo 1, significa que já ta 
                            if (carrinhosH[j].posicaoX() > regiaoCritica[0][0] and semaphore):
                                if (carrinhosH[j].posicaoX() < regiaoCritica[0][1]):
                                    # Caso entre nesse if, significa que o carro está na região crítica
                                    # e esta usando o recurso
                                    # e nesse momento, por estar trancada pelo "acquire" não há perigo
                                    # de preempção por parte da thread horizontal e alterar o semaphore.
                                    semaphore = 0;
                                    # aumenta o score
                                    score += 1;
                                    break;
                finally:
                    #Após fazer o necessário, libera a thread
                    lock.release();
                #------------------------------------------------------------------------------
               
                # se entrar nesse if significa que o carrinho atual não é o último
                # e veririca se o carro da frente está parado
                if (i+1 < len(carrinhosH)):
                    if (carrinhosH[i+1].freiando == 1):
                        carrinhosH[i].freiando = 1;
                
                #Verifica se pode freiar o carrinhosH[i] quando o sinal está fechado.
                if (abertoHorizontal == 0 and carrinhosH[i].freiando == 0):
                    carrinhosH[i].verificaMovimento();
                #verifica se o carrinhosH[i] está parado e o sinal está aberto.
                elif (abertoHorizontal == 1 and carrinhosH[i].velocidadeAtual == 0):
                    carrinhosH[i].acelera();

                #inserindo os elementos
                carrinhosH[i].aparecer(tela);

                #inicializando movimento
                carrinhosH[i].movimentacao();

        contParados = 0;
        #Também atualiza os carros Verticais  
        if (qtddVertical > 0): #experimentar por isso no for do H
            for k in range(qtddVertical):
                carrinhosV[k].aparecer(tela)
                # verifica se o carrinho ta parado
                if (carrinhosV[k].velocidadeAtual == 0):
                    contParados += 1;
            # se tiver 3 carros parados, o jogador perde o jogo
            if (contParados == 3):
                perdeu = 1;
                # chama a tela de lose;
                

        
        pygame.display.update();

    #--------------------------------------------------

#Função da Thread Vertical
def ruaVertical():
    global qtddHorizontal;
    global qtddVertical;
    global regiaoCritica;
    global semaphore;
    global reset;
    global score;
    global perdeu;
    
    #conta quantos carros estão parados
    contParados = 0;

    # timerGerador é o número que o auxGerador tem que chegar para gerar um novo carro
    timerGerador = random.randint(1, 2);

    # auxGerador nada mais é que um contador de segundos
    auxGerador = 0
    
    #--------------Laço de repetição do game-----------
    while True:

        # se perdeu, fica num loop infinito até recomeçar o jogo
        while (perdeu == 1):
            if (perdeu == 0):
                break;
        
        # se o jogador resetou o jogo
        if (reset == 0 and len(carrinhosV) > 0):
            for k in range(len(carrinhosV)):
                carrinhosV.pop();
                qtddVertical = 0;
                # espera que a outra rua seja resetada antes de continuar
                if (qtddHorizontal == 0):
                    reset = 1;

        clock.tick(fps);
        # a cada segundo o auxGerador incrementa
        # Quanto menor o número menor que 1000, mais chances de vir carrinho
        if (pygame.time.get_ticks()%1000 > 985): 
            auxGerador += 1;
        
        # se deu o tanto de segundos necessários, nasce um novo carrinho
        if (auxGerador == timerGerador):
            timerGerador = random.randint(1, 2);
            auxGerador = 0;
            #Insere o carrinho no primeiro da lista, suporta no máximo 3
            if (len(carrinhosV) < 3):
                #Criando os objeetos dos carrinho.
                carrinhosV.insert(0, carroVertical());
                #aumenta a quantidade de carro
                qtddVertical += 1;

        # atualiza o cenário
        tela.blit(ImagemFundo, (0,0));

        #atualizando score
        text = font.render('Pontos: ' + str(score), 1, (255, 0, 0))
        tela.blit(text, (10,5));

        #Verificando os sinais no momento
        if (abertoHorizontal == 1):
            tela.blit(sinalVerde, cordenadaHorizontal);
            tela.blit(sinalVermelho, cordenadaVertical);
        else:
            tela.blit(sinalVerde, cordenadaVertical);
            tela.blit(sinalVermelho, cordenadaHorizontal);

        # Se tem carrinho andando, ele irá entrar no for e fazer os mecânismos
        if (len(carrinhosV) > 0): 
            for i in range(len(carrinhosV)):
                
                #----------------------------------Semáforo--------------------------------------
                # Verifica se pode entrar na região crítica e trocar para o sinal verde
                # o lock tranca a thread para não deixar que a outra thread acesse o semaphore
                lock.acquire();
                try:
                    # verifica se o sinal vertical está aberto
                    # porque ele só pode acessar a região crítica (alterar o semaphore)
                    # se o sinal estiver aberto
                    if (abertoHorizontal == 0):
                        semaphore = 1;
                        for j in range(len(carrinhosV)):    
                            # Analisando regiaoCritica e dando valor ao semaphore
                            if (carrinhosV[j].posicaoY() > regiaoCritica[1][0]):
                                if (carrinhosV[j].posicaoY() < regiaoCritica[1][1]):
                                    # Caso entre nesse if, significa que o carro está na região crítica
                                    # e esta usando o recurso
                                    # e nesse momento, por estar trancada pelo "acquire" não há perigo
                                    # de preempção por parte da thread horizontal e alterar o semaphore.
                                    semaphore = 0;
                                    # aumenta o score
                                    score += 1;
                                    break;
                finally:
                    #Após fazer o necessário, libera a thread
                    lock.release();
                #--------------------------------------------------------------------------------
                
                # se entrar nesse if significa que o carrinho atual não é o último
                # e veririca se o carro da frente está parado
                if (i+1 < len(carrinhosV)):
                    if (carrinhosV[i+1].freiando == 1):
                        carrinhosV[i].freiando = 1;
                
                #Verifica se pode freiar o carrinhosV[i] quando o sinal está fechado.
                if (abertoHorizontal == 1 and carrinhosV[i].freiando == 0):
                    carrinhosV[i].verificaMovimento();
                #verifica se o carrinhosV[i] está parado e o sinal está aberto.
                elif (abertoHorizontal == 0 and carrinhosV[i].velocidadeAtual == 0):
                    carrinhosV[i].acelera();
                
                #inserindo os elementos
                carrinhosV[i].aparecer(tela);
                
                #inicializando movimento
                carrinhosV[i].movimentacao();
        
        contParados = 0;
        #Também atualiza os carros horizontais
        if (qtddHorizontal > 0):
            for k in range(qtddHorizontal):
                carrinhosH[k].aparecer(tela)
                # verifica se o carrinho ta parado
                if (carrinhosH[k].velocidadeAtual == 0):
                    contParados += 1;
            # se tiver 3 carros parados, o jogador perde o jogo
            if (contParados == 5):
                perdeu = 1;
                # chama a tela de lose;
        
        pygame.display.update();

    #--------------------------------------------------


#Menu do jogo
def menuGame():  
    # flag auxiliar para chamar as telas do game.
    flag = 0;

    # Iniciando a música do jogo
    file_path = 'arquivos/startMenu.wav'
    file_wav = wave.open(file_path)
    frequency = file_wav.getframerate()
    pygame.mixer.init(frequency=frequency)
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.set_volume(0.7)
    pygame.mixer.music.play(loops=10)
    menu = startMenu;

    while True:
        tela.blit(menu, (0,0));
        pygame.display.update();
        # verificação dos botões apertados no jogo.
        for event in pygame.event.get():
            
            # Se clicar no X ele fecha o game
            if event.type == QUIT: 
                pygame.quit();

            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos();
                
                #coordenadas do botão jogar
                if (((pos[0] > 534 and pos[0] < 750) and (pos[1] > 119 and pos[1] < 184)) and menu == startMenu):
                    flag = 1;
                #coordenadas do botão sobre
                if (((pos[0] > 538 and pos[0] < 754) and (pos[1] > 238 and pos[1] < 303)) and menu == startMenu):
                    menu = aboutMenu
                #coordenadas do botão menu
                if (((pos[0] > 501 and pos[0] < 713) and (pos[1] > 347 and pos[1] < 411)) and menu == aboutMenu):
                    menu = startMenu;
                #coordenadas do botão sair
                elif (((pos[0] > 542 and pos[0] < 756) and (pos[1] > 347 and pos[1] < 411)) and menu == startMenu):
                    pygame.quit();
                    sys.exit()
        # clicou em iniciar jogo, sai do while menu        
        if (flag):
            flag = 0;
            break;

#tela de derrota
def lose():
    global music;
    global musicLose;
    global perdeu;

    #setando o texto dos pontos
    text = font.render('Pontos: ' + str(score), 1, (255, 0, 0))

    # flag auxiliar para chamar as telas do game.
    flag = 0;

    # Iniciando a música do jogo
    file_path = musicLose;
    file_wav = wave.open(file_path)
    frequency = file_wav.getframerate()
    pygame.mixer.init(frequency=frequency)
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.set_volume(0.6)
    pygame.mixer.music.play(loops=10)
    
    #carrego o cenário de lose
    lose = pygame.image.load('arquivos/lose1.jpg');
    
    while True:

        # atualizando tela e o scrore
        tela.blit(lose, (0,0));
        tela.blit(text, (382, 162));
        pygame.display.update();

        # verificação dos botões apertados no jogo.
        for event in pygame.event.get():
            #atualizando score
            
            # Se clicar no X ele fecha o game
            if event.type == QUIT: 
                pygame.quit();
                sys.exit()

             # se clicar em alguma tecla
            if event.type == KEYDOWN:
                if event.key == K_f:
                    flag = 1;
                    music = 'arquivos/secret.wav'
                    musicLose = 'arquivos/loseF.wav'

            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos();
                
                #coordenadas do botão recomeçar
                if ((pos[0] > 336 and pos[0] < 548) and (pos[1] > 240 and pos[1] < 304)):
                    #seta a flag de saída
                    flag = 1;
                    music = 'arquivos/TrafficSound.wav'
                    musicLose = 'arquivos/lose.wav'

                #coordenadas do botão sair
                if ((pos[0] > 336 and pos[0] < 548) and (pos[1] > 346 and pos[1] < 410)):
                    pygame.quit();
                    sys.exit()
            
        # clicou em iniciar jogo, sai do while menu        
        if (flag != 0):
            break;
    
    # Iniciando a música do transito antes de encerrar
    file_path = music
    file_wav = wave.open(file_path)
    frequency = file_wav.getframerate()
    pygame.mixer.init(frequency=frequency)
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(loops=20)
    
    

#------------------------------------------main----------------------------------------------
def carTransito():
    #declarando a variavel global no escopo
    global linhaHorizonal;
    global linhaVertical;
    global abertoHorizontal;
    global semaphore;
    global reset;
    global score;
    global perdeu;
    global music;

    # Iniciando a música do jogo
    file_path = music
    file_wav = wave.open(file_path)
    frequency = file_wav.getframerate()
    pygame.mixer.init(frequency=frequency)
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(loops=20)
    
    #--------------Laço de repetição do game-----------
    while True:
        
        #se o jogador perdeu
        if (perdeu == 1):
            #chama a função lose
            lose();
            #reseta as variáveis
            reset = 0;
            score = 0;
            perdeu = 0;
            linhaVertical = 155;
            linhaHorizonal = 354;

        # verificação dos botões apertados no jogo.
        for event in pygame.event.get():
            
            # Se clicar no X ele fecha o game
            if event.type == QUIT: 
                pygame.quit();
                sys.exit()
            
            # se clicar em alguma tecla
            if event.type == KEYDOWN:

                # se a tecla for espaço, verifica o semaphore e solicita a troca dos sinais.
                if event.key == K_SPACE:
                    # Tranca a thread principal para verificar o valor do semáforo, evitando o seguinte caso:
                    # o if é verificado, mas logo em seguida é preemptado, e a thread que preemptou altera
                    # o valor do semaphore para 0, e quando esse threadh principal volta a executar, 
                    # ela ainda vai achar que o semaphore é 1, mas na verdade não é mais.
                    lock.acquire();
                    if (semaphore == 1): #recurso disponivel, pode trocar os sinais
                        if (abertoHorizontal == 0):  
                            abertoHorizontal = 1;
                            linhaVertical = 155;
                        else:
                            abertoHorizontal = 0;
                            linhaHorizonal = 354;
                    lock.release();
                    
                # se a teclar for esc, fecha o jogo.
                if event.key == K_ESCAPE:
                    pygame.quit();
                    sys.exit()
                    
    #--------------------------------------------------
#----------------------------------------------------------------------------------------------        

#----------------------------Inicializando threads e prefiéricos-------------------------------

#Setando nome do jogo
pygame.display.set_caption('The traffic light');

# Chama o Menu do jogo
menuGame();

# Inicializando threads da rua horizontal
t0 = threading.Thread(target = ruaHorizontal, name = 'carrosHorizontal');
t0.setDaemon(True);
t0.start();

# Inicializando threads da rua vertical
t1 = threading.Thread(target = ruaVertical, name = 'carrosVertical');
t1.setDaemon(True);
t1.start();

#chama a Main
carTransito();
#----------------------------------------------------------------------------------------------