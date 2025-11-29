import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import copy

# -------------------------------------------------------
# MODELO DE DADOS
# -------------------------------------------------------
class Processo:
    def __init__(self, nome, tempo_restante, prioridade, tempo_chegada):
        self.nome = nome
        self.tempoTotal = tempo_restante  # Burst original
        self.tempoRestante = tempo_restante
        self.prioridade_original = prioridade
        self.prioridade_atual = prioridade # Usado no RR com Envelhecimento
        self.tempoChegada = tempo_chegada
        self.tempoFim = 0

    def __repr__(self):
        return f"{self.nome}(Prio:{self.prioridade_original}, Cheg:{self.tempoChegada})"

# -------------------------------------------------------
# LÓGICA DO ESCALONADOR
# -------------------------------------------------------
class EscalonadorLogic:
    
    # --- 1. ROUND ROBIN COM PRIORIDADE E ENVELHECIMENTO ---
    # (Mantém: Maior número = Maior prioridade)
    def run_rr_aging(self, lista_processos, quantum=2):
        filaEntrada = sorted(copy.deepcopy(lista_processos), key=lambda x: x.tempoChegada)
        filaProntos = []
        processos_concluidos = []
        historico_execucao = [] 
        
        tempoAtual = 0
        
        # Carrega quem já chegou no t=0
        while filaEntrada and filaEntrada[0].tempoChegada <= tempoAtual:
            p = filaEntrada.pop(0)
            espera = tempoAtual - p.tempoChegada
            p.prioridade_atual += espera 
            filaProntos.append(p)

        while filaEntrada or filaProntos:
            if not filaProntos:
                if filaEntrada:
                    tempo_salto = filaEntrada[0].tempoChegada
                    historico_execucao.append(("Ocioso", tempoAtual, tempo_salto)) 
                    tempoAtual = tempo_salto
                    while filaEntrada and filaEntrada[0].tempoChegada <= tempoAtual:
                        p = filaEntrada.pop(0)
                        p.prioridade_atual += (tempoAtual - p.tempoChegada)
                        filaProntos.append(p)
                    continue
                else:
                    break

            # Lógica RR original: Maior Valor = Maior Prioridade
            melhor_idx = 0
            for i in range(1, len(filaProntos)):
                if filaProntos[i].prioridade_atual > filaProntos[melhor_idx].prioridade_atual:
                    melhor_idx = i
            
            atual = filaProntos.pop(melhor_idx) 
            tempo_inicio = tempoAtual
            
            tempo_execucao = min(quantum, atual.tempoRestante)
            processos_em_espera = filaProntos 

            atual.tempoRestante -= tempo_execucao
            tempoAtual += tempo_execucao

            for p in processos_em_espera:
                p.prioridade_atual += tempo_execucao
            
            while filaEntrada and filaEntrada[0].tempoChegada <= tempoAtual:
                novo_proc = filaEntrada.pop(0)
                novo_proc.prioridade_atual += (tempoAtual - novo_proc.tempoChegada)
                filaProntos.append(novo_proc)

            historico_execucao.append((atual.nome, tempo_inicio, tempoAtual))

            if atual.tempoRestante > 0:
                atual.prioridade_atual = atual.prioridade_original
                filaProntos.append(atual)
            else:
                atual.tempoFim = tempoAtual
                processos_concluidos.append(atual)
        
        return historico_execucao, processos_concluidos

    # --- 2. SRTF (SHORTEST REMAINING TIME FIRST) - PREEMPTIVO ---
    def run_srtf(self, lista_processos, quantum=None):
        processos = copy.deepcopy(lista_processos)
        n = len(processos)
        processos_concluidos = []
        historico_bruto = [] 
        
        tempo = 0
        completos = 0
        
        while completos < n:
            candidatos = [p for p in processos if p.tempoChegada <= tempo and p.tempoRestante > 0]
            
            if not candidatos:
                historico_bruto.append(("Ocioso", tempo))
                tempo += 1
                continue
            
            # Escolhe menor tempo restante
            maisCurto = min(candidatos, key=lambda p: p.tempoRestante)
            
            maisCurto.tempoRestante -= 1
            historico_bruto.append((maisCurto.nome, tempo))
            tempo += 1
            
            if maisCurto.tempoRestante == 0:
                completos += 1
                maisCurto.tempoFim = tempo
                processos_concluidos.append(maisCurto)
        
        return self._compactar_historico(historico_bruto), processos_concluidos

    # --- 3. PRIORIDADE (NÃO PREEMPTIVO) - ATUALIZADO ---
    # AGORA: MAIOR NÚMERO = MAIOR PRIORIDADE
    def run_priority_np(self, lista_processos, quantum=None):
        fila_entrada = sorted(copy.deepcopy(lista_processos), key=lambda x: x.tempoChegada)
        fila_prontos = [] 
        processos_concluidos = []
        historico_execucao = []
        
        tempo_atual = 0
        total_processos = len(fila_entrada)
        
        while len(processos_concluidos) < total_processos:
            
            # 1. Carrega quem chegou
            idx = 0
            while idx < len(fila_entrada):
                if fila_entrada[idx].tempoChegada <= tempo_atual:
                    fila_prontos.append(fila_entrada.pop(idx))
                else:
                    break
            
            # 2. Ociosidade
            if not fila_prontos:
                if fila_entrada:
                    proximo_chegada = fila_entrada[0].tempoChegada
                    historico_execucao.append(("Ocioso", tempo_atual, proximo_chegada))
                    tempo_atual = proximo_chegada
                    continue
                else:
                    break 
            
            # 3. SELEÇÃO (MODIFICADA): MAIOR PRIORIDADE PRIMEIRO
            # Usamos -p.prioridade_original para que os maiores números fiquem "menores" na ordenação padrão
            # Ex: Prio 10 vira -10, Prio 2 vira -2. O -10 vem antes.
            # O tempoChegada continua positivo para manter FIFO no desempate.
            fila_prontos.sort(key=lambda p: (-p.prioridade_original, p.tempoChegada))
            
            escolhido = fila_prontos.pop(0)
            
            # 4. Execução
            inicio = tempo_atual
            duracao = escolhido.tempoTotal
            fim = inicio + duracao
            
            escolhido.tempoFim = fim
            historico_execucao.append((escolhido.nome, inicio, fim))
            tempo_atual = fim
            
            processos_concluidos.append(escolhido)
            
        return historico_execucao, processos_concluidos

    def _compactar_historico(self, historico_bruto):
        if not historico_bruto: return []
        compactado = []
        atual_nome, inicio_tempo = historico_bruto[0]
        curr_time = inicio_tempo
        
        for i in range(1, len(historico_bruto)):
            nome, t = historico_bruto[i]
            if nome != atual_nome or t != curr_time + 1:
                compactado.append((atual_nome, inicio_tempo, curr_time + 1))
                atual_nome = nome
                inicio_tempo = t
            curr_time = t
        compactado.append((atual_nome, inicio_tempo, curr_time + 1))
        return compactado

