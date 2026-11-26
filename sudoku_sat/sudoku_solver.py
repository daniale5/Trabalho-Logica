"""Sudoku 9x9 como problema SAT. Base: modelagem do professor Alexandre Arruda."""
import argparse
import json
from itertools import combinations
from pathlib import Path

DIGITOS = range(1, 10)
INDICES = range(1, 4)
TABULEIRO_PROFESSOR = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]


def criar_mapeamentos():
    mapping_to_int = {}
    mapping_from_int = {}
    counter_mapping = 1
    # Mesma ordem e nomenclatura do código original.
    for quadrant_i in INDICES:
        for quadrant_j in INDICES:
            for matrix_i in INDICES:
                for matrix_j in INDICES:
                    for value in DIGITOS:
                        proposition = f'{value}_{matrix_i}_{matrix_j}_{quadrant_i}_{quadrant_j}'
                        mapping_to_int[proposition] = counter_mapping
                        mapping_from_int[counter_mapping] = proposition
                        counter_mapping += 1
    return mapping_to_int, mapping_from_int


mapping_to_int, mapping_from_int = criar_mapeamentos()


def literal(linha, coluna, valor):
    """Coordenadas globais 1..9 -> identificador na nomenclatura original."""
    quadrant_i, matrix_i = divmod(linha - 1, 3)
    quadrant_j, matrix_j = divmod(coluna - 1, 3)
    proposition = f'{valor}_{matrix_i+1}_{matrix_j+1}_{quadrant_i+1}_{quadrant_j+1}'
    return mapping_to_int[proposition]


def validar_entrada(tabuleiro):
    """Valida formato/domínio; conflitos lógicos são tratados pelo SAT."""
    if not isinstance(tabuleiro, (list, tuple)) or len(tabuleiro) != 9:
        raise ValueError('O tabuleiro deve ter 9 linhas.')
    for linha in tabuleiro:
        if not isinstance(linha, (list, tuple)) or len(linha) != 9:
            raise ValueError('Cada linha deve ter 9 células.')
        for valor in linha:
            if type(valor) is not int or not 0 <= valor <= 9:
                raise ValueError('As células devem conter inteiros de 0 a 9.')


def exatamente_um(formula, literais):
    """Uma cláusula positiva e uma negativa para cada par distinto."""
    formula.append(list(literais))
    for a, b in combinations(literais, 2):
        formula.append([-a, -b])


def restricoes_celulas(formula):
    for linha in DIGITOS:
        for coluna in DIGITOS:
            exatamente_um(formula, [literal(linha, coluna, v) for v in DIGITOS])


def restricoes_linhas(formula):
    for linha in DIGITOS:
        for valor in DIGITOS:
            exatamente_um(formula, [literal(linha, c, valor) for c in DIGITOS])


def restricoes_colunas(formula):
    for coluna in DIGITOS:
        for valor in DIGITOS:
            exatamente_um(formula, [literal(l, coluna, valor) for l in DIGITOS])


def restricoes_quadrantes(formula):
    for quadrant_i in INDICES:
        for quadrant_j in INDICES:
            for value in DIGITOS:
                literais = []
                for matrix_i in INDICES:
                    for matrix_j in INDICES:
                        proposition = f'{value}_{matrix_i}_{matrix_j}_{quadrant_i}_{quadrant_j}'
                        literais.append(mapping_to_int[proposition])
                exatamente_um(formula, literais)


def restricoes_pistas(formula, tabuleiro):
    for linha in DIGITOS:
        for coluna in DIGITOS:
            valor = tabuleiro[linha-1][coluna-1]
            if valor != 0:
                formula.append([literal(linha, coluna, valor)])


def construir_formula(tabuleiro):
    """Retorna as cláusulas CNF como listas e as contagens por grupo."""
    validar_entrada(tabuleiro)
    formula = []
    contagens = {}
    for nome, gerar in [('celulas', restricoes_celulas), ('linhas', restricoes_linhas),
                        ('colunas', restricoes_colunas), ('quadrantes', restricoes_quadrantes)]:
        antes = len(formula)
        gerar(formula)
        contagens[nome] = len(formula) - antes
    antes = len(formula)
    restricoes_pistas(formula, tabuleiro)
    contagens['pistas'] = len(formula) - antes
    return formula, contagens


def resolver_glucose(clauses):
    from pysat.formula import CNF
    from pysat.solvers import Glucose4
    formula = CNF(from_clauses=clauses)
    with Glucose4(bootstrap_with=formula.clauses) as solver:
        if not solver.solve():
            return None
        return solver.get_model()


