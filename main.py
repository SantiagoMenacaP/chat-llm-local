"""
Punto de entrada principal de la aplicación mi_chat_llm.
"""
from app.ui import ChatApp


def main():
    app = ChatApp()
    app.mainloop()


if __name__ == "__main__":
    main()
