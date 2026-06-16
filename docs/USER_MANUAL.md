# Manual do Usuário - PDI Interativo

Este manual descreve como utilizar as funcionalidades da aplicação de Processamento Digital de Imagens.

## 1. Interface Principal

A interface é dividida em quatro áreas principais:

- **Painel Esquerdo:** Seleção de imagens, carregamento de novos arquivos, botões de Desfazer/Refazer e Reset.
- **Painel Central:** Exibição da imagem original para comparação.
- **Painel Direito:** Exibição da imagem processada com os filtros aplicados.
- **Painel Inferior:** Abas de controle para Filtros, Transformações, Cores e Histograma.

## 2. Carregando Imagens

- **Galeria:** Clique em qualquer miniatura no painel esquerdo para carregar uma das imagens padrão.
- **Abrir Imagem:** Utilize o botão "Abrir Imagem..." para selecionar um arquivo do seu computador.

## 3. Aplicando Filtros e Transformações

### Filtros
Nesta aba, você pode aplicar suavização ou detecção de bordas:
- **Gaussiano e Mediana:** Arraste o slider para ajustar a intensidade e clique em "Aplicar" para fixar o efeito no histórico.
- **Laplaciano:** Clique para realçar todas as bordas.
- **Sobel:** Selecione a direção (Horizontal, Vertical ou Ambos) e clique em "Aplicar".

### Transformações
- **Brilho e Contraste:** Os ajustes são mostrados em tempo real enquanto você move os sliders. Clique em "Fixar Alterações" para salvar esse estado no histórico.
- **Binarização:** Converte a imagem para preto e branco absoluto com base no limiar.

### Cores
- **Inverter:** Cria o negativo da imagem.
- **Tons de Cinza:** Remove as cores preservando a luminosidade.
- **Equalizar:** Melhora automaticamente o contraste global.
- **Isolar Cor:** Escolha uma cor para manter; todas as outras partes da imagem ficarão em cinza.

## 4. Histórico e Salvamento

- **Desfazer/Refazer:** Utilize os botões no painel esquerdo para navegar pelas suas últimas 20 alterações.
- **Salvar:** Clique em "Salvar Imagem..." para exportar o resultado final em PNG, JPG ou outros formatos suportados.
- **Resetar:** Remove todas as alterações e volta à imagem original carregada.
