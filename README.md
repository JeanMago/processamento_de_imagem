# PDI PhotoPro - Editor de Imagens Avançado

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blueviolet.svg)
![License](https://img.shields.io/badge/license-MIT-important.svg)

O **PDI PhotoPro** é uma aplicação desktop de nível profissional para Processamento Digital de Imagens (PDI), inspirada no fluxo de trabalho do Adobe Photoshop. Desenvolvido com Python, OpenCV e CustomTkinter, oferece um ambiente robusto para aplicação de filtros espaciais, transformações ponto a ponto e análise de cores através de uma interface "Studio" moderna e intuitiva.

---

## 🎨 Interface Profissional (Estilo Photoshop)

- **Painel de Propriedades Intuitivo:** Todos os ajustes (Brilho, Contraste, Limiar) e Filtros são agrupados em cartões de alta fidelidade com feedback numérico em tempo real.
- **Componentes de UI Modernos:** Utiliza botões segmentados para seleção de modo e sliders dinâmicos.
- **Suporte HighDPI:** A renderização nativa usando `ctk.CTkImage` garante visuais nítidos em monitores 4K e telas com escala.
- **Espaço de Trabalho Interativo:** Zoom em tempo real (roda do mouse), rastreamento de coordenadas e uma barra de ações rápidas para operações de Desfazer/Refazer/Reset.

---

## 🚀 Principais Recursos

### 1. Filtragem Espacial (FILTERS)
- **Desfoque Gaussiano:** Suavização de alta qualidade com intensidade de kernel ajustável.
- **Filtro de Mediana:** Remoção eficaz de ruído do tipo "sal e pimenta".
- **Detecção de Bordas:**
    - **Sobel:** Modos Horizontal, Vertical e Combinado via controles segmentados modernos.
    - **Laplacian:** Realce refinado de bordas.

### 2. Transformações de Ponto (ADJUST)
- **Brilho & Contraste:** Ajuste linear contínuo com pré-visualização ao vivo.
- **Binarização (Thresholding):** Ferramenta de segmentação com controle preciso do limiar (0-255).
- **Presets de Cor:** Conversão para Tons de Cinza com um clique, Inversão de Cores (Negativo) e Equalização Global de Histograma.

### 3. Isolação de Cores (COLOR)
- **Seleção Direcionada:** Isole matizes específicos (**Vermelho, Verde, Azul, Amarelo, Ciano, Magenta**) enquanto converte o restante da imagem para tons de cinza. Ideal para análises técnicas e efeitos artísticos.

### 4. Fluxo de Trabalho Avançado (HISTORY)
- **Sistema de Desfazer/Refazer:** Navegue para frente e para trás no seu histórico de edição (até 20 passos).
- **Histograma RGB:** Sincronização em tempo real dos dados de frequência de cores.
- **Galeria de Ativos/Camadas:** Acesso rápido a imagens de amostra predefinidas para testes.

---

## 💻 Instalação

### Pré-requisitos
- Python 3.8 ou superior.
- `pip` (gerenciador de pacotes do Python).

### Passos
1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/pdi-photopro.git
   cd pdi-photopro
   ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Ou instale manualmente: `pip install opencv-python numpy customtkinter pillow`)*

3. **Execute a aplicação:**
   ```bash
   python main.py
   ```

---

## 📂 Estrutura do Projeto

```text
projeto/
├── images/             # Banco de imagens de exemplo
├── src/
│   ├── filters/        # Algoritmos de PDI: Suavização e Bordas
│   ├── transformations/# Algoritmos de PDI: Ponto a ponto e Cores
│   ├── gui/            # Visão Moderna: Lógica da App CustomTkinter
│   ├── services/       # Controller: Gerenciamento de estado e I/O
│   └── utils/          # Auxiliares: Conversões e Redimensionamento
├── tests/              # Testes unitários para validação de algoritmos
├── main.py             # Ponto de entrada
└── requirements.txt    # Dependências do projeto
```

---

## 🛠️ Desenvolvido Com

- **[OpenCV](https://opencv.org/):** O motor principal para processamento de imagem de alto desempenho.
- **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter):** Um wrapper moderno para Tkinter com modo escuro e widgets profissionais.
- **[NumPy](https://numpy.org/):** Manipulação eficiente de matrizes para dados de imagem.
- **[Pillow (PIL)](https://python-pillow.org/):** Carregamento de imagens e integração com a GUI.

---