# -------------------------------------------------------
# INTERFACE GRÁFICA
# -------------------------------------------------------
class App(ttk.Window):
    def __init__(self):
        super().__init__(themename="flatly")
        self.title("Simulador de Escalonamento de Processos")
        self.geometry("1150x850")
        
        self.logic = EscalonadorLogic()
        self.lista_processos_originais = []

        self._setup_ui()

    def _setup_ui(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=BOTH, expand=YES)

        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=LEFT, fill=Y, padx=10)

        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=RIGHT, fill=BOTH, expand=YES, padx=10)

        # --- INPUTS ---
        ttk.Label(left_panel, text="Novo Processo", font=("Helvetica", 14, "bold")).pack(pady=10)
        
        ttk.Label(left_panel, text="Nome:").pack(anchor=W)
        self.entry_nome = ttk.Entry(left_panel)
        self.entry_nome.pack(fill=X, pady=2)

        ttk.Label(left_panel, text="Chegada:").pack(anchor=W)
        self.entry_chegada = ttk.Entry(left_panel)
        self.entry_chegada.pack(fill=X, pady=2)

        ttk.Label(left_panel, text="Duração (Burst):").pack(anchor=W)
        self.entry_tempo = ttk.Entry(left_panel)
        self.entry_tempo.pack(fill=X, pady=2)

        ttk.Label(left_panel, text="Prioridade:").pack(anchor=W)
        self.entry_prio = ttk.Entry(left_panel)
        self.entry_prio.pack(fill=X, pady=2)
        
        ttk.Separator(left_panel, orient=HORIZONTAL).pack(fill=X, pady=10)
        
        # Seleção de Algoritmo
        ttk.Label(left_panel, text="Algoritmo:", font=("Helvetica", 10, "bold")).pack(anchor=W)
        self.algo_var = tk.StringVar(value="RR com Envelhecimento")
        algos = ["RR com Envelhecimento", "SRTF (Preemptivo)", "Prioridade (Não-Preemptivo)"]
        self.combo_algos = ttk.Combobox(left_panel, textvariable=self.algo_var, values=algos, state="readonly")
        self.combo_algos.pack(fill=X, pady=5)
        self.combo_algos.bind("<<ComboboxSelected>>", self._on_algo_change)

        ttk.Label(left_panel, text="Quantum (apenas RR):").pack(anchor=W)
        self.entry_quantum = ttk.Entry(left_panel)
        self.entry_quantum.insert(0, "2")
        self.entry_quantum.pack(fill=X, pady=2)

        btn_add = ttk.Button(left_panel, text="Adicionar", command=self.add_processo, bootstyle=SUCCESS)
        btn_add.pack(fill=X, pady=10)

        # Tabela
        cols = ("nome", "chegada", "tempo", "prioridade")
        self.tree = ttk.Treeview(left_panel, columns=cols, show="headings", height=10)
        self.tree.heading("nome", text="Nome")
        self.tree.heading("chegada", text="Chegada")
        self.tree.heading("tempo", text="Burst")
        self.tree.heading("prioridade", text="Prio")
        
        self.tree.column("nome", width=60)
        self.tree.column("chegada", width=60, anchor=CENTER)
        self.tree.column("tempo", width=60, anchor=CENTER)
        self.tree.column("prioridade", width=70, anchor=CENTER)
        self.tree.pack(fill=BOTH, expand=YES, pady=5)

        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(fill=X, pady=5)
        ttk.Button(btn_frame, text="Limpar", command=self.limpar_tudo, bootstyle=SECONDARY).pack(side=LEFT, expand=YES, padx=2)
        ttk.Button(btn_frame, text="SIMULAR", command=self.executar_simulacao, bootstyle=PRIMARY).pack(side=LEFT, expand=YES, padx=2)

        # --- RESULTADOS ---
        self.info_frame = ttk.Labelframe(right_panel, text="Informações do Algoritmo", padding=10, bootstyle="info")
        self.info_frame.pack(fill=X, pady=5)
        self.lbl_info = ttk.Label(self.info_frame, text="Selecione um algoritmo.")
        self.lbl_info.pack(anchor=W)

        self.metrics_frame = ttk.Labelframe(right_panel, text="Relatório Final", padding=10)
        self.metrics_frame.pack(fill=X, pady=5)
        self.lbl_metricas = ttk.Label(self.metrics_frame, text="...", font=("Consolas", 9))
        self.lbl_metricas.pack(anchor=W)

        self.graph_frame = ttk.Labelframe(right_panel, text="Diagrama de Gantt", padding=10)
        self.graph_frame.pack(fill=BOTH, expand=YES, pady=5)

        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=YES)
        
        self._on_algo_change(None)

    def _on_algo_change(self, event):
        algo = self.algo_var.get()
        if "RR" in algo:
            self.lbl_info.config(text="Round Robin: Usa Quantum e Envelhecimento.\nMAIOR NÚMERO = MAIOR PRIORIDADE.")
            self.entry_quantum.config(state="normal")
        elif "SRTF" in algo:
            self.lbl_info.config(text="SRTF: Shortest Remaining Time First (Preemptivo).\nExecuta quem tem menos tempo restante.")
            self.entry_quantum.config(state="disabled")
        else:
            # ATUALIZADO AQUI
            self.lbl_info.config(text="Prioridade (Não-Preemptivo):\nMAIOR NÚMERO = MAIOR PRIORIDADE.\nOrdena a fila de prontos pela prioridade antes de executar.")
            self.entry_quantum.config(state="disabled")

    def add_processo(self):
        try:
            nome = self.entry_nome.get()
            if not nome: raise ValueError
            chegada = int(self.entry_chegada.get())
            tempo = int(self.entry_tempo.get())
            prio = int(self.entry_prio.get())
            
            p = Processo(nome, tempo, prio, chegada)
            self.lista_processos_originais.append(p)
            self.tree.insert("", "end", values=(nome, chegada, tempo, prio))
            
            self.entry_nome.delete(0, END)
            self.entry_chegada.delete(0, END)
            self.entry_tempo.delete(0, END)
            self.entry_prio.delete(0, END)
            self.entry_nome.focus()
        except ValueError:
            messagebox.showerror("Erro", "Dados inválidos.")

    def limpar_tudo(self):
        self.lista_processos_originais = []
        self.tree.delete(*self.tree.get_children())
        self.ax.clear()
        self.canvas.draw()
        self.lbl_metricas.config(text="...")

    def executar_simulacao(self):
        if not self.lista_processos_originais: return
        
        algo = self.algo_var.get()
        historico = []
        concluidos = []
        
        if "RR" in algo:
            try: q = int(self.entry_quantum.get())
            except: q = 2
            historico, concluidos = self.logic.run_rr_aging(self.lista_processos_originais, quantum=q)
        elif "SRTF" in algo:
            historico, concluidos = self.logic.run_srtf(self.lista_processos_originais)
        else:
            historico, concluidos = self.logic.run_priority_np(self.lista_processos_originais)
        
        if concluidos:
            self._mostrar_metricas(concluidos)
        
        self.plot_gantt(historico)

    def _mostrar_metricas(self, concluidos):
        soma_esp = 0; soma_ret = 0; detalhes = ""
        concluidos.sort(key=lambda x: x.nome) 
        
        detalhes += f"{'Processo':<10} | {'Chegada':<8} | {'Burst':<6} | {'Fim':<6} | {'Retorno':<8} | {'Espera':<6}\n"
        detalhes += "-"*65 + "\n"
        
        for p in concluidos:
            retorno = p.tempoFim - p.tempoChegada
            espera = retorno - p.tempoTotal
            soma_esp += espera
            soma_ret += retorno
            detalhes += f"{p.nome:<10} | {p.tempoChegada:<8} | {p.tempoTotal:<6} | {p.tempoFim:<6} | {retorno:<8} | {espera:<6}\n"
        
        media_esp = soma_esp/len(concluidos)
        media_ret = soma_ret/len(concluidos)
        
        resumo = f"Média Espera: {media_esp:.2f} | Média Turnaround (Retorno): {media_ret:.2f}\n\n{detalhes}"
        self.lbl_metricas.config(text=resumo)

    def plot_gantt(self, historico):
        self.ax.clear()
        self.ax.set_xlabel('Tempo (u.t.)')
        self.ax.set_ylabel('Processos')
        self.ax.grid(True, axis='x', linestyle='--', alpha=0.5)

        processos_reais = sorted(list(set([h[0] for h in historico if h[0] != "Ocioso"])))
        self.ax.set_yticks(range(len(processos_reais)))
        self.ax.set_yticklabels(processos_reais)
        
        tempo_max = historico[-1][2] if historico else 0
        self.ax.set_xlim(0, max(tempo_max, 1) + 1)
        
        cores = {}
        for nome in processos_reais:
            random.seed(sum(ord(c) for c in nome))
            cores[nome] = (random.random(), random.random(), random.random())
        cores["Ocioso"] = (0.9, 0.9, 0.9) 

        for nome, inicio, fim in historico:
            duracao = fim - inicio
            if nome == "Ocioso": continue 
            idx = processos_reais.index(nome)
            self.ax.barh(y=idx, width=duracao, left=inicio, height=0.6, color=cores[nome], edgecolor='black')
            if duracao >= 0.5:
                self.ax.text(inicio + duracao/2, idx, str(duracao), ha='center', va='center', color='white', fontsize=8, fontweight='bold')

        self.canvas.draw()

if __name__ == "__main__":
    app = App()
    app.mainloop()