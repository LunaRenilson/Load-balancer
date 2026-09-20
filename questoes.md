## Resolução Item a)

Seja $N(t)$ o número total de requisições que chegam ao balanceador até ao instante $t$. De acordo com o enunciado, $N(t)$ segue um processo de Poisson com taxa $\lambda$[cite: 1], o que significa que a probabilidade de ocorrerem $n$ chegadas totais é dada por:

$$ P(N(t) = n) = \frac{e^{-\lambda t}(\lambda t)^n}{n!} $$

Sob a política aleatória, cada requisição é direcionada ao servidor $i \in \{1, 2, 3\}$ com probabilidade $p_i = 1/3$, de forma estritamente independente das restantes requisições[cite: 1]. Seja $N_i(t)$ o número de requisições enviadas ao servidor $i$. O total de chegadas é a soma das chegadas em cada servidor: $N(t) = N_1(t) + N_2(t) + N_3(t)$.

Dado que ocorreram $n$ chegadas totais ($N(t) = n$), a forma como essas requisições se distribuem entre os três servidores segue uma distribuição multinomial. A probabilidade condicional de termos $n_1$ requisições no servidor 1, $n_2$ no servidor 2 e $n_3$ no servidor 3 (em que $n_1 + n_2 + n_3 = n$) é:

$$ P(N_1(t)=n_1, N_2(t)=n_2, N_3(t)=n_3 \mid N(t)=n) = \frac{n!}{n_1!n_2!n_3!} p_1^{n_1} p_2^{n_2} p_3^{n_3} $$

Para encontrar a probabilidade conjunta incondicional de $(N_1(t), N_2(t), N_3(t))$, multiplicamos a probabilidade condicional pela probabilidade de ocorrerem exatamente $n$ chegadas no processo original:

$$ P(N_1(t)=n_1, N_2(t)=n_2, N_3(t)=n_3) = P(N_1(t)=n_1, \dots \mid N(t)=n) \cdot P(N(t)=n) $$

Substituindo as expressões:

$$ P(N_1(t)=n_1, N_2(t)=n_2, N_3(t)=n_3) = \left( \frac{n!}{n_1!n_2!n_3!} p_1^{n_1} p_2^{n_2} p_3^{n_3} \right) \left( \frac{e^{-\lambda t}(\lambda t)^n}{n!} \right) $$

Podemos cancelar o termo $n!$ no numerador e no denominador. Lembrando que $n = n_1 + n_2 + n_3$ e que a exponencial pode ser reescrita como $e^{-\lambda t} = e^{-\lambda(p_1 + p_2 + p_3)t} = e^{-\lambda p_1 t} e^{-\lambda p_2 t} e^{-\lambda p_3 t}$, reorganizamos a equação como:

$$ P(N_1(t)=n_1, N_2(t)=n_2, N_3(t)=n_3) = \left( \frac{e^{-\lambda p_1 t}(\lambda p_1 t)^{n_1}}{n_1!} \right) \left( \frac{e^{-\lambda p_2 t}(\lambda p_2 t)^{n_2}}{n_2!} \right) \left( \frac{e^{-\lambda p_3 t}(\lambda p_3 t)^{n_3}}{n_3!} \right) $$

A expressão mostra que a probabilidade conjunta dos três processos fatorizou-se exatamente no produto de três distribuições de Poisson individuais. Isto demonstra as duas conclusões exigidas pelo teorema da decomposição (splitting):

1. **Independência:** Como a probabilidade conjunta é o produto exato das probabilidades marginais, os três processos (e por consequência, os três servidores) são mutuamente independentes[cite: 1].
2. **Processos de Poisson de taxa $\lambda_i$:** Cada variável $N_i(t)$ tem a forma da função de massa de probabilidade de Poisson com parâmetro $\lambda p_i t$.

Como a política de escalonamento garante que a escolha é equiprovável para os 3 servidores ($p_1 = p_2 = p_3 = 1/3$)[cite: 1], a taxa de chegada a cada servidor individual resulta em:

$$ \lambda_i = \lambda p_i = \frac{\lambda}{3} $$



## Resolução Item e) Verique a Lei de Little (E[N] = X · E[R]) nos seus dados de simulação, para as três políticas.

