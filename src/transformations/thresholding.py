import cv2
import numpy as np

def apply_binarization(image: np.ndarray, threshold: int = 127, method: str = 'Binary', block_size: int = 11, c: float = 2.0) -> np.ndarray:
    r"""
    Aplica diferentes métodos de limiarização (binarização) sobre uma imagem.
    
    A função converte a imagem de entrada BGR para escala de cinza de canal único
    e realiza a binarização com base no método escolhido. Os métodos suportados são:
    
    1. Limiarização Global (Threshold Fixo):
       Compara cada pixel f(x, y) com um limiar global T:
       - 'Binary':
         g(x, y) = \begin{cases} 255 & \text{se } f(x, y) > T \\ 0 & \text{caso contrário} \end{cases}
       - 'Binary Inverse':
         g(x, y) = \begin{cases} 0 & \text{se } f(x, y) > T \\ 255 & \text{caso contrário} \end{cases}
       - 'Truncate':
         g(x, y) = \begin{cases} T & \text{se } f(x, y) > T \\ f(x, y) & \text{caso contrário} \end{cases}
       - 'To Zero':
         g(x, y) = \begin{cases} f(x, y) & \text{se } f(x, y) > T \\ 0 & \text{caso contrário} \end{cases}
       - 'To Zero Inverse':
         g(x, y) = \begin{cases} 0 & \text{se } f(x, y) > T \\ f(x, y) & \text{caso contrário} \end{cases}

    2. Algoritmo de Otsu ('Otsu'):
       Calcula o limiar global ideal T* de maneira automática a partir do histograma,
       minimizando a variância intra-classe das populações de fundo (background, 0)
       e objeto (foreground, 1):
         \sigma_w^2(T) = \omega_0(T) \sigma_0^2(T) + \omega_1(T) \sigma_1^2(T)
       onde \omega_i(T) e \sigma_i^2(T) são a probabilidade de ocorrência e a variância
       de cada classe, respectivamente.

    3. Limiarização Adaptativa Local:
       Calcula um limiar dinâmico T(x, y) para cada pixel individual com base em uma
       janela de vizinhança de dimensões B \times B (definida por block_size):
       - 'Adaptive Mean':
         T(x, y) = \mu(x, y) - C
         onde \mu(x, y) é a média aritmética local da intensidade dos pixels na vizinhança.
       - 'Adaptive Gaussian':
         T(x, y) = G(x, y) - C
         onde G(x, y) é a média local ponderada por uma distribuição Gaussiana.

    Parâmetros:
        image (np.ndarray): Matriz tridimensional da imagem no formato BGR.
        threshold (int): Limiar global T utilizado nos métodos estáticos (0 a 255).
        method (str): Nome do método de limiarização.
        block_size (int): Tamanho da janela local quadrada para métodos adaptativos (deve ser ímpar e >= 3).
        c (float): Constante C subtraída da média local calculada no limiar adaptativo.
        
    Retorna:
        np.ndarray: Imagem binarizada no espaço BGR (3 canais idênticos).
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Garante que block_size seja ímpar e >= 3 para a limiarização adaptativa
    if block_size < 3:
        block_size = 3
    elif block_size % 2 == 0:
        block_size += 1

    method_lower = method.lower()
    if method_lower == 'binary':
        _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    elif method_lower in ('binary inverse', 'binary_inv', 'binary inv'):
        _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
    elif method_lower in ('truncate', 'trunc'):
        _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_TRUNC)
    elif method_lower in ('to zero', 'tozero'):
        _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_TOZERO)
    elif method_lower in ('to zero inverse', 'tozero_inv', 'to zero inv'):
        _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_TOZERO_INV)
    elif method_lower == 'otsu':
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    elif method_lower in ('adaptive mean', 'adaptive_mean'):
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                       cv2.THRESH_BINARY, block_size, c)
    elif method_lower in ('adaptive gaussian', 'adaptive_gaussian'):
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, block_size, c)
    else:
        # Fallback padrão
        _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        
    return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
