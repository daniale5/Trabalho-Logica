# Sudoku SAT — Lógica para Computação

Projeto acadêmico baseado no código de partida do professor Alexandre Arruda. O objetivo é modelar qualquer Sudoku clássico 9×9 como uma fórmula proposicional em Forma Normal Conjuntiva (CNF) e resolvê-lo com um SAT Solver.

## Integrantes

Preencher com os nomes reais (máximo de três pessoas, conforme enunciado). Verificar as regras da disciplina sobre autoria e uso de IA antes do envio.

## Fundamentos e modelagem

Uma variável proposicional `value_matrix_i_matrix_j_quadrant_i_quadrant_j` afirma que determinado valor ocupa determinada posição interna de um quadrante. Os dois dicionários `mapping_to_int` e `mapping_from_int` preservam a nomenclatura e a ordem do código de sala. São 9 × 9 × 9 = 729 variáveis.

Os identificadores positivos representam literais positivos e os negativos, suas negações. Uma lista de inteiros representa uma disjunção; a lista de cláusulas representa sua conjunção. O solver procura um modelo que torne todas as cláusulas verdadeiras.

Usamos P(l,c,v) para indicar que o valor v ocupa a linha l e coluna c, de 1 a 9. A função `literal` traduz essa notação para o mapeamento original usando `divmod`.

Para qualquer grupo de nove literais x1,...,x9, a função `exatamente_um` gera a cláusula (x1 ∨ ... ∨ x9), que exige pelo menos um, e para cada par i<j gera (¬xi ∨ ¬xj), que proíbe dois simultaneamente. A segunda regra resulta de ¬(xi ∧ xj), pela lei de De Morgan. A conjunção das duas exige exatamente um.

| Regra | Grupo de nove literais | Exemplo | Cláusulas |
|---|---|---|---:|
| Células | P(l,c,v), variando v | Uma célula não pode conter 1 e 2 | 2997 |
| Linhas | P(l,c,v), variando c | O 5 aparece uma vez na linha 3 | 2997 |
| Colunas | P(l,c,v), variando l | O 8 aparece uma vez na coluna 5 | 2997 |
| Quadrantes | P(l,c,v), variando as posições do bloco | O 4 aparece uma vez no bloco central | 2997 |
| Pistas | P(l,c,v) para cada valor inicial diferente de zero | P(1,1,5), cláusula [5] | k |

Cada grupo exige 1 + C(9,2) = 37 cláusulas. Há 81 grupos em cada uma das quatro primeiras regras: 4 × 81 × 37 = 11988. Com k pistas, são 11988+k cláusulas geradas. No caso obrigatório, k=30, totalizando 12018 cláusulas (10560 distintas). Algumas cláusulas binárias entre quadrantes e linhas/colunas são redundantes; elas foram mantidas para explicitar a modelagem.

A fórmula contém as regras; o modelo é uma atribuição de verdade que satisfaz a fórmula. A reconstrução usa apenas os identificadores positivos, decodifica os nomes das proposições e obtém 81 valores verdadeiros. A validação verifica todas as cláusulas, pistas, linhas, colunas e quadrantes.

## Tecnologias

- Python 3 (biblioteca padrão e python-sat)
- PySAT / Glucose4: backend principal
- SymPy 1.14.0 / DPLL2: backend alternativo de verificação (opcional)
- unittest: testes automatizados

## Instalação e execução

Em um terminal com Python instalado:

```bash
python -m pip install -r requirements.txt
python sudoku_solver.py
python sudoku_solver.py exemplos/professor.json
python -m unittest -v
```

Um tabuleiro JSON deve conter nove listas com nove inteiros de 0 a 9 (0 representa vazio). O programa retorna SAT com uma solução, UNSAT quando não há solução ou informa erro de entrada para uma matriz malformada. Pistas conflitantes são tratadas como UNSAT. Não é feita a enumeração de todas as soluções nem a verificação de unicidade. O escopo é Sudoku clássico 9×9.

Para usar o backend alternativo:

```bash
python -m pip install -r requirements-verificacao.txt
python sudoku_solver.py --backend sympy
```

Para testar com SymPy, no Linux/macOS:

```bash
SUDOKU_BACKEND=sympy python -m unittest -v
```

No PowerShell do Windows:

```powershell
$env:SUDOKU_BACKEND = 'sympy'
python -m unittest -v
Remove-Item Env:SUDOKU_BACKEND
```

## Entrada e saída do caso obrigatório

Entrada transcrita do PDF da atividade:

```text
5 3 0 | 0 7 0 | 0 0 0
6 0 0 | 1 9 5 | 0 0 0
0 9 8 | 0 0 0 | 0 6 0
8 0 0 | 0 6 0 | 0 0 3
4 0 0 | 8 0 3 | 0 0 1
7 0 0 | 0 2 0 | 0 0 6
0 6 0 | 0 0 0 | 2 8 0
0 0 0 | 4 1 9 | 0 0 5
0 0 0 | 0 8 0 | 0 7 9
```

Saída validada pelo backend SymPy:

```text
5 3 4 | 6 7 8 | 9 1 2
6 7 2 | 1 9 5 | 3 4 8
1 9 8 | 3 4 2 | 5 6 7
8 5 9 | 7 6 1 | 4 2 3
4 2 6 | 8 5 3 | 7 9 1
7 1 3 | 9 2 4 | 8 5 6
9 6 1 | 5 3 7 | 2 8 4
2 8 7 | 4 1 9 | 6 3 5
3 4 5 | 2 8 6 | 1 7 9
```

## Evidências e limites da validação

O ambiente de desenvolvimento não disponibilizou a instalação de python-sat. Os oito testes foram efetivamente executados com SymPy 1.14.0, incluindo o tabuleiro do professor, tabuleiro quase completo, tabuleiro com 80 vazios, UNSAT com e sem conflito imediato, entradas inválidas, mapeamento e contagens. Consulte `testes_executados.txt`. A mesma CNF é encaminhada ao Glucose4 pelo backend principal; execute os testes com ele antes da entrega para verificar essa integração. Nenhuma alegação de execução do Glucose4 é feita aqui.

## Arquivos

- `sudoku_solver.py`: implementação e interface de terminal
- `test_sudoku.py`: testes automatizados
- `requirements.txt`: dependência principal
- `requirements-verificacao.txt`: dependência alternativa
- `exemplos/`: matrizes de entrada
- `testes_executados.txt`: registro dos testes efetivamente realizados
- `roteiro_video.md`: roteiro de estudo e apresentação

## Referências e autoria

- Alexandre Arruda, **Atividade de Lógica para Computação** e código inicial de sala, 2026.
- PySAT: https://pysathq.github.io/
- SymPy: https://docs.sympy.org/

A equipe deve revisar, compreender e adaptar o projeto, registrar as contribuições reais e respeitar as orientações de autoria do professor. O enunciado exige o envio, via SIGAA até 06/12/2026, de um arquivo contendo o link do repositório e do vídeo de apresentação.