A **Lei de Little** é um teorema fundamental da Teoria de Filas que estabelece que, para qualquer sistema estável e conservativo em estado estacionário, o número médio de clientes/requisições no sistema ($E[N]$) é igual à taxa média de chegada/vazão efetiva ($X$) multiplicada pelo tempo médio de permanência no sistema ($E[R]$):

$$ E[N] = X \cdot E[R] $$

Uma das propriedades mais notáveis da Lei de Little é a sua **universalidade**: ela independe da distribuição de chegadas, da distribuição do tempo de serviço e da política de escalonamento/roteamento adotada (seja Aleatória, Round-Robin ou Fila Mais Curta / JSQ).

### Tabela de Verificação Empírica dos Dados de Simulação

Abaixo apresentamos os dados extraídos das simulações (`results/results.csv`) para cada política e valor de $\lambda$, comparando o produto $X \cdot E[R]$ com o valor medido de $E[N]$:

| Política | $\lambda$ | Vazão $X$ | Tempo Resposta $E[R]$ | Produto $X \cdot E[R]$ | Medido $E[N]$ | Erro Relativo (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Aleatória** | 0.6 | 0.5963 | 1.2495 | 0.74516 | 0.74539 | **0.031%** |
| | 1.2 | 1.2042 | 1.6658 | 2.00606 | 2.00614 | **0.004%** |
| | 1.8 | 1.8044 | 2.5451 | 4.59334 | 4.59406 | **0.016%** |
| | 2.4 | 2.4067 | 4.9342 | 11.87449 | 11.87660 | **0.018%** |
| | 2.7 | 2.6985 | 9.3119 | 25.13206 | 25.13860 | **0.026%** |
| **Round-Robin** | 0.6 | 0.6018 | 1.0636 | 0.64030 | 0.64055 | **0.040%** |
| | 1.2 | 1.2045 | 1.2844 | 1.54729 | 1.54763 | **0.022%** |
| | 1.8 | 1.7928 | 1.7905 | 3.21013 | 3.21119 | **0.033%** |
| | 2.4 | 2.4116 | 3.6433 | 8.78519 | 8.78735 | **0.025%** |
| | 2.7 | 2.6939 | 6.6240 | 17.86036 | 17.86093 | **0.003%** |
| **Fila Mais Curta (JSQ)** | 0.6 | 0.5935 | 1.0164 | 0.60323 | 0.60304 | **0.031%** |
| | 1.2 | 1.1997 | 1.1511 | 1.38096 | 1.38102 | **0.004%** |
| | 1.8 | 1.8050 | 1.4058 | 2.53742 | 2.53762 | **0.008%** |
| | 2.4 | 2.4204 | 2.2915 | 5.54719 | 5.54485 | **0.042%** |
| | 2.7 | 2.7010 | 3.8665 | 10.44928 | 10.44747 | **0.017%** |

Onde o erro relativo é calculado por:

$$ \text{Erro (\%)} = \frac{|E[N]_{\text{medido}} - (X \cdot E[R])|}{E[N]_{\text{medido}}} \times 100\% $$

### Conclusão da Análise

1. **Cumprimento Estrito da Lei de Little:** Em todas as 15 configurações experimentais, a igualdade $E[N] = X \cdot E[R]$ é satisfeita com erro relativo inferior a **0,05%** (praticamente nulo).
2. **Independência da Política:** Embora as políticas inteligentes (Round-Robin e Fila Mais Curta) reduzam significativamente tanto $E[R]$ quanto $E[N]$ em relação à política Aleatória, a relação proporcional $E[N] / E[R] = X$ é preservada de forma exata em todas as políticas.
3. **Causa das Mínimas Variações:** As discrepâncias na ordem de $10^{-4}$ são causadas unicamente pela amostragem em tempo discreto do estado do sistema e pelo arredondamento numérico das médias amostrais acumuladas.

Portanto, **os resultados da simulação cumprem perfeitamente a Lei de Little**.


## Resolução Item F) Para o caso λ = 3,3: explique por que o sistema é instável e por que as fórmulas dos itens anteriores deixam de valer. Use a aproximação fluida N(t) ≈ N(0) + (λ − 3μ)t e compare com a curva de N(t) obtida na simulação.

### 1. Por que o sistema é instável?

A capacidade máxima total de processamento do sistema composto por 3 servidores homogêneos, cada um com taxa individual de atendimento $\mu = 1.0$ req/u.t., é dada por:

$$ C_{\text{máx}} = 3 \cdot \mu = 3.0 \text{ requisições / u.t.} $$

Para a taxa de chegada $\lambda = 3.3$ req/u.t., a intensidade de tráfego global do sistema ($\rho$) é:

$$ \rho = \frac{\lambda}{3\mu} = \frac{3.3}{3.0} = 1.10 > 1.0 $$

Em Teoria de Filas, a condição necessária e suficiente para que um sistema alcance um estado de equilíbrio estacionário é que a intensidade de tráfego seja estritamente menor que a unidade ($\rho < 1.0$). Quando $\lambda > 3\mu$ ($\rho = 1.10 > 1$), o sistema é **estocasticamente instável (supercrítico)**: a taxa de chegada supera continuamente a capacidade máxima de serviço dos servidores.

### 2. Por que as fórmulas estacionárias deixam de valer?

As equações analíticas M/M/1 dos itens anteriores (como $E[N] = \frac{\rho}{1-\rho}$ e $E[R] = \frac{1}{\mu - \lambda/3}$) assumem a existência de uma distribuição de probabilidade limite quando $t \to \infty$. 

Matematicamente, a derivação do modelo estacionário depende do somatório da série geométrica de probabilidade de estados $\sum_{k=0}^{\infty} \rho^k = \frac{1}{1-\rho}$. Para $\rho \ge 1.0$, essa série **diverge** para o infinito:

$$ \lim_{t \to \infty} E[N(t)] = \infty \quad \text{e} \quad \lim_{t \to \infty} E[R(t)] = \infty $$

Portanto, não existe um valor médio constante ou distribuição limite em estado estacionário; a fila cresce indefinidamente enquanto houver tráfego de entrada.

### 3. Aproximação Fluida determinística

Em regimes supercríticos ($\rho > 1$), a dinâmica estocástica passa a ser dominada por uma tendência determinística conhecida como **aproximação fluida**. O diferencial líquido (*drift*) de acúmulo de requisições por unidade de tempo é:

$$ \text{drift} = \lambda - 3\mu = 3.3 - 3.0 = +0.3 \text{ requisições / u.t.} $$

Logo, a aproximação fluida modela a evolução temporal do número de requisições $N(t)$ no sistema por uma equação linear:

$$ N(t) \approx N(0) + (\lambda - 3\mu) t = N(0) + 0.3 \cdot t $$

### 4. Correspondência com as Métricas e Resultados da Simulação

Ao analisar os dados obtidos no experimento instável (`results/results.json` e gráfico `results/N_t_lambda33.png`), observa-se perfeita correspondência com a teoria fluida:

1. **Saturação da Vazão Efetiva ($X \approx 3.0$ req/u.t.):**
   - Embora a taxa de chegada seja $\lambda = 3.3$, a vazão média de saída medida na simulação estabiliza no gargalo físico do sistema: $X_{\text{simulado}} \approx 3.0004$ req/u.t.
   - Todos os 3 servidores operam em **100% de utilização** ($U_1 = U_2 = U_3 = 1.0$).

2. **Acúmulo Contínuo no Sistema ($E[N]$ médio):**
   - Devido ao *drift* de $+0.3$ req/u.t., as requisições não atendidas se acumulam na fila indefinidamente.
   - Ao longo da janela de simulação ($t = 5000$ u.t.), a métrica amostraria acumulada de requisições no sistema atinge o valor médio de **$E[N]_{\text{simulado}} \approx 866.21$** requisições na política aleatória.

3. **Validação Gráfica da Inclinação (`results/N_t_lambda33.png`):**
   - O gráfico temporal $N(t)$ gerado pelo simulador demonstra um crescimento linear sustentado ao longo do tempo.
   - A inclinação da curva empírica coincide exatamente com a reta teórica da aproximação fluida $N(t) = N(0) + 0.3 \cdot t$, confirmando experimentalmente o comportamento supercrítico do sistema.