def resolver_sympy(clauses):
    """Backend SAT alternativo para verificação; não usa backtracking de Sudoku."""
    from sympy import And, Or, Symbol
    from sympy.logic.inference import satisfiable
    simbolos = [Symbol(f'p{i}') for i in range(1, 730)]
    # Reutiliza os mesmos literais inteiros, traduzindo-os para expressões SymPy.
    literais = {i: s for i, s in enumerate(simbolos, 1)}
    literais.update({-i: ~s for i, s in enumerate(simbolos, 1)})
    formula = And(*(Or(*(literais[i] for i in clause)) for clause in clauses))
    modelo = satisfiable(formula, algorithm='dpll2')
    if modelo is False:
        return None
    return [i if modelo.get(s, False) else -i for i, s in enumerate(simbolos, 1)]


def reconstruir_tabuleiro(modelo):
    tabuleiro = [[0] * 9 for _ in DIGITOS]
    for identificador in modelo:
        if identificador <= 0:
            continue
        value, matrix_i, matrix_j, quadrant_i, quadrant_j = map(
            int, mapping_from_int[identificador].split('_'))
        linha = (quadrant_i - 1) * 3 + matrix_i - 1
        coluna = (quadrant_j - 1) * 3 + matrix_j - 1
        if tabuleiro[linha][coluna] != 0:
            raise RuntimeError('Modelo atribuiu dois valores à mesma célula.')
        tabuleiro[linha][coluna] = value
    return tabuleiro


def verificar_solucao(original, solucao):
    validar_entrada(original)
    validar_entrada(solucao)
    esperados = set(DIGITOS)
    pistas = all(original[l][c] == 0 or original[l][c] == solucao[l][c]
                 for l in range(9) for c in range(9))
    linhas = all(set(linha) == esperados for linha in solucao)
    colunas = all({solucao[l][c] for l in range(9)} == esperados for c in range(9))
    quadrantes = all({solucao[l][c] for l in range(i, i+3) for c in range(j, j+3)} == esperados
                     for i in (0, 3, 6) for j in (0, 3, 6))
    return {'pistas': pistas, 'linhas': linhas, 'colunas': colunas, 'quadrantes': quadrantes}


def resolver_sudoku(tabuleiro, backend='glucose'):
    clauses, contagens = construir_formula(tabuleiro)
    backends = {'glucose': resolver_glucose, 'sympy': resolver_sympy}
    if backend not in backends:
        raise ValueError('Backend desconhecido.')
    modelo = backends[backend](clauses)
    if modelo is None:
        return None, contagens
    # Verifica também todas as cláusulas do modelo encontrado.
    verdadeiros = set(modelo)
    if not all(any(lit in verdadeiros for lit in clause) for clause in clauses):
        raise RuntimeError('O modelo não satisfaz a CNF.')
    solucao = reconstruir_tabuleiro(modelo)
    if not all(verificar_solucao(tabuleiro, solucao).values()):
        raise RuntimeError('A solução não respeita as regras do Sudoku.')
    return solucao, contagens


def exibir_tabuleiro(tabuleiro):
    borda = '+-------+-------+-------+'
    for i, linha in enumerate(tabuleiro):
        if i % 3 == 0:
            print(borda)
        grupos = [' '.join(str(v) if v else '.' for v in linha[j:j+3]) for j in (0, 3, 6)]
        print('| ' + ' | '.join(grupos) + ' |')
    print(borda)


def main():
    parser = argparse.ArgumentParser(description='Resolvedor SAT de Sudoku 9x9')
    parser.add_argument('arquivo', nargs='?', help='Matriz 9x9 em JSON (0 = vazio)')
    parser.add_argument('--backend', choices=['glucose', 'sympy'], default='glucose')
    args = parser.parse_args()
    try:
        tabuleiro = json.loads(Path(args.arquivo).read_text(encoding='utf-8')) if args.arquivo else TABULEIRO_PROFESSOR
        solucao, contagens = resolver_sudoku(tabuleiro, args.backend)
    except (ValueError, OSError) as erro:
        parser.exit(2, f'Entrada inválida: {erro}\n')
    except ImportError as erro:
        parser.exit(2, f'Dependência ausente: {erro}. Instale os requisitos.\n')
    print('Entrada:')
    exibir_tabuleiro(tabuleiro)
    print(f'Variáveis: {len(mapping_to_int)} | Cláusulas: {sum(contagens.values())}')
    print(f'Grupos: {contagens} | Backend: {args.backend}')
    if solucao is None:
        print('UNSAT: não existe solução.')
        return
    print('SAT: solução encontrada:')
    exibir_tabuleiro(solucao)
    print('Validação:', verificar_solucao(tabuleiro, solucao))


if __name__ == '__main__':
    main()
