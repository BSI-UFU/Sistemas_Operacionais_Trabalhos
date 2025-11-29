

---

# 🖥️ Simulador de Escalonamento de Processos — Documentação do Código

Este projeto implementa um **simulador gráfico de algoritmos de escalonamento de processos**, utilizando **Tkinter**, **ttkbootstrap** para estilização moderna e **Matplotlib** para geração de diagramas de Gantt.

O simulador permite **cadastrar processos**, escolher entre diferentes algoritmos de escalonamento, **visualizar métricas finais** (tempo de espera, turnaround) e acompanhar a execução através de um **diagrama de Gantt interativo**.

---

# 📌 Estrutura Geral do Código

O código é dividido em três grandes seções:

1. **Modelo de Dados**
2. **Lógica do Escalonador**
3. **Interface Gráfica (GUI)**

Cada parte é descrita em detalhes abaixo.

---

# 1️⃣ Modelo de Dados

A classe `Processo` representa cada processo da simulação.

```python
class Processo:
    def __init__(self, nome, tempo_restante, prioridade, tempo_chegada):
        self.nome = nome
        self.tempoTotal = tempo_restante
        self.tempoRestante = tempo_restante
        self.prioridade_original = prioridade
        self.prioridade_atual = prioridade
        self.tempoChegada = tempo_chegada
        self.tempoFim = 0
```

### Propriedades principais

* **nome** – identificador do processo
* **tempoChegada** – instante em que entra no sistema
* **tempoTotal** – burst original
* **tempoRestante** – usado em algoritmos preemptivos
* **prioridade_original** – prioridade definida pelo usuário
* **prioridade_atual** – usada no envelhecimento (RR)
* **tempoFim** – usado para cálculo de métricas

---

# 2️⃣ Lógica do Escalonador

Toda a lógica dos algoritmos está encapsulada na classe:

```python
class EscalonadorLogic:
```

São implementados **três algoritmos**:

---

## 🔶 2.1 Round Robin com Prioridade e Envelhecimento

### Características:

* **Quantum configurável**
* **Processos com maior número têm maior prioridade**
* Enquanto esperam, os processos ganham prioridade (envelhecimento)
* Resolve injustiças e starvation
* Quando um processo volta para a fila, sua prioridade é **resetada** à original

### Saída:

* Lista compactada com execuções (para Gantt)
* Lista de processos concluídos com `tempoFim`

---

## 🔷 2.2 SRTF – Shortest Remaining Time First (Preemptivo)

* A cada unidade de tempo seleciona o processo com **menor tempo restante**
* Totalmente preemptivo
* Registra execução **passo a passo**
* Depois compacta para gerar o Gantt

É o único algoritmo que não usa quantum.

---

## 🔸 2.3 Prioridade Não-Preemptivo

* Sempre seleciona o processo com **maior prioridade numérica**
* Em caso de empate:

  * desempate por ordem de chegada (FIFO)
* Processo executa até terminar (não-preemptivo)

---

### Compactação de Histórico

Algoritmos preemptivos geram listas longas.
A função `_compactar_historico()` reduz em intervalos contínuos:

```python
(proc, 0), (proc,1), (proc,2)
→ (proc, 0, 3)
```

---

# 3️⃣ Interface Gráfica (GUI)

A aplicação usa:

* **Tkinter** (interface)
* **ttkbootstrap** (tema moderno)
* **Matplotlib** (diagramas)
* **Treeview** (lista de processos)
* **Combobox** (seleção de algoritmo)

Tudo está dentro da classe:

```python
class App(ttk.Window):
```

---

## 🧩 Funcionalidades da Interface

### ✔ Adicionar Processo

O usuário informa:

* Nome
* Tempo de chegada
* Duração (burst)
* Prioridade

Processo é adicionado a:

* lista interna
* tabela Treeview

### ✔ Seleção do Algoritmo

Opções:

* RR com Envelhecimento
* SRTF
* Prioridade Não-Preemptivo

Painel lateral exibe explicação do algoritmo.

### ✔ Simulação

Após clicar **SIMULAR**:

1. Chama a função correta do escalonador
2. Calcula métricas:

   * tempo de espera
   * turnaround
   * médias
3. Gera diagrama de Gantt colorido
4. Atualiza painel de resultados

---

# 📊 Geração do Gráfico de Gantt

O método `plot_gantt()`:

* Cria barras horizontais (barh)
* Gera cor única para cada processo baseada no nome
* Desenha intervalos de execução
* Ignora linhas de CPU ociosa
* Mostra duração dentro das barras

---

# 📈 Métricas Calculadas

Para cada processo:

* **Retorno (Turnaround)**

  ```
  tempoFim – tempoChegada
  ```

* **Espera**

  ```
  Turnaround – Burst
  ```

Também calcula:

* Média de espera
* Média de turnaround

---

# ▶️ Execução da Aplicação

```python
if __name__ == "__main__":
    app = App()
    app.mainloop()
```

---

# 🧾 Resumo Final

Este código implementa:

* Um **simulador completo** de escalonamento
* Três algoritmos clássicos (RR com Aging, SRTF, Prioridade NP)
* Interface moderna e intuitiva
* Exportação visual via Gantt
* Cálculo completo de métricas de desempenho
* Representação gráfica e tabular dos resultados

Ideal para:

* Estudos de Sistemas Operacionais
* Visualização de comportamento de algoritmos de CPU
* Aulas e apresentações
* Análise de desempenho entre políticas de escalonamento
* Extensões para novos algoritmos (FCFS, EDF, MLFQ, entre outors.)

---

