# Guia de Instalação - PDI Interativo

Siga os passos abaixo para configurar o ambiente e executar a aplicação.

## Pré-requisitos

1. **Python 3.8+**: Certifique-se de ter o Python instalado em seu sistema. Você pode verificar executando `python --version`.
2. **PIP**: O gerenciador de pacotes do Python.

## Instalação das Dependências

Abra o terminal ou prompt de comando na raiz do projeto e execute:

```bash
pip install -r requirements.txt
```

Caso o arquivo `requirements.txt` não esteja disponível, instale manualmente:

```bash
pip install opencv-python numpy customtkinter pillow
```

## Execução

Para iniciar a aplicação, execute:

```bash
python main.py
```

## Solução de Problemas Comuns

- **Erro de importação 'cv2'**: Verifique se o `opencv-python` foi instalado corretamente.
- **Interface com texto cortado**: A aplicação foi otimizada para resoluções acima de 1280x720. Em telas menores, verifique a escala do sistema operacional.
- **Lentidão em imagens 4K**: O processamento em tempo real pode ser exigente. Para melhor performance, utilize imagens com resolução até Full HD (1920x1080).
