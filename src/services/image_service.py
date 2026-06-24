import cv2
import os
import numpy as np

class ImageService:
    def __init__(self):
        """
        Inicializa o serviço de processamento e gerenciamento do estado da imagem.
        
        Atributos:
            original_image (np.ndarray | None): Cópia da imagem original carregada do disco (imutável).
            current_image (np.ndarray | None): Estado atual da imagem após aplicação de filtros/transformações.
            history (list[np.ndarray]): Pilha de histórico de estados da imagem para suporte a Undo/Redo.
            history_index (int): Índice que aponta para a posição atual na pilha do histórico.
        """
        self.original_image = None
        self.current_image = None
        self.history = []
        self.history_index = -1

    def load_image(self, file_path: str) -> np.ndarray:
        """
        Carrega uma imagem a partir de um caminho no sistema de arquivos.
        
        Realiza a leitura utilizando OpenCV e inicializa os buffers de imagem original, 
        imagem atual e a pilha de histórico.
        
        Parâmetros:
            file_path (str): Caminho absoluto ou relativo do arquivo de imagem.
            
        Retorna:
            np.ndarray: Cópia da imagem carregada (no formato de canais BGR padrão do OpenCV).
            
        Exceções:
            FileNotFoundError: Caso o arquivo não seja encontrado no caminho fornecido.
            ValueError: Caso o OpenCV falhe ao decodificar a imagem (ex: formato corrompido).
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        image = cv2.imread(file_path)
        if image is None:
            raise ValueError("Failed to load image.")
        
        # Garante cópias profundas dos dados pixelados (numpy array) para evitar problemas de referência mútua
        self.original_image = image.copy()
        self.current_image = image.copy()
        self.history = [self.current_image.copy()]
        self.history_index = 0
        return self.current_image

    def save_image(self, file_path: str) -> bool:
        """
        Grava a imagem atual no disco no formato correspondente à extensão do caminho fornecido.
        
        Parâmetros:
            file_path (str): Caminho onde a imagem será salva.
            
        Retorna:
            bool: True se a gravação ocorreu com sucesso, False caso contrário.
            
        Exceções:
            ValueError: Se não houver nenhuma imagem em memória para ser salva.
        """
        if self.current_image is None:
            raise ValueError("No image to save.")
        
        success = cv2.imwrite(file_path, self.current_image)
        return success

    def update_current_image(self, new_image: np.ndarray, add_to_history: bool = True) -> None:
        """
        Atualiza o estado atual da imagem com uma nova matriz e manipula o histórico.
        
        Se a flag 'add_to_history' for ativada:
            - Descarta qualquer ramo futuro no histórico (caso tenha havido operações de 'Undo' 
              seguidas de uma nova modificação).
            - Insere uma cópia da nova imagem no topo da pilha.
            - Limita o tamanho do histórico a um máximo de 20 estados para otimização de uso de memória RAM.
            
        Parâmetros:
            new_image (np.ndarray): Nova imagem resultante de processamento.
            add_to_history (bool): Define se o novo estado deve ser registrado na pilha de Undo/Redo.
        """
        self.current_image = new_image.copy()
        if add_to_history:
            # Remove o ramo do histórico à frente se o usuário alterou a imagem após fazer Undo
            self.history = self.history[:self.history_index + 1]
            self.history.append(self.current_image.copy())
            self.history_index += 1
            
            # Limita a pilha de histórico a 20 operações para proteção de estouro de memória
            if len(self.history) > 20:
                self.history.pop(0)
                self.history_index -= 1

    def undo(self) -> np.ndarray | None:
        """
        Retrocede um estado na pilha de histórico (Desfazer).
        
        Retorna:
            np.ndarray | None: A imagem anterior na pilha ou None se o histórico estiver no início.
        """
        if self.history_index > 0:
            self.history_index -= 1
            self.current_image = self.history[self.history_index].copy()
            return self.current_image
        return None

    def redo(self) -> np.ndarray | None:
        """
        Avança um estado na pilha de histórico (Refazer).
        
        Retorna:
            np.ndarray | None: A próxima imagem na pilha ou None se o índice já estiver no topo.
        """
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_image = self.history[self.history_index].copy()
            return self.current_image
        return None

    def reset(self) -> np.ndarray | None:
        """
        Restaura a imagem ao seu estado original carregado inicialmente do disco.
        
        Retorna:
            np.ndarray | None: A imagem original restaurada e registrada no histórico, ou None se indisponível.
        """
        if self.original_image is not None:
            self.update_current_image(self.original_image)
            return self.current_image
        return None
