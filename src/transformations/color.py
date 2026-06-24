import cv2
import numpy as np

def apply_isolate_color(image: np.ndarray, color_name: str = 'red') -> np.ndarray:
    r"""
    Isola uma cor específica na imagem (mantendo-a colorida) e converte o restante em escala de cinza.
    
    A técnica utiliza a conversão para o espaço de cores HSV (Hue, Saturation, Value),
    pois este espaço desacopla a informação cromática (matiz/tonalidade - H) da intensidade 
    luminosa (brilho - V) e da pureza da cor (saturação - S).
    
    Para segmentar a cor, define-se um intervalo de aceitação no espaço HSV [H_min, S_min, V_min] 
    até [H_max, S_max, V_max]. A máscara binária M(x, y) é calculada por:
        M(x, y) = \begin{cases} 
            255 & \text{se } H(x,y) \in [H_{\min}, H_{\max}] \land S(x,y) \in [S_{\min}, S_{\max}] \land V(x,y) \in [V_{\min}, V_{\max}] \\ 
            0 & \text{caso contrário} 
        \end{cases}
    
    Particularidade para a cor Vermelha ('red'):
    Como o matiz vermelho está localizado nas extremidades do círculo de matizes (próximo a 0° e 360°),
    sua representação no OpenCV (onde H varia de 0 a 179) é dividida em duas faixas:
        - Faixa inferior: H_1 \in [0, 10]
        - Faixa superior: H_2 \in [160, 179]
    O algoritmo calcula duas máscaras independentes (M_1 e M_2) e realiza a união lógica (OR):
        M_{\text{red}}(x, y) = M_1(x, y) \lor M_2(x, y)
        
    Composição Final:
    Os pixels que não pertencem ao intervalo de interesse são convertidos para tons de cinza:
        g(x, y) = \begin{cases} 
            f(x, y) & \text{se } M(x, y) = 255 \\ 
            [\text{gray}(x, y), \text{gray}(x, y), \text{gray}(x, y)] & \text{se } M(x, y) = 0 
        \end{cases}
        
    Parâmetros:
        image (np.ndarray): Imagem BGR de entrada.
        color_name (str): Cor a ser isolada ('red', 'green', 'blue', 'yellow', 'cyan', 'magenta').
        
    Retorna:
        np.ndarray: Imagem com a cor selecionada preservada e fundo desaturado (escala de cinza).
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Define as faixas de cores no espaço HSV do OpenCV
    ranges = {
        'red': ([0, 100, 100], [10, 255, 255], [160, 100, 100], [180, 255, 255]),
        'green': ([35, 100, 100], [85, 255, 255]),
        'blue': ([100, 100, 100], [140, 255, 255]),
        'yellow': ([20, 100, 100], [30, 255, 255]),
        'cyan': ([85, 100, 100], [100, 255, 255]),
        'magenta': ([140, 100, 100], [160, 255, 255])
    }
    
    if color_name not in ranges:
        return image
    
    target_range = ranges[color_name]
    
    if color_name == 'red':
        mask1 = cv2.inRange(hsv, np.array(target_range[0]), np.array(target_range[1]))
        mask2 = cv2.inRange(hsv, np.array(target_range[2]), np.array(target_range[3]))
        mask = cv2.bitwise_or(mask1, mask2)
    else:
        mask = cv2.inRange(hsv, np.array(target_range[0]), np.array(target_range[1]))
    
    # Cria uma versão em escala de cinza de 3 canais
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    
    # Mescla as imagens: mantém a cor original onde a máscara for 255 e usa a escala de cinza onde for 0
    res = np.where(mask[:, :, None] == 255, image, gray_bgr)
    return res
