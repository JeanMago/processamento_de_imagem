# Manual Técnico - PDI Interativo

## 1. Arquitetura do Sistema

O projeto segue o padrão **MVC (Model-View-Controller)** para garantir separação de responsabilidades:

- **Model:** Implementado em `src/filters/` e `src/transformations/`. Contém a lógica matemática pura utilizando NumPy e OpenCV.
- **View:** Implementada em `src/gui/`. Utiliza CustomTkinter para renderização de widgets e Pillow para conversão de formatos de imagem.
- **Controller/Services:** `src/services/image_service.py` gerencia o estado da aplicação, histórico e operações de I/O. `main.py` orquestra a inicialização.

## 2. Processamento de Imagens

### Filtros Espaciais
- **Convolução:** Utilizada no filtro Gaussiano e Sobel. O sistema trata kernels dinamicamente com base nos inputs do usuário.
- **Ordenação de Posto:** O filtro de Mediana utiliza o método de vizinhança para remoção de ruído impulsivo.

### Transformações Lineares
- O ajuste de Brilho e Contraste utiliza a fórmula: $g(x) = \alpha \cdot f(x) + \beta$, onde $\alpha$ é o ganho (contraste) e $\beta$ o bias (brilho).
- A binarização utiliza o algoritmo de limiarização global de Otsu ou limiar fixo conforme selecionado.

## 3. Fluxo de Dados

1. O usuário dispara um evento na GUI (ex: move slider).
2. A View captura o valor e solicita uma pré-visualização ao Service ou aplica diretamente via Model.
3. O Model processa a matriz `numpy.ndarray`.
4. O resultado é convertido de BGR (OpenCV) para RGB (PIL) e então para um objeto `PhotoImage` compatível com o Tkinter.
5. O Canvas é atualizado (objetivo de desempenho: < 200ms para feedback visual).

## 4. Gestão de Memória

A aplicação mantém uma pilha (Stack) de objetos de imagem para suportar o Desfazer/Refazer. Para otimizar o uso de memória, as imagens são armazenadas como matrizes NumPy comprimidas ou com limite de profundidade de histórico (atualmente 20 passos).
