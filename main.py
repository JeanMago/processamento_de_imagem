import sys
import os

# Adiciona o diretório 'src' ao PATH de busca do Python para permitir importações absolutas 
# dos módulos internos (gui, transformations, filters, services, utils) de qualquer ponto.
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.gui.app import ImageApp

def main():
    """
    Ponto de entrada principal da aplicação PhotoPro PDI.
    
    Instancia o loop de eventos principal da interface gráfica CustomTkinter (ImageApp)
    e fornece uma estrutura de captura de exceções de nível superior para diagnosticar falhas catastróficas 
    durante a inicialização do aplicativo.
    """
    try:
        app = ImageApp()
        app.mainloop()
    except Exception as e:
        print(f"Ocorreu um erro catastrófico ao iniciar a aplicação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
