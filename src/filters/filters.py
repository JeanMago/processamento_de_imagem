import cv2
import numpy as np

def apply_gaussian_blur(image: np.ndarray, kernel_size: int = 5, sigma: float = 1.0) -> np.ndarray:
    r"""
    Aplica a suavização por Filtro Gaussiano (Filtro Passa-Baixas Espacial).
    
    A operação realiza a convolução da imagem de entrada f(x,y) com um kernel isotrópico h(x,y)
    baseado na distribuição gaussiana bidimensional:
        G(x, y, \sigma) = \frac{1}{2 \pi \sigma^2} e^{-\frac{x^2 + y^2}{2 \sigma^2}}
    onde:
        - \sigma representa o desvio padrão (grau de espalhamento/borramento).
        - kernel_size é a dimensão do vizinho espacial quadrado (deve ser ímpar e positivo).
    
    Parâmetros:
        image (np.ndarray): Matriz tridimensional da imagem no formato BGR.
        kernel_size (int): Tamanho da janela local do kernel (N x N).
        sigma (float): Desvio padrão da distribuição Gaussiana.
        
    Retorna:
        np.ndarray: Imagem suavizada (atenuada em altas frequências).
    """
    if kernel_size % 2 == 0:
        kernel_size += 1
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigmaX=sigma)

def apply_median_blur(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    r"""
    Aplica o Filtro de Mediana (Filtro não-linear estatístico de ordem).
    
    Substitui a intensidade de cada píxel f(x,y) pela mediana dos valores contidos na 
    janela de vizinhança S_xy:
        g(x, y) = \text{mediana} \{ f(s, t) \} \text{ para } (s, t) \in S_{xy}
    Esse filtro é excelente para remover ruídos impulsivos (tipo "sal e pimenta") sem borrar
    tanto as bordas da imagem quanto os filtros lineares de média.
    
    Parâmetros:
        image (np.ndarray): Matriz tridimensional da imagem de entrada.
        kernel_size (int): Tamanho do diâmetro da janela (deve ser ímpar e positivo).
        
    Retorna:
        np.ndarray: Imagem filtrada sem ruídos espúrios de alta variação pontual.
    """
    if kernel_size % 2 == 0:
        kernel_size += 1
    return cv2.medianBlur(image, kernel_size)

def apply_laplacian(image: np.ndarray, ksize: int = 3, scale: float = 1.0, delta: float = 0.0) -> np.ndarray:
    r"""
    Aplica o operador Laplaciano (Filtro Passa-Altas Espacial).
    
    O operador Laplaciano de uma função bidimensional f(x,y) calcula a segunda derivada parcial
    espacial, destacando transições abruptas de intensidade (bordas isotrópicas):
        \nabla^2 f = \frac{\partial^2 f}{\partial x^2} + \frac{\partial^2 f}{\partial y^2}
    No domínio discreto, isto é aproximado por convolução com kernels de aproximação de diferenças
    finitas de segunda ordem. A magnitude resultante é convertida e normalizada.
    
    Parâmetros:
        image (np.ndarray): Imagem BGR de entrada.
        ksize (int): Tamanho do kernel para aproximar a derivada (ímpar).
        scale (float): Fator opcional de escala para as derivadas calculadas.
        delta (float): Valor opcional somado ao resultado antes do mapeamento uint8.
        
    Retorna:
        np.ndarray: Imagem BGR de contornos destacados.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F, ksize=ksize, scale=scale, delta=delta)
    abs_laplacian = cv2.convertScaleAbs(laplacian)
    return cv2.cvtColor(abs_laplacian, cv2.COLOR_GRAY2BGR)

def apply_sobel(image: np.ndarray, direction: str = 'both', ksize: int = 3) -> np.ndarray:
    r"""
    Aplica o Operador Sobel para detecção de bordas orientadas e magnitude de gradiente.
    
    Calcula aproximações digitais das derivadas parciais espaciais de primeira ordem 
    nas direções horizontal (x) e vertical (y) usando convoluções com kernels 3x3 ou maiores:
        G_x = S_x * f(x,y)
        G_y = S_y * f(x,y)
    
    Se direction for 'both', calcula a magnitude aproximada do gradiente:
        |G| \approx 0.5 * |G_x| + 0.5 * |G_y|
        
    Parâmetros:
        image (np.ndarray): Imagem BGR de entrada.
        direction (str): 'horizontal', 'vertical' ou 'both'.
        ksize (int): Tamanho do kernel Sobel (ímpar e entre 1 e 31).
        
    Retorna:
        np.ndarray: Imagem contendo as bordas destacadas nas orientações solicitadas.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    if direction == 'horizontal' or direction == 'both':
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=ksize)
        abs_sobelx = cv2.convertScaleAbs(sobelx)
        
    if direction == 'vertical' or direction == 'both':
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=ksize)
        abs_sobely = cv2.convertScaleAbs(sobely)
        
    if direction == 'both':
        combined = cv2.addWeighted(abs_sobelx, 0.5, abs_sobely, 0.5, 0)
        return cv2.cvtColor(combined, cv2.COLOR_GRAY2BGR)
    elif direction == 'horizontal':
        return cv2.cvtColor(abs_sobelx, cv2.COLOR_GRAY2BGR)
    else:
        return cv2.cvtColor(abs_sobely, cv2.COLOR_GRAY2BGR)
