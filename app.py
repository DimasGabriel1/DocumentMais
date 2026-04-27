import customtkinter as ctk
from PIL import Image
import motor
import threading
import sys
import io

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class ConsoleRedirect(io.StringIO):
    def __init__(self, textbox):
        super().__init__()
        self.textbox = textbox

    def write(self, text):
        self.textbox.insert("end", text)
        self.textbox.see("end")

    def flush(self):
        pass


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        # CONFIG PADRÃO
        self.num_prints = ctk.IntVar(value=4)
        self.tempo = ctk.IntVar(value=10)
        self.tempo_inatividade = ctk.IntVar(value=10)
        self.tempo_scroll = ctk.DoubleVar(value=3)

        self.title("Document +")

        # RESPONSIVIDADE
        largura_tela = self.winfo_screenwidth()
        altura_tela = self.winfo_screenheight()
        altura_util = altura_tela - 80

        if altura_tela <= 768:
            largura_janela = int(largura_tela * 0.75)
            altura_janela = int(altura_util * 0.95)
        else:
            largura_janela = int(largura_tela * 0.6)
            altura_janela = int(altura_util * 0.85)

        altura_janela = min(altura_janela, 750)

        pos_x = int((largura_tela - largura_janela) / 2)
        pos_y = int((altura_util - altura_janela) / 2)

        self.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

        self.minsize(800, 600)
        self.resizable(True, True)

        # ÍCONE DA JANELA
        try:
            self.iconbitmap("logo.ico")
        except:
            pass

        # SCROLL PRINCIPAL
        scroll_frame = ctk.CTkScrollableFrame(self, corner_radius=0)
        scroll_frame.pack(fill="both", expand=True)

        frame = scroll_frame

        # TÍTULO
        titulo = ctk.CTkLabel(
            frame,
            text="Prestação de Contas",
            font=("Segoe UI", 24, "bold")
        )
        titulo.pack(pady=(10, 20))

        # LINKS
        ctk.CTkLabel(frame, text="Site Desktop").pack()
        self.desktop = ctk.CTkEntry(frame, width=600)
        self.desktop.pack(pady=5)

        ctk.CTkLabel(frame, text="Site Mobile").pack()
        self.mobile = ctk.CTkEntry(frame, width=600)
        self.mobile.pack(pady=5)

        ctk.CTkLabel(frame, text="Site Híbrido").pack()
        self.hibrido = ctk.CTkEntry(frame, width=600)
        self.hibrido.pack(pady=(5, 15))

        # SWITCH PRESTAÇÃO
        self.prestacao = ctk.CTkSwitch(
            frame,
            text="Incluir CAPA, GAM e Assinatura"
        )
        self.prestacao.pack(pady=10)

        # DADOS
        ctk.CTkLabel(frame, text="Cliente").pack()
        self.cliente = ctk.CTkEntry(frame, width=400)
        self.cliente.pack(pady=3)

        ctk.CTkLabel(frame, text="CNPJ").pack()
        self.cnpj = ctk.CTkEntry(frame, width=400)
        self.cnpj.pack(pady=3)

        ctk.CTkLabel(frame, text="PI").pack()
        self.pi = ctk.CTkEntry(frame, width=400)
        self.pi.pack(pady=3)

        ctk.CTkLabel(frame, text="Campanha").pack()
        self.campanha = ctk.CTkEntry(frame, width=400)
        self.campanha.pack(pady=3)

        ctk.CTkLabel(frame, text="Período de Veiculação").pack()
        self.periodo = ctk.CTkEntry(frame, width=400)
        self.periodo.pack(pady=(3, 15))

        # BOTÃO CONFIGURAÇÃO
        self.btn_config = ctk.CTkButton(
            frame,
            text="⚙️ Configurações",
            width=200,
            command=self.abrir_config
        )
        self.btn_config.pack(pady=5)

        # BOTÃO GERAR
        self.botao = ctk.CTkButton(
            frame,
            text="GERAR",
            height=45,
            width=200,
            command=self.iniciar_execucao
        )
        self.botao.pack(pady=10)

        # CONSOLE
        ctk.CTkLabel(frame, text="Status da Execução").pack()

        self.console = ctk.CTkTextbox(
            frame,
            font=("Consolas", 12)
        )
        self.console.pack(pady=10, fill="both", expand=True)

        sys.stdout = ConsoleRedirect(self.console)

    # ABRIR CONFIGURAÇÕES
    def abrir_config(self):
        win = ctk.CTkToplevel(self)
        win.title("Configurações")
        win.geometry("300x300")

        try:
            win.iconbitmap("logo.ico")
        except:
            pass

        win.transient(self)
        win.attributes('-topmost', True)

        ctk.CTkLabel(win, text="Número de Prints").pack(pady=5)
        ctk.CTkEntry(win, textvariable=self.num_prints).pack(pady=(0, 5))

        ctk.CTkLabel(win, text="Tempo (espera inicial)").pack(pady=5)
        ctk.CTkEntry(win, textvariable=self.tempo).pack(pady=(0, 5))

        ctk.CTkLabel(win, text="Tempo Inatividade").pack(pady=5)
        ctk.CTkEntry(win, textvariable=self.tempo_inatividade).pack(pady=(0, 5))

        ctk.CTkLabel(win, text="Tempo Espera Scroll").pack(pady=5)
        ctk.CTkEntry(win, textvariable=self.tempo_scroll).pack(pady=(0, 5))

    # INICIAR EXECUÇÃO
    def iniciar_execucao(self):
        thread = threading.Thread(target=self.gerar)
        thread.start()

    # GERAR
    def gerar(self):
        self.console.delete("1.0", "end")

        dados = {
            "cliente": self.cliente.get(),
            "cnpj": self.cnpj.get(),
            "pi": self.pi.get(),
            "campanha": self.campanha.get(),
            "periodo": self.periodo.get()
        }

        prestacao = self.prestacao.get() == 1

        motor.NUM_PRINTS = int(self.num_prints.get())
        motor.Tempo = int(self.tempo.get())
        motor.TEMPO_INATIVIDADE = int(self.tempo_inatividade.get())
        motor.TEMPO_ESPERA_SCROLL = float(self.tempo_scroll.get())

        motor.executar(
            link_desktop=self.desktop.get(),
            link_mobile=self.mobile.get(),
            link_hibrido=self.hibrido.get(),
            prestacao=prestacao,
            dados_capa=dados
        )


if __name__ == "__main__":
    app = App()
    app.mainloop()