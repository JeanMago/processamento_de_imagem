import cv2
import numpy as np

def apply_brightness_contrast(image: np.ndarray, brightness: float = 0.0, contrast: float = 0.0) -> np.ndarray:
    """
    Aplica uma transformação linear pontual de intensidade para brilho e contraste.
    
    A transformação segue o modelo matemático clássico:
        g(x, y) = \\alpha \\cdot f(x, y) + \\beta
    onde:
        - \\alpha (ganho) controla o contraste. Valores > 1 aumentam o contraste; valores < 1 reduzem.
        - \\beta (bias) ajusta o nível de brilho transladando o histograma linearmente.
    
    O mapeamento de contraste converte a escala linear de entrada [-100, 100] para a escala real:
        - Para contraste positivo (>= 0): \\alpha = 1.0 + (contrast / 100.0) * 2.0  (mapeia de 1.0 a 3.0)
        - Para contraste negativo (< 0): \\alpha = 1.0 + (contrast / 100.0) * 0.9  (mapeia de 0.1 a 1.0)
    
    A operação realiza a aritmética com ponto flutuante (float32) e aplica corte (clipping)
    sobre o intervalo [0, 255] para evitar comportamento de overflow circular ao converter de volta para uint8.
    
    Parâmetros:
        image (np.ndarray): Matriz tridimensional da imagem no formato BGR.
        brightness (float): Fator de deslocamento de brilho \\beta ([-100, 100]).
        contrast (float): Fator de contraste linear ([-100, 100]).
        
    Retorna:
        np.ndarray: Imagem com brilho e contraste ajustados.
    """
    if contrast >= 0:
        alpha = 1.0 + (contrast / 100.0) * 2.0
    else:
        alpha = 1.0 + (contrast / 100.0) * 0.9
        
    beta = brightness
    
    adjusted = np.clip(image.astype(np.float32) * alpha + beta, 0, 255).astype(np.uint8)
    return adjusted

def apply_invert_colors(image: np.ndarray) -> np.ndarray:
    """
    Inverte o mapa de tons da imagem (negativo fotográfico).
    
    Para cada canal de cor, realiza a operação complementar:
        g(x, y) = 255 - f(x, y)
        
    Parâmetros:
        image (np.ndarray): Imagem de entrada.
        
    Retorna:
        np.ndarray: Imagem com valores de cor invertidos elemento a elemento (bitwise NOT).
    """
    return cv2.bitwise_not(image)

def apply_grayscale(image: np.ndarray) -> np.ndarray:
    """
    Converte a imagem BGR para escala de cinza de 3 canais idênticos.
    
    A conversão segue a fórmula de luminância ITU-R BT.601 (Luma):
        Y = 0.299 \\cdot R + 0.587 \\cdot G + 0.114 \\cdot B
    Após calcular a luminância de canal único Y, replica-se a matriz 3 vezes para manter
    a compatibilidade tridimensional BGR das funções de visualização.
    
    Parâmetros:
        image (np.ndarray): Imagem colorida BGR de entrada.
        
    Retorna:
        np.ndarray: Imagem em escala de cinza com dimensionalidade BGR (3 canais idênticos).
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

def apply_histogram_equalization(image: np.ndarray) -> np.ndarray:
    """
    Aplica equalização de histograma preservando a informação de croma.
    
    A equalização de histograma redistribui as intensidades dos píxels utilizando a Função 
    de Distribuição Acumulada (CDF) normalizada para mapear os tons de forma a aproximar o histograma 
    de uma distribuição uniforme. 
    Para evitar distorções de cor e alterações no balanço cromático da imagem, o processo:
        1. Converte a imagem BGR para o espaço de cores YUV.
        2. Aplica a equalização estritamente no canal Y (luminância/luminosidade).
        3. Converte a imagem equalizada de volta ao espaço BGR original.
        
    Parâmetros:
        image (np.ndarray): Imagem BGR de entrada.
        
    Retorna:
        np.ndarray: Imagem com contraste global maximizado.
    """
    img_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
    return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
