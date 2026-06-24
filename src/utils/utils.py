import cv2
import numpy as np
from PIL import Image, ImageTk

def cv2_to_pil(image: np.ndarray) -> Image.Image:
    """
    Converte uma imagem no formato OpenCV (matriz NumPy) para o formato PIL Image.
    
    A função realiza o tratamento de canais de cores:
        - Se a imagem de entrada for em escala de cinza (2D ou 3D com 1 canal), 
          ela é convertida para RGB replicando o canal cinza.
        - Se a imagem for BGR (padrão do OpenCV), ela é transposta para RGB,
          pois a biblioteca PIL espera a ordenação clássica de canais [Vermelho, Verde, Azul].
          
    Parâmetros:
        image (np.ndarray): Matriz NumPy contendo os pixels da imagem.
        
    Retorna:
        PIL.Image.Image: Imagem convertida e compatível com a biblioteca Pillow.
    """
    if len(image.shape) == 2 or image.shape[2] == 1:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    else:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(image_rgb)

def pil_to_tk(pil_image: Image.Image) -> ImageTk.PhotoImage:
    """
    Converte um objeto PIL Image em uma estrutura PhotoImage do Tkinter.
    
    Esta conversão é obrigatória para que o widget Canvas ou Label do CustomTkinter/Tkinter 
    consiga renderizar e gerenciar o bitmap em memória da imagem.
    
    Parâmetros:
        pil_image (PIL.Image.Image): Instância de imagem Pillow.
        
    Retorna:
        ImageTk.PhotoImage: Referência de imagem Tkinter compatível para renderização.
    """
    return ImageTk.PhotoImage(pil_image)

def calculate_histogram(image: np.ndarray) -> list:
    """
    Calcula as frequências de distribuição de intensidade (histograma) para cada canal de cor.
    
    Utiliza o método otimizado do OpenCV (cv2.calcHist) para computar a contagem de pixels
    para cada um dos 256 níveis de cinza/cor no intervalo [0, 255].
    
    Se a imagem for multicanal (BGR), o histograma é calculado individualmente para cada canal
    (Blue, Green, Red) e associado a uma cor de representação gráfica ('b', 'g', 'r').
    Se for escala de cinza, calcula apenas o histograma de luminância ('k').
    
    Parâmetros:
        image (np.ndarray): Matriz NumPy da imagem (BGR ou Cinza).
        
    Retorna:
        list[tuple[np.ndarray, str]]: Lista de tuplas contendo o array do histograma (256 elementos float)
                                      e a respectiva cor de plotagem ('r', 'g', 'b' ou 'k').
    """
    if len(image.shape) == 2 or image.shape[2] == 1:
        hist = cv2.calcHist([image], [0], None, [256], [0, 256])
        return [(hist.flatten(), 'k')]
        
    hist_data = []
    colors = ('b', 'g', 'r')
    for i, col in enumerate(colors):
        hist = cv2.calcHist([image], [i], None, [256], [0, 256])
        hist_data.append((hist.flatten(), col))
    return hist_data

def resize_to_fit(image: np.ndarray, max_width: int, max_height: int) -> np.ndarray:
    r"""
    Redimensiona a imagem para caber dentro das dimensões máximas fornecidas mantendo a proporção de aspecto.
    
    A proporção de aspecto (aspect ratio) A é definida por:
        A = W / H
    O algoritmo garante que:
        W_{new} \le W_{max} \quad \text{e} \quad H_{new} \le H_{max}
    preservando a relação espacial e evitando distorção/estiramento da imagem original.
    Utiliza interpolação cv2.INTER_AREA, recomendada para amostragem decrescente (downsampling),
    evitando artefatos de aliasing.
    
    Parâmetros:
        image (np.ndarray): Imagem OpenCV BGR de entrada.
        max_width (int): Largura máxima permitida para a viewport.
        max_height (int): Altura máxima permitida para a viewport.
        
    Retorna:
        np.ndarray: Imagem redimensionada de modo proporcional e ajustada à moldura.
    """
    h, w = image.shape[:2]
    aspect = w / h if h != 0 else 1
    
    if w > max_width:
        w = max_width
        h = int(w / aspect) if aspect != 0 else 1
    
    if h > max_height:
        h = max_height
        w = int(h * aspect)
        
    w = max(1, w)
    h = max(1, h)
    return cv2.resize(image, (w, h), interpolation=cv2.INTER_AREA)
