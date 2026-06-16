# Documentação do Código - PDI PhotoPro

Este documento fornece uma visão detalhada da estrutura do código, classes e funções do projeto PDI PhotoPro.

## Estrutura de Pastas

```text
src/
├── filters/         # Algoritmos de filtragem espacial
├── transformations/ # Transformações de ponto a ponto e cores
├── services/        # Lógica de negócio e gerenciamento de estado
├── gui/             # Interface gráfica (CustomTkinter)
└── utils/           # Funções utilitárias e conversões
```

---

## 1. Módulo de Filtros (`src/filters/filters.py`)

Contém funções para aplicação de filtros espaciais utilizando OpenCV.

- **`apply_gaussian_blur(image, kernel_size=5, sigma=1.0)`**:
  - Aplica o desfoque Gaussiano.
  - Garante que o `kernel_size` seja ímpar.
- **`apply_median_blur(image, kernel_size=5)`**:
  - Aplica o filtro de mediana para remoção de ruídos (tipo sal e pimenta).
- **`apply_laplacian(image, ksize=3, scale=1, delta=0)`**:
  - Aplica o operador Laplaciano para detecção de bordas.
- **`apply_sobel(image, direction='both', ksize=3)`**:
  - Aplica o operador Sobel para detecção de bordas horizontais, verticais ou ambas.

---

## 2. Módulo de Transformações (`src/transformations/transformations.py`)

Responsável por ajustes de cor, brilho e operações ponto a ponto.

- **`apply_brightness_contrast(image, brightness=0, contrast=0)`**:
  - Ajusta linearmente o brilho e o contraste da imagem.
- **`apply_binarization(image, threshold=127)`**:
  - Converte a imagem para preto e branco (binária) com base em um limiar.
- **`apply_invert_colors(image)`**:
  - Inverte as cores da imagem (negativo).
- **`apply_grayscale(image)`**:
  - Converte a imagem para tons de cinza.
- **`apply_isolate_color(image, color_name='red')`**:
  - Isola uma cor específica (Vermelho, Verde, Azul, Amarelo, Ciano, Magenta) e converte o restante em cinza.
- **`apply_histogram_equalization(image)`**:
  - Equaliza o histograma no canal Y (espaço YUV) para melhorar o contraste sem distorcer as cores.

---

## 3. Módulo de Serviços (`src/services/image_service.py`)

Contém a classe principal de gerenciamento de dados.

### Classe `ImageService`
- **Atributos**:
  - `original_image`: Cópia da imagem original carregada.
  - `current_image`: Imagem atual com as modificações aplicadas.
  - `history`: Pilha (lista) para armazenar estados anteriores (Undo/Redo).
  - `history_index`: Índice atual na pilha de histórico.
- **Métodos**:
  - `load_image(file_path)`: Carrega uma imagem do disco.
  - `save_image(file_path)`: Salva a imagem atual no disco.
  - `update_current_image(new_image, add_to_history=True)`: Atualiza a imagem de trabalho e gerencia a pilha de histórico (limite de 20 passos).
  - `undo()` / `redo()`: Navega pelo histórico de modificações.
  - `reset()`: Retorna à imagem original.

---

## 4. Módulo de Utilidades (`src/utils/utils.py`)

Funções de suporte para conversão de formatos e análise.

- **`cv2_to_pil(image)`**: Converte matrizes BGR do OpenCV para o formato RGB do PIL.
- **`pil_to_tk(pil_image)`**: Converte imagem PIL em um objeto compatível com o Tkinter (`PhotoImage`).
- **`calculate_histogram(image)`**: Calcula a distribuição de frequências de cores (R, G, B) para exibição gráfica.
- **`resize_to_fit(image, max_width, max_height)`**: Redimensiona a imagem para caber na tela mantendo a proporção original.

---

## 5. Interface Gráfica (`src/gui/app.py`)

Implementa a interface do usuário para interação com os algoritmos de PDI.

### Classe `ImageApp` (Herda de `ctk.CTk`)
- **Principais Componentes**:
  - `setup_ui_skeleton()`: Cria a estrutura de barras de menu, status e áreas principais.
  - `setup_properties_panel()`: Configura o painel lateral com abas (ADJUST, FILTERS, COLOR, HISTORY).
  - `setup_canvas_area()`: Configura a área central de visualização (Original vs. Processada).
- **Gerenciamento de Eventos**:
  - Manipula sliders, botões e atalhos de mouse (zoom).
  - Realiza atualizações em "tempo real" (live preview) antes de confirmar as alterações no histórico.
