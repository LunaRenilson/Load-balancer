# UNICAMP - Universidade Estadual de Campinas
## Instituto de Computação

**MC714 - Sistemas Distribuídos**  
**2º Semestre de 2026**

# Trabalho 1: Balanceador de Carga para um Sistema Distribuído

**Professor:** Carlos Alberto Astudillo Trujillo  
**Estudante de Mestrado (PED):** Diogo Maciel da Cunha  
**Data:** Campinas, Agosto de 2026

---

## 1 Instruções

O balanceamento de carga em um sistema distribuído é uma técnica fundamental para otimizar o uso de recursos e garantir eficiência. O objetivo é distribuir a carga entre pontos do sistema, evitando que alguns fiquem sobrecarregados enquanto outros permanecem subutilizados, trazendo mais escalabilidade e uma melhor alocação dos recursos. Este projeto visa a implementação e a análise de um balanceador de carga que receba requisições e seja capaz de alocá-las em sistemas computacionais distribuídos, levando em consideração políticas fundamentais, modelagem analítica e avaliação por simulação. Entregue um relatório de até 4 páginas descrevendo o processo, além do código-fonte. Este projeto deverá ser desenvolvido em dupla. A avaliação levará em consideração o relatório e o código-fonte da solução.

**Resumo**
- Implementar um balanceador de carga
- Analsar balanceador de carga
- Gerar Relatório (de até 4 páginas)

### 1.1 Trabalho a fazer

**Linguagem de programação e plataforma:**
* Escolha qualquer linguagem de programação (por exemplo, Python, Java, C++, Go).

**Políticas fundamentais de balanceamento de carga:** implemente pelo menos as seguintes três políticas:
* **Escolha Aleatória:** o balanceador de carga seleciona aleatoriamente um servidor do conjunto para cada pedido recebido.
* **Round Robin:** O balanceador de carga distribui igualmente as requisições entre os servidores de forma cíclica.
* **Fila Mais Curta:** O balanceador de carga monitora a fila de execução de todos os servidores e atribui a requisição ao servidor com a menor fila.

**Simulação de tráfego:**
* A chegada dos pacotes/requisições deve ser modelada por uma distribuição de Pareto Limitada (Bounded Pareto) com parâmetro Hurst de 0.8.
* O sistema deve ser submetido a rajadas de carga com tamanhos de 30, 60, 90 e 120 requisições. Considerem que os experimentos devem ser executados separadamente. Exemplo: uma execução com rajadas de no máximo 30 requisições, seguido de outro experimento independente com rajadas de 60 e etc.
* Cada experimento deve ter duração máxima de 200 unidades de tempo.

**Simulação de servidores:**
* Simule 3 servidores homogêneos para o atendimento das requisições.
* O tempo de processamento de cada requisição deve ser constante em 5% (0.05 unidades de tempo).
* Cada servidor possui capacidade finita de processamento simultâneo, suportando processar até 15 requisições ao mesmo tempo.
* O estado do servidor e o comprimento das filas devem ser monitorados ao longo de toda a execução.

**Execução dos experimentos e métricas:**
* Cada experimento deve ser executado 10 vezes, e as métricas reportadas devem ser a média dos 10 experimentos independentes.
* Registre o desempenho sob as diferentes condições de tráfego e políticas avaliando as métricas principais: vazão do sistema (throughput) e tempo médio de resposta (average response time).

**Modelagem Analítica e Comparação:**
* Deve ser desenvolvida uma modelagem analítica do sistema distribuído de balanceamento.
* No modelo analítico, assuma que a probabilidade de transição do balanceador para qualquer um dos 3 servidores é de $1/3$ (balanceamento justo).
* Realize uma comparação rigorosa entre os valores teóricos obtidos analiticamente e os resultados coletados através da simulação.

**Detalhes da implementação:**
* O balanceador de carga deve possuir configuração para alternar entre as três políticas implementadas.
* A implementação deve registrar logs detalhados ou apresentar na saída padrão a dinâmica de distribuição de carga.

**Documentação e Relatório:**
* Forneça instruções claras sobre como compilar e executar o seu código.
* Inclua a dedução e formulação do modelo analítico, comparando seus resultados com os gráficos/dados da simulação.
* Inclua uma descrição da divisão de trabalho entre os membros da dupla (compatível com os commits do repositório).
* Comente o seu código adequadamente.

**Instruções de Submissão:**
* Submeta o seu código-fonte num único ficheiro comprimido (.zip ou .tar.gz).
* Certifique-se de que o código execute perfeitamente em ambiente Windows ou Linux.

**Ponto extra (opcional):** Implemente políticas adicionais de balanceamento de carga, como:
* Variar o poder de processamento dos servidores, permitindo capacidades heterogêneas.
* Atribuir um servidor de backup acionado quando os buffers ficarem cheios.

### 1.2 Entregáveis
* `relatorio_projeto1_nome_de_um_integrante_do_grupo.pdf`
* `codigo_projeto1_nome_de_um_integrante_do_grupo.zip`

### 1.3 Data de entrega
A data de entrega é no dia 22 de setembro de 2026. Deverão subir os arquivos no Classroom dentro da tarefa do projeto. Apenas uma submissão por dupla é necessária.

---

## 2 Relatório

Prepare um relatório de máximo 4 páginas no formato IEEE (coluna dupla).
O relatório deve conter, pelo menos:
* Resumo.
* Descrição da arquitetura do balanceador e políticas adotadas.
* Descrição dos servidores e parametrização do tráfego (Bounded Pareto, rajadas de 30 a 120 requisições).
* Desenvolvimento da modelagem analítica (considerando probabilidade $1/3$ de transição por servidor).
* Resultados e discussão: Comparação quantitativa entre os valores analíticos e a média das 10 execuções da simulação.
* Conclusão.

---

## 3 Dicas

* Não comece o projeto dias antes da submissão. Planejem sua entrega e façam avanços oportunamente.
* É permitido utilizar bibliotecas de simulação de eventos discretos caso desejem (como SimPy em Python ou JSL em Java).

---

## 4 Avaliação

O projeto abrange a avaliação do relatório e do código-fonte. O detalhe da ponderação é apresentado na Tabela 1.

* É proibido copiar o trabalho de outra dupla. Se detectado, todos os envolvidos serão penalizados.
* **Critérios de avaliação:**
  * **Corretude:** Implementação correta das políticas, da simulação e da modelagem analítica.
  * **Validação:** Consistência na comparação entre modelo analítico e simulação.
  * **Qualidade do código:** Código modular, documentado e limpo.
  * **Documentação:** Clareza e rigor técnico no relatório de 4 páginas.

**Tabela 1: Avaliação do projeto**

| Item | % |
| :--- | :--- |
| Relatório e Modelagem Analítica | 30 |
| Geração de Tráfego e Rajadas (código e funcionalidade) | 15 |
| Implementação dos Servidores (capacidade e concorrência) | 15 |
| Implementação do Balanceador de Carga | 20 |
| Implementação e Comparação das Políticas / Simulações e Analítico | 20 |

MC714_2s2026.md
Exibindo MC714_2s2026.md.