# Roteiro de apresentação — Sudoku SAT

Sugestão de duração: 6 a 8 minutos (o PDF não determina duração). Adapte com suas próprias palavras. Grave a execução real do Glucose4 após confirmar a instalação e os testes.

| Tempo | Conteúdo | Mostrar na tela |
|---|---|---|
| 0:00–0:40 | Problema e objetivo: resolver Sudoku 9×9 genericamente com lógica proposicional | Tabuleiro do PDF |
| 0:40–1:40 | Proposição, mapeamentos, 729 variáveis, literais positivos e negativos | `criar_mapeamentos`, `literal`, exemplo 7_1_2_3_2 |
| 1:40–3:30 | Exatamente um: pelo menos um e no máximo um; células, linhas, colunas, quadrantes e pistas | `exatamente_um`, funções de restrições; demonstre De Morgan |
| 3:30–4:30 | CNF, contagem das cláusulas, solver e modelo | `construir_formula`, `resolver_glucose` |
| 4:30–5:45 | Execução do Sudoku original; reconstrução e validação | `python sudoku_solver.py`, `reconstruir_tabuleiro`, `verificar_solucao` |
| 5:45–6:30 | Demonstração de UNSAT e testes | `python sudoku_solver.py exemplos/conflito.json`, `python -m unittest -v` |
| 6:30–7:00 | Conclusão, escopo e limitações | Resultado e repositório |

## Explicação sugerida

A atividade propõe transformar um Sudoku em um problema de satisfatibilidade booleana. O solver não recebe regras de Sudoku diretamente: ele recebe cláusulas que representam cada regra. Mantivemos os mapeamentos do professor e separamos a construção da fórmula da etapa de resolução.

Uma proposição representa uma hipótese sobre um valor em uma célula. Como são 81 células e nove valores possíveis por célula, temos 729 variáveis. Cada variável é identificada por um inteiro, e o sinal negativo representa a negação.

A restrição de pelo menos um utiliza uma cláusula disjuntiva. A de no máximo um utiliza cláusulas negativas para todos os pares. Juntas, garantem exatamente um. Aplicamos essa lógica às células e à ocorrência de cada valor em linhas, colunas e quadrantes. As pistas iniciais geram cláusulas unitárias. Para o tabuleiro do professor, temos 11988 cláusulas das regras mais 30 das pistas.

O Glucose4 procura uma atribuição que satisfaça a CNF. Se encontrar, decodificamos apenas os literais positivos, pois indicam as hipóteses verdadeiras. Reconstruímos o tabuleiro e verificamos todas as regras. Se não houver atribuição, o resultado é UNSAT. O programa não usa backtracking convencional de Sudoku nem depende do tabuleiro específico.

## Perguntas para treinar

1. **Por que 729 variáveis?** São 81 células, cada uma com nove possibilidades.
2. **Por que inteiros negativos?** Representam a negação do literal positivo correspondente.
3. **Por que não basta uma cláusula com nove literais positivos?** Ela permite que dois ou mais valores sejam verdadeiros.
4. **Por que 36 pares?** C(9,2)=36, cada par distinto gera uma proibição.
5. **O que ocorre se retirar as pistas?** O solver ainda pode encontrar um Sudoku completo válido, mas não precisa respeitar o tabuleiro original.
6. **Por que há cláusulas repetidas?** Uma mesma proibição pode pertencer às regras de linha/coluna e quadrante. Isso não muda as soluções.
7. **O que significa UNSAT?** Não há atribuição que torne todas as cláusulas verdadeiras.
8. **Qual a diferença entre CNF e modelo?** CNF é a descrição lógica do problema; modelo é uma atribuição que a satisfaz.
9. **Por que o solver não devolve diretamente o tabuleiro?** Ele trabalha com literais booleanos; o mapeamento inverso reconstrói a matriz.
10. **O programa verifica unicidade?** Não. Encontra uma solução quando existe. Para testar unicidade, seria necessário bloquear a primeira solução e executar o solver novamente.
11. **Por que não utilizar a fórmula da demonstração?** Ela já é UNSAT e não pode se tornar SAT ao adicionar cláusulas.
12. **Por que separar CNF e solver?** Para organizar a geração, a inspeção e contagem das restrições independentemente do algoritmo de resolução.

## Antes de gravar

Preencha os integrantes reais no README, execute os testes com Glucose4, confira os resultados e explique a lógica com suas próprias palavras. Não apresente como executado aquilo que não foi testado. A validação inicial foi realizada com SymPy devido à indisponibilidade de python-sat no ambiente de elaboração.
