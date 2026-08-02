import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Optional
from app.llm_client import OllamaClient


class ChatApp(tk.Tk):
    """
    Interfaz gráfica principal en Tkinter para el Chat Client de Ollama.
    Implementa alta cohesión delegando la comunicación HTTP a OllamaClient
    y utilizando hilos para no congelar la UI.
    """

    AVAILABLE_MODELS = ("gemma2:2b", "llama3.2:3b", "llama3.1:8b")

    def __init__(self, client: Optional[OllamaClient] = None):
        super().__init__()

        self.title("Cliente de Chat Ollama - LLM local")
        self.geometry("800x650")
        self.minsize(600, 450)

        # Inyección de dependencia del cliente LLM
        self.client = client if client else OllamaClient()

        # Configuración de estilos visuales
        self._setup_styles()

        # Construcción de componentes UI
        self._create_widgets()

        # Configuración de atajos e hilos
        self.is_processing = False

    def _setup_styles(self):
        """Configura los temas y estilos de ttk para una apariencia moderna."""
        style = ttk.Style(self)
        style.theme_use("clam")

        # Configurar colores de la interfaz
        bg_color = "#f4f6f9"
        self.configure(bg=bg_color)

        style.configure("TFrame", background=bg_color)
        style.configure("Header.TFrame", background="#ffffff", relief="flat")
        style.configure("TLabel", background=bg_color, font=("Segoe UI", 10))
        style.configure("HeaderLabel.TLabel", background="#ffffff", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", font=("Segoe UI", 9, "bold"), padding=6)
        style.configure("Send.TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("Clear.TButton", font=("Segoe UI", 9), padding=5)

    def _create_widgets(self):
        """Crea y organiza todos los elementos visuales de la interfaz."""

        # -------------------------------------------------------------
        # 1. BARRA SUPERIOR (HEADER): Selección de Modelo y Acciones
        # -------------------------------------------------------------
        header_frame = ttk.Frame(self, style="Header.TFrame", padding=(15, 10))
        header_frame.pack(fill=tk.X, side=tk.TOP)

        model_label = ttk.Label(header_frame, text="Modelo LLM:", style="HeaderLabel.TLabel")
        model_label.pack(side=tk.LEFT, padx=(0, 10))

        self.model_var = tk.StringVar(value=self.AVAILABLE_MODELS[0])
        self.model_combo = ttk.Combobox(
            header_frame,
            textvariable=self.model_var,
            values=self.AVAILABLE_MODELS,
            state="readonly",
            font=("Segoe UI", 10),
            width=18
        )
        self.model_combo.pack(side=tk.LEFT, padx=(0, 20))

        # Botón para limpiar historial
        clear_btn = ttk.Button(
            header_frame,
            text="🗑️ Limpiar Historial",
            style="Clear.TButton",
            command=self._clear_chat_history
        )
        clear_btn.pack(side=tk.RIGHT)

        # -------------------------------------------------------------
        # 2. ÁREA PRINCIPAL: Historial de Chat con Scroll
        # -------------------------------------------------------------
        chat_frame = ttk.Frame(self, padding=(15, 10))
        chat_frame.pack(fill=tk.BOTH, expand=True)

        self.chat_history = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#2c3e50",
            relief="solid",
            borderwidth=1,
            padx=12,
            pady=12
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True)

        # Configurar tags estilizadas para dar formato a los mensajes
        self.chat_history.tag_configure("user_header", font=("Segoe UI", 10, "bold"), foreground="#1a73e8")
        self.chat_history.tag_configure("user_msg", font=("Segoe UI", 10), foreground="#202124")
        self.chat_history.tag_configure("assistant_header", font=("Segoe UI", 10, "bold"), foreground="#0f9d58")
        self.chat_history.tag_configure("assistant_msg", font=("Segoe UI", 10), foreground="#202124")
        self.chat_history.tag_configure("time_badge", font=("Segoe UI", 9, "italic"), foreground="#5f6368")
        self.chat_history.tag_configure("error_msg", font=("Segoe UI", 10, "bold"), foreground="#d93025")
        self.chat_history.tag_configure("system_msg", font=("Segoe UI", 9, "italic"), foreground="#70757a")

        # Iniciar como de solo lectura
        self.chat_history.config(state=tk.DISABLED)

        # Mensaje de bienvenida inicial
        self._append_system_message("Bienvenido al Chat con Ollama. Selecciona un modelo y envía tu mensaje.\n"
                                     "Nota: Asegúrate de tener Ollama corriendo y los modelos descargados (ollama pull <modelo>).\n" + ("─" * 70) + "\n")

        # -------------------------------------------------------------
        # 3. BARRA DE ESTADO
        # -------------------------------------------------------------
        self.status_var = tk.StringVar(value="⚪ Listo para enviar mensajes.")
        status_bar = ttk.Label(
            self,
            textvariable=self.status_var,
            font=("Segoe UI", 9, "italic"),
            anchor=tk.W,
            padding=(15, 2)
        )
        status_bar.pack(fill=tk.X)

        # -------------------------------------------------------------
        # 4. ÁREA INFERIOR: Entrada de Texto y Botón Enviar
        # -------------------------------------------------------------
        input_frame = ttk.Frame(self, padding=(15, 10))
        input_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.input_text = tk.Text(
            input_frame,
            height=3,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            relief="solid",
            borderwidth=1,
            padx=8,
            pady=8
        )
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Atajos de teclado: Enter para enviar, Shift+Enter para nueva línea
        self.input_text.bind("<Return>", self._on_enter_pressed)
        self.input_text.bind("<Shift-Return>", self._on_shift_enter_pressed)

        self.send_button = ttk.Button(
            input_frame,
            text="Enviar 🚀",
            style="Send.TButton",
            command=self._send_message
        )
        self.send_button.pack(side=tk.RIGHT, fill=tk.Y)

    def _on_enter_pressed(self, event):
        """Maneja la tecla Enter para enviar el mensaje."""
        if not event.state & 0x0001:  # Si no está presionado Shift
            self._send_message()
            return "break"  # Evita que se inserte el salto de línea por defecto

    def _on_shift_enter_pressed(self, event):
        """Maneja Shift+Enter para permitir multilínea."""
        return None  # Permite la inserción normal del salto de línea

    def _send_message(self):
        """Obtiene el texto del usuario e inicia el procesamiento asíncrono."""
        if self.is_processing:
            return

        prompt = self.input_text.get("1.0", tk.END).strip()
        if not prompt:
            return

        selected_model = self.model_var.get()

        # Limpiar entrada y mostrar mensaje del usuario en el historial
        self.input_text.delete("1.0", tk.END)
        self._append_user_message(prompt)

        # Deshabilitar interfaz mientras se genera la respuesta
        self.is_processing = True
        self.send_button.config(state=tk.DISABLED)
        self.model_combo.config(state=tk.DISABLED)
        self.status_var.set(f"⏳ Generando respuesta con '{selected_model}'... Por favor espera.")

        # Ejecución asíncrona mediante hilo secundario para no congelar la UI
        thread = threading.Thread(
            target=self._async_fetch_response,
            args=(selected_model, prompt),
            daemon=True
        )
        thread.start()

    def _async_fetch_response(self, model: str, prompt: str):
        """
        Ejecuta la llamada a la API en un hilo en segundo plano.
        """
        result = self.client.generate(model=model, prompt=prompt)
        # Notificar al hilo principal de Tkinter para actualizar la UI de manera segura
        self.after(0, self._on_response_received, model, result)

    def _on_response_received(self, model: str, result: dict):
        """
        Callback ejecutado en el hilo principal de Tkinter al recibir la respuesta.
        """
        if result["success"]:
            self._append_assistant_message(
                model=model,
                response=result["response"],
                elapsed_time=result["elapsed_time"]
            )
            self.status_var.set(f"✅ Respuesta recibida en {result['elapsed_time']}s.")
        else:
            self._append_error_message(f"Error ({result['elapsed_time']}s): {result['error']}")
            self.status_var.set("❌ Ocurrió un error al consultar Ollama.")

        # Reestablecer estado de la UI
        self.is_processing = False
        self.send_button.config(state=tk.NORMAL)
        self.model_combo.config(state="readonly")

    def _clear_chat_history(self):
        """Limpia el área de texto del historial de chat."""
        if messagebox.askyesno("Limpiar historial", "¿Deseas borrar todo el historial de la conversación?"):
            self.chat_history.config(state=tk.NORMAL)
            self.chat_history.delete("1.0", tk.END)
            self.chat_history.config(state=tk.DISABLED)
            self._append_system_message("Historial limpiado correctamente.\n" + ("─" * 70) + "\n")
            self.status_var.set("⚪ Historial borrado.")

    def _append_user_message(self, message: str):
        """Agrega un mensaje del usuario al historial."""
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, "👤 Tú:\n", "user_header")
        self.chat_history.insert(tk.END, f"{message}\n\n", "user_msg")
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.see(tk.END)

    def _append_assistant_message(self, model: str, response: str, elapsed_time: float):
        """Agrega la respuesta del asistente con el tiempo transcurrido."""
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, f"🤖 Asistente ({model}) ", "assistant_header")
        self.chat_history.insert(tk.END, f"⏱️ [{elapsed_time:.2f}s]\n", "time_badge")
        self.chat_history.insert(tk.END, f"{response}\n\n", "assistant_msg")
        self.chat_history.insert(tk.END, ("─" * 70) + "\n\n", "system_msg")
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.see(tk.END)

    def _append_error_message(self, error_text: str):
        """Agrega un mensaje de error al historial."""
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, f"⚠️ {error_text}\n\n", "error_msg")
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.see(tk.END)

    def _append_system_message(self, sys_text: str):
        """Agrega un mensaje del sistema al historial."""
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, f"{sys_text}\n", "system_msg")
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.see(tk.END)
