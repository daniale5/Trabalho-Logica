import os
import unittest
from copy import deepcopy
from sudoku_solver import (TABULEIRO_PROFESSOR, construir_formula, literal,
                           mapping_to_int, mapping_from_int, resolver_sudoku,
                           verificar_solucao)

BACKEND = os.getenv('SUDOKU_BACKEND', 'glucose')
ESPERADO = [
    [5,3,4,6,7,8,9,1,2], [6,7,2,1,9,5,3,4,8], [1,9,8,3,4,2,5,6,7],
    [8,5,9,7,6,1,4,2,3], [4,2,6,8,5,3,7,9,1], [7,1,3,9,2,4,8,5,6],
    [9,6,1,5,3,7,2,8,4], [2,8,7,4,1,9,6,3,5], [3,4,5,2,8,6,1,7,9],
]

class SudokuTests(unittest.TestCase):
    def resolver(self, board):
        return resolver_sudoku(board, BACKEND)[0]

    def test_mapeamento(self):
        self.assertEqual(len(mapping_to_int), 729)
        self.assertEqual(set(mapping_to_int.values()), set(range(1,730)))
        self.assertTrue(all(mapping_from_int[i] == p for p,i in mapping_to_int.items()))
        self.assertEqual(literal(7,5,7), mapping_to_int['7_1_2_3_2'])
        self.assertEqual(len({literal(l,c,v) for l in range(1,10) for c in range(1,10) for v in range(1,10)}),729)

    def test_contagens(self):
        clauses, counts = construir_formula(TABULEIRO_PROFESSOR)
        self.assertEqual(counts, dict(celulas=2997, linhas=2997, colunas=2997, quadrantes=2997, pistas=30))
        self.assertEqual(len(clauses), 12018)
        self.assertEqual(sum(len(c)==9 for c in clauses),324)
        self.assertEqual(sum(len(c)==2 for c in clauses),11664)
        self.assertEqual(sum(len(c)==1 for c in clauses),30)
        self.assertEqual(len({tuple(sorted(c)) for c in clauses}), 10560)

    def test_professor(self):
        board = deepcopy(TABULEIRO_PROFESSOR)
        sol = self.resolver(board)
        self.assertEqual(sol, ESPERADO)
        self.assertEqual(board, TABULEIRO_PROFESSOR)
        self.assertTrue(all(verificar_solucao(board,sol).values()))

    def test_poucos_vazios(self):
        board = deepcopy(ESPERADO)
        board[0][0] = board[8][8] = 0
        self.assertEqual(self.resolver(board), ESPERADO)

    def test_muitos_vazios(self):
        board = [[0]*9 for _ in range(9)]
        board[0][0] = 5
        sol = self.resolver(board)
        self.assertTrue(all(verificar_solucao(board,sol).values()))

    def test_sem_solucao_sem_conflito_imediato(self):
        board = deepcopy(TABULEIRO_PROFESSOR)
        board[0][2] = 1
        self.assertIsNone(self.resolver(board))

    def test_pistas_conflitantes(self):
        board = deepcopy(TABULEIRO_PROFESSOR)
        board[0][2] = 5
        self.assertIsNone(self.resolver(board))

    def test_entrada_invalida(self):
        for board in ([[0]*9]*8, [[0]*8]*9, [[10]*9]*9, [[True]*9]*9):
            with self.subTest(board=board):
                with self.assertRaises(ValueError):
                    self.resolver(board)

if __name__ == '__main__':
    unittest.main()
