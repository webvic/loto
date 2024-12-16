# constants.py

from enum import Enum

# Перечисление статусов игры
class GameStatus(Enum):
    NEXT_MOVE = 1
    WIN = 2
    LOOSE = 3

# Константы для игры в лото
LOTTO_NUM = 90                     # Максимальное число бочонка
NUMBER_RANGE = list(range(1, LOTTO_NUM + 1))  # Числа от 1 до LOTTO_NUM
CARD_ROWS = 3                      # Количество рядов на карточке
CARD_COLS = 9                      # Количество колонок на карточке
NUMBERS_PER_ROW = 5                # Количество чисел в каждом ряду
BLANK = 0                          # Обозначение пустой ячейки
CROSS = '-'                        # Обозначение зачёркнутого числа
MISTAKE_RATE = 0.01                # Процент ошибок робота
