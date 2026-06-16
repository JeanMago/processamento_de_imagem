import sys
import os

# Add src to path if needed
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.gui.app import ImageApp

def main():
    try:
        app = ImageApp()
        app.mainloop()
    except Exception as e:
        print(f"Ocorreu um erro ao iniciar a aplicação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
