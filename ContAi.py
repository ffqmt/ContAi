import os
import subprocess
import requests
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import json
import time
import shutil
import tempfile

# Versão atual do aplicativo
CURRENT_VERSION = "1.3.1"
PREFERENCES_FILE = "preferences.json"

class CentralApp:
    @staticmethod
    def resource_path(relative_path):
        """Obtem o caminho absoluto para recursos, funciona tanto no ambiente de desenvolvimento quanto no executável."""
        try:
            # PyInstaller cria uma pasta temporária e armazena o caminho no atributo `frozen`
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def __init__(self, master):
        self.master = master
        self.master.title("Central de Aplicativos ContAi")
        self.master.geometry("300x400")
        self.master.configure(bg="#001f3f")

        # Lista de aplicativos com suas visibilidades
        self.apps = {
            "Gerador de Relatório XML": True,
            "PDF DAS - Sem movimento": True
        }

        # Carregar preferências do usuário
        self.load_preferences()

        # Criar barra de menu
        self.create_menu()

        # Carregar e redimensionar a logo
        self.logo = self.load_image(CentralApp.resource_path("imagens/LOGO IMAGEM.png"), (130, 75))
        if self.logo:
            self.logo_label = tk.Label(master, image=self.logo, bg="#001f3f")
            self.logo_label.pack(pady=10, padx=10, expand=False)

        # Frame para os botões
        self.button_frame = tk.Frame(master, bg="#001f3f")
        self.button_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Carregar ícones para os botões
        self.icon_relatorio = self.load_image(CentralApp.resource_path("imagens/nfxml.png"), (20, 20))
        self.icon_outro = self.load_image(CentralApp.resource_path("imagens/segregadas.png"), (20, 20))

        # Criar botões baseados nas preferências do usuário
        self.create_buttons()

        # Verificar atualizações ao iniciar
        self.check_for_updates()

        # Aplicar estilo neon
        self.apply_neon_style()

    def load_preferences(self):
        if os.path.exists(PREFERENCES_FILE):
            with open(PREFERENCES_FILE, "r") as f:
                self.apps = json.load(f)

    def save_preferences(self):
        with open(PREFERENCES_FILE, "w") as f:
            json.dump(self.apps, f)

    def create_menu(self):
        menubar = tk.Menu(self.master)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Sobre", command=self.show_about)
        help_menu.add_command(label="Ajuda", command=self.show_help)
        menubar.add_cascade(label="Ajuda", menu=help_menu)

        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Personalizar Aplicativos", command=self.open_customization_window)
        menubar.add_cascade(label="Personalização", menu=settings_menu)

        self.master.config(menu=menubar)

    def open_customization_window(self):
        customization_window = tk.Toplevel(self.master)
        customization_window.title("Personalização de Aplicativos")
        customization_window.geometry("300x200")
        customization_window.configure(bg="#001f3f")

        tk.Label(customization_window, text="Escolha os aplicativos a ocultar:", bg="#001f3f", fg="white").pack(pady=10)

        for app_name in self.apps.keys():
            var = tk.BooleanVar(value=self.apps[app_name])
            checkbox = tk.Checkbutton(customization_window, text=app_name, variable=var,
                                       bg="#001f3f", fg="white", selectcolor="#0056b3",
                                       command=lambda name=app_name, var=var: self.update_app_visibility(name, var.get()))
            checkbox.pack(anchor=tk.W)

        tk.Button(customization_window, text="Fechar", command=lambda: [self.save_preferences(), customization_window.destroy()],
                  bg="#0056b3", fg="white").pack(pady=10)

    def update_app_visibility(self, app_name, is_visible):
        self.apps[app_name] = is_visible
        self.update_buttons()

    def create_buttons(self):
        for app_name, is_visible in self.apps.items():
            if is_visible:
                if app_name == "Gerador de Relatório XML":
                    self.btn_relatorio_xml = tk.Button(
                        self.button_frame,
                        text=app_name,
                        command=self.open_xml_report_generator,
                        bg="#0056b3",
                        fg="white",
                        compound=tk.LEFT,
                        image=self.icon_relatorio,
                        padx=5,
                        pady=0
                    )
                    self.btn_relatorio_xml.pack(pady=5, fill=tk.X)
                elif app_name == "PDF DAS - Sem movimento":
                    self.btn_outro_app = tk.Button(
                        self.button_frame,
                        text=app_name,
                        command=self.open_other_app,
                        bg="#0056b3",
                        fg="white",
                        compound=tk.LEFT,
                        image=self.icon_outro,
                        padx=5,
                        pady=0
                    )
                    self.btn_outro_app.pack(pady=5, fill=tk.X)

    def update_buttons(self):
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        self.create_buttons()

    def show_about(self):
        about_message = (
            "Central de Aplicativos ContAi\n"
            "Desenvolvido por Franco Sistemas\n"
            "Direitos reservados a Contaudi Assessoria Contabil\n"
            "Telefone de contato: (66) 3498-1622\n"
            "Versão: " + CURRENT_VERSION
        )
        messagebox.showinfo("Sobre", about_message)

    def show_help(self):
        messagebox.showinfo("Ajuda", "Esta é a Central de Aplicativos ContAi.\nUse os botões para acessar diferentes funcionalidades.")

    def load_image(self, path, size=None):
        try:
            image = Image.open(path)
            if size:
                image = image.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar a imagem: {e}")
            return None

    def check_for_updates(self):
        try:
            response = requests.get("http://localhost:6050/version.json")
            latest_version = response.json().get("version")
            if latest_version > CURRENT_VERSION:
                self.prompt_update()
        except Exception as e:
            print(f"Erro ao verificar atualizações: {e}")

    def prompt_update(self):
        if messagebox.askyesno("Atualização Disponível", "Uma nova versão está disponível. Deseja atualizar?"):
            self.download_update("http://localhost:6050/atualizacoes/ContAi.exe")

    def download_update(self, url):
        """Baixa a nova versão do aplicativo para uma pasta temporária e inicia o processo de atualização."""
        # Criar uma janela de progresso
        progress_window = tk.Toplevel(self.master)
        progress_window.title("Atualizando...")
        progress_window.geometry("300x100")
        progress_window.configure(bg="#001f3f")

        # Criar uma barra de progresso
        progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
        progress_bar.pack(pady=20, padx=20, fill=tk.X)

        # Iniciar a barra de progresso
        progress_bar.start()

        # Caminho para a pasta temporária
        temp_dir = tempfile.gettempdir()
        new_app_path = os.path.join(temp_dir, "ContAi_new.exe")  # Novo caminho do executável

        try:
            # Faz o download da nova versão
            response = requests.get(url, stream=True)
            response.raise_for_status()

            # Salva a nova versão na pasta temporária
            total_length = int(response.headers.get('content-length', 0))
            with open(new_app_path, "wb") as f:
                for data in response.iter_content(chunk_size=4096):
                    f.write(data)
                    # Atualiza a barra de progresso
                    progress_bar['value'] += len(data) / total_length * 100
                    progress_window.update_idletasks()

            # Finaliza a barra de progresso
            progress_bar.stop()
            progress_window.destroy()

            # Fecha a aplicação atual
            self.master.destroy()  # Fecha a instância atual

            # Aguardar um momento para garantir que a aplicação fechou
            time.sleep(1)

            # Caminho do executável original
            original_app_path = os.path.join(os.path.dirname(__file__), "ContAi.exe")

            # Mover o novo executável para substituir o antigo
            shutil.move(new_app_path, original_app_path)

            # Reinicia a aplicação
            subprocess.Popen([original_app_path])

        except Exception as e:
            progress_bar.stop()
            progress_window.destroy()
            messagebox.showerror("Erro", f"Não foi possível atualizar o aplicativo: {e}")

    def close_application(self):
        """Força o fechamento do aplicativo, se necessário."""
        try:
            subprocess.call(['taskkill', '/F', '/IM', 'ContAi.exe'])
        except Exception as e:
            print(f"Erro ao tentar fechar o aplicativo: {e}")

    def is_process_running(self, process_name):
        """Verifica se o processo ainda está em execução."""
        try:
            output = subprocess.check_output('tasklist', shell=True)
            return process_name in output.decode('latin-1')
        except subprocess.CalledProcessError as e:
            print(f"Erro ao executar o comando: {e}")
            return False
        except UnicodeDecodeError as e:
            print(f"Erro ao verificar o processo: {e}")
            return False

    def open_xml_report_generator(self):
        """Abre o gerador de relatórios de XML."""
        app_path = os.path.join(CentralApp.resource_path("dist"), "Contaudi - Gerador de Relatório XML NFSE.exe")
        print(f"Caminho do aplicativo: {app_path}")
        self.open_app(app_path)

    def open_other_app(self):
        """Abre outro aplicativo."""
        app_path = os.path.join(CentralApp.resource_path("dist"), "SegregaDAS.exe")
        print(f"Caminho do aplicativo: {app_path}")
        self.open_app(app_path)

    def open_app(self, caminho):
        """Abre um aplicativo dado o caminho."""
        try:
            subprocess.Popen(caminho)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o aplicativo: {e}")

    def apply_neon_style(self):
        """Aplica estilo neon aos botões."""
        buttons = []
        if hasattr(self, 'btn_relatorio_xml'):
            buttons.append(self.btn_relatorio_xml)
        if hasattr(self, 'btn_outro_app'):
            buttons.append(self.btn_outro_app)

        for button in buttons:
            button.bind("<Enter>", lambda e, b=button: b.configure(bg="#00ffcc"))  # Cor neon ao passar o mouse
            button.bind("<Leave>", lambda e, b=button: b.configure(bg="#0056b3"))  # Retorna à cor original

if __name__ == "__main__":
    root = tk.Tk()
    app = CentralApp(root)
    root.mainloop()
