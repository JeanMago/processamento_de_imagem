import cv2
import numpy as np

def apply_resize(image: np.ndarray, width: int, height: int, interpolation: int = cv2.INTER_LINEAR) -> np.ndarray:
    r"""
    Redimensiona a imagem para as dimensões absolutas de largura (width) e altura (height).
    
    O mapeamento geométrico de coordenadas espaciais (x, y) de destino para as coordenadas (u, v) 
    de origem é resolvido por meio de interpolação digital. Por padrão, utiliza-se a 
    Interpolação Bilinear (cv2.INTER_LINEAR), que realiza uma interpolação linear ponderada 
    em ambas as direções usando os 4 vizinhos mais próximos:
        f(x, y) \approx (1 - \Delta x)(1 - \Delta y) f(x_1, y_1) + \Delta x (1 - \Delta y) f(x_2, y_1) + (1 - \Delta x) \Delta y f(x_1, y_2) + \Delta x \Delta y f(x_2, y_2)
        
    Parâmetros:
        image (np.ndarray): Imagem BGR de entrada.
        width (int): Largura de destino W_new.
        height (int): Altura de destino H_new.
        interpolation (int): Flag do OpenCV para o método de interpolação (ex: cv2.INTER_NEAREST, cv2.INTER_LINEAR, cv2.INTER_CUBIC, cv2.INTER_AREA).
        
    Retorna:
        np.ndarray: Imagem redimensionada nas dimensões especificadas.
    """
    if width <= 0 or height <= 0:
        return image
    return cv2.resize(image, (width, height), interpolation=interpolation)

def apply_rotation(image: np.ndarray, angle: float, keep_bounds: bool = True) -> np.ndarray:
    r"""
    Rotaciona a imagem em torno de seu ponto central geométrico por um ângulo em graus.
    
    A rotação bidimensional de um ponto por um ângulo \theta é uma transformação afim. A matriz 
    de transformação afim 2x3 M calcula as coordenadas rotacionadas (x', y') a partir das originais (x, y):
        \begin{bmatrix} x' \\ y' \end{bmatrix} = \begin{bmatrix} \alpha & \beta \\ -\beta & \alpha \end{bmatrix} \begin{bmatrix} x - x_c \\ y - y_c \end{bmatrix} + \begin{bmatrix} x_c \\ y_c \end{bmatrix}
    onde:
        - (x_c, y_c) é o centro de rotação da imagem: x_c = W / 2, y_c = H / 2.
        - \alpha = \cos(\theta)
        - \beta = \sin(\theta)
        
    Se keep_bounds for True:
        As dimensões da imagem de saída são expandidas de modo a conter toda a imagem original rotacionada 
        sem cortes periféricos. As novas dimensões W_{new} e H_{new} são calculadas por:
            W_{new} = H \cdot |\sin(\theta)| + W \cdot |\cos(\theta)|
            H_{new} = H \cdot |\cos(\theta)| + W \cdot |\sin(\theta)|
        Em seguida, a matriz de rotação M é transladada para alinhar o novo centro:
            M_{0, 2} \leftarrow M_{0, 2} + \frac{W_{new}}{2} - x_c
            M_{1, 2} \leftarrow M_{1, 2} + \frac{H_{new}}{2} - y_c
            
    Se keep_bounds for False:
        A imagem resultante mantém as mesmas dimensões da imagem de entrada (W, H), resultando em corte
        das quinas da imagem que excedem a janela.
        
    Parâmetros:
        image (np.ndarray): Imagem BGR de entrada.
        angle (float): Ângulo de rotação \theta em graus (valores positivos rotacionam no sentido anti-horário).
        keep_bounds (bool): Se True, ajusta o tamanho da tela final para não cortar a imagem.
        
    Retorna:
        np.ndarray: Imagem rotacionada.
    """
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    
    # Calcula a matriz de rotação afim 2x3 M
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    if keep_bounds:
        # Extrai os coeficientes trigonométricos para calcular os novos limites
        cos_val = np.abs(M[0, 0])
        sin_val = np.abs(M[0, 1])
        
        new_w = int((h * sin_val) + (w * cos_val))
        new_h = int((h * cos_val) + (w * sin_val))
        
        # Ajusta a translação na matriz M para garantir o alinhamento central correto no novo canvas
        M[0, 2] += (new_w / 2) - center[0]
        M[1, 2] += (new_h / 2) - center[1]
        
        rotated = cv2.warpAffine(image, M, (new_w, new_h))
    else:
        rotated = cv2.warpAffine(image, M, (w, h))
        
    return rotated

def apply_scale(image: np.ndarray, scale_x: float, scale_y: float = None, interpolation: int = cv2.INTER_LINEAR) -> np.ndarray:
    r"""
    Aplica um fator de escala (multiplicativo) nas direções X e Y sobre as dimensões da imagem.
    
    As novas dimensões são dadas pelo produto das dimensões originais pelos respectivos fatores:
        W_{new} = \lfloor W \cdot s_x \rfloor
        H_{new} = \lfloor H \cdot s_y \rfloor
        
    Parâmetros:
        image (np.ndarray): Imagem BGR de entrada.
        scale_x (float): Fator multiplicativo de escala horizontal s_x (ex: 1.5 para aumentar 50%).
        scale_y (float): Fator multiplicativo de escala vertical s_y. Se for None, s_y = s_x (escala isotrópica/uniforme).
        interpolation (int): Flag do OpenCV para o método de interpolação digital.
        
    Retorna:
        np.ndarray: Imagem escalonada.
    """
    if scale_y is None:
        scale_y = scale_x
    if scale_x <= 0 or scale_y <= 0:
        return image
    h, w = image.shape[:2]
    new_w = int(w * scale_x)
    new_h = int(h * scale_y)
    if new_w <= 0 or new_h <= 0:
        return image
    return cv2.resize(image, (new_w, new_h), interpolation=interpolation)
