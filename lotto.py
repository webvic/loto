# lotto.py
# Игра в лото

import random
import numpy as np
import pandas as pd
from constants import (
    GameStatus, LOTTO_NUM, NUMBER_RANGE, CARD_ROWS, CARD_COLS,
    NUMBERS_PER_ROW, NUMBERS_IN_CARD, BLANK, CROSS, CROSS_STR, MISTAKE_RATE
)

class LottoCard:
    
    def __init__(self, numbers=None):
        """
        Инициализирует карточку лото.
        
        :param numbers: Список чисел для карточки. Если None, используется диапазон от 1 до LOTTO_NUM.
        """
        if numbers is None:
            self.numbers = NUMBER_RANGE.copy()
        else:
            if len(numbers) < NUMBERS_IN_CARD:
                raise ValueError(f"Для создания карточки необходимо как минимум {NUMBERS_IN_CARD} чисел.")
            if len(set(numbers)) != len(numbers):
                raise ValueError("Числа в списке должны быть уникальными.")
            if not all(num in NUMBER_RANGE for num in numbers):
                raise ValueError(f"Все числа должны быть в диапазоне от {NUMBER_RANGE[0]} до {NUMBER_RANGE[-1]}.")
            self.numbers = numbers.copy()
        self.card = self._create_card()
    
    @property
    def df(self):
        return self.card
    
    @df.setter
    def df(self, new_card):
        self.card = new_card
    
    def _create_card(self):        
        card_rows = []
        for _ in range(CARD_ROWS):
            card_dict = {k: BLANK for k in range(CARD_COLS)}
            # Выбираем NUMBERS_PER_ROW уникальных чисел и колонок
            row_numbers = sorted(random.sample(self.numbers, k=NUMBERS_PER_ROW))
            row_indices = sorted(random.sample(range(CARD_COLS), k=NUMBERS_PER_ROW))
            # Заполняем выбранные колонки числами
            card_dict.update(zip(row_indices, row_numbers))
            card_rows.append(card_dict)
            # Удаляем выбранные числа, чтобы избежать повторений
            self.numbers = [num for num in self.numbers if num not in row_numbers]
        
        # Создаём DataFrame с типом данных object
        card = pd.DataFrame(card_rows)
        print('Сгенерил карту:\n', card)
        return card

class Player:
        
    def __init__(self, name: str, is_human: bool = True, card: 'LottoCard' = None, mistake_rate=MISTAKE_RATE):
        """
        Инициализирует игрока.
        
        :param name: Имя игрока.
        :param is_human: Флаг, указывающий, является ли игрок человеком.
        :param card: Объект LottoCard для игрока. Если None, создаётся новая карточка.
        :param mistake_rate: Вероятность ошибки робота.
        """
        self.name = name
        self.card = card if card else LottoCard()
        self.is_human = is_human
        self.moves = {'row': [], 'col': []}
        self.mistake_rate = mistake_rate  # Добавляем атрибут mistake_rate

    def check_barrel(self, barrel):
        """
        Проверяет наличие номера бочонка на карточке.
        
        :param barrel: Номер бочонка.
        :return: Кортеж из индексов строки и колонки, если число найдено, иначе (None, None).
        """
        row_idx, col_idx = np.where(self.card.df == barrel)
        
        if row_idx.size:  # Если число найдено, позиции не пустые
            return int(row_idx[0]), int(col_idx[0])
        else:
            # Если нет, возвращаем 2 х None
            return None, None

    def update_moves_list(self, row_idx, col_idx, barrel):
        """
        Обновляет список ходов игрока и заменяет число на CROSS.
        
        :param row_idx: Индекс строки.
        :param col_idx: Индекс колонки.
        :param barrel: Номер бочонка.
        :return: Статус игры.
        """
        self.moves['row'].append(row_idx)
        self.moves['col'].append(col_idx)
        print(f'Игрок {self.name} вычеркнул бочонок {barrel} на строке {row_idx} в столбце {col_idx}')
        # Заменяем число на CROSS в карточке
        self.card.df.iat[row_idx, col_idx] = CROSS

        # Проверяем окончание игры
        if len(self.moves['row']) < NUMBERS_IN_CARD:
            return GameStatus.NEXT_MOVE
        else:
            return GameStatus.WIN

    def check_move(self, strike_out, barrel):
        """
        Проверяет ход игрока.
        
        :param strike_out: Команда вычеркнуть число (True/False).
        :param barrel: Номер бочонка.
        :return: Статус игры.
        """
        row_idx, col_idx = self.check_barrel(barrel)
        barrel_on_card = row_idx is not None

        # Моделируем у робота возможность ошибки
        if not self.is_human:
            # Робот может ошибиться с вероятностью mistake_rate
            if random.random() > self.mistake_rate:
                strike_out = barrel_on_card
            else:            
                # В mistake_rate случаев инвертируем правильный результат    
                strike_out = not barrel_on_card

        if barrel_on_card and strike_out:
            # Если цифра нашлась и команда "Вычеркнуть", то верный ход
            return self.update_moves_list(row_idx, col_idx, barrel)
        elif not barrel_on_card and not strike_out:
            # Верный пропуск хода
            return GameStatus.NEXT_MOVE
        else:
            # Ошибка: зря вычеркнул или не заметил
            print(f'{self.name} ошибся')
            if barrel_on_card:
                print('Не заметил номера бочонка в своей карточке')
            else:
                print('Попытался вычеркнуть номер, которого нет в карточке')                
            return GameStatus.LOOSE   

    def show_card(self):
        """
        Готовит DataFrame для печати текущего состояния карты игрока.
        
        :return: DataFrame с актуализированной карточкой.
        """
        # Преобразуем DataFrame в строки и заменяем '0' на пустую строку
        df_str = self.card.df.astype(str).replace(str(BLANK), '')
        row_idx = self.moves['row']
        col_idx = self.moves['col']

        # Если список индексов непустой, произведем замену цифр на прочерки
        if row_idx and col_idx:
            df_str.values[row_idx, col_idx] = CROSS_STR

        # Возвращаем актуализированную таблицу
        return df_str

# Класс для генерации бочонков лото
class Lotto:
    def __init__(self, max_number: int = LOTTO_NUM):
        self.numbers = NUMBER_RANGE.copy()
        random.shuffle(self.numbers)

    def draw(self):
        """
        Выбирает случайный бочонок из оставшихся.
        
        :return: Номер бочонка или None, если бочонки закончились.
        """
        return self.numbers.pop() if self.numbers else None

class PlayRound:

    def __init__(self, *players: 'Player'):
        """
        Инициализирует игровой раунд.
        
        :param players: Игроки участвующие в раунде.
        """
        if not (2 <= len(players) <= 5):
            raise ValueError("Количество игроков должно быть от 2 до 5.")
        self.players = list(players)  # Преобразуем кортеж в список для удобства
        self.lotto = Lotto()
        self.move_num = 0

    def run_play_round(self):
        """
        Запускает один раунд игры со списком игроков.
        """
        players_list = ', '.join([f"{player.name} ({'Человек' if player.is_human else 'Робот'})" for player in self.players])
        print(f"Начало игрового раунда! Игроки: {players_list}")
        print('Карточки игроков:')
        self.print_cards()
        
        # Цикл игры
        while (barrel := self.lotto.draw()):
            self.move_num += 1
            print(f"Ход {self.move_num}: Выбран бочонок: {barrel}")

            # Ходы всех игроков
            for player in self.players.copy():  # Используем копию списка для безопасного удаления
                if player.is_human:
                    input_text = input(f'Ваш ход, {player.name}. Зачеркнуть цифру? (y/n): ')
                    strike_out = input_text.strip().lower() in ['y', 'yes', 'да', '1']
                else:
                    # Робот принимает решение автоматически внутри метода check_move
                    strike_out = None

                status = player.check_move(strike_out, barrel)
                
                if status == GameStatus.WIN:
                    self.print_cards()
                    print(f'Поздравляю! {player.name} выиграл(а)!')
                    return
                elif status == GameStatus.LOOSE:
                    print(f'Игрок {player.name} проиграл(а) и выбывает из игры!')
                    self.players.remove(player)

                    if len(self.players) >= 2:
                        continue
                    if len(self.players) == 1: 
                        print(f'Остался один игрок {self.players[0].name}. Победа присуждается ему')
                        return
                    else:
                        print('Ни одного игрока не осталось. Ничья')
                        return                    
                    
            # Печать текущего статуса карточек
            self.print_cards()        

        else:
            print('Все бочонки кончились! Ничья')

    def print_cards(self):
        """
        Печатает карточки всех игроков в один ряд.
        """
        headers = [f"{player.name} (Зачеркнуто: {len(player.moves['row'])})" for player in self.players]
        df_cards = [player.show_card() for player in self.players]

        # Создаём DataFrame-разделитель
        separator = pd.DataFrame({ '|': [ '|' ] * len(df_cards[0]) }, dtype=object)

        # Объединяем DataFrame и добавляем разделитель между ними, кроме последнего
        dfs_with_separators = [
            pd.concat([df, separator], axis=1) for df in df_cards[:-1]
        ] + [df_cards[-1]]  # Последний DataFrame без разделителя

        # Объединяем все части по горизонтали
        df_joined = pd.concat(dfs_with_separators, axis=1)

        # Формирование многоуровневых заголовков с заменой нижнего уровня на '-'
        multi_cols = []
        for i, header in enumerate(headers):
            card_cols = df_cards[i].columns
            for _ in card_cols:
                multi_cols.append((header, '-'))  # Заменяем названия колонок на '-'
            if i < len(headers) - 1:
                multi_cols.append(('|', '-'))  # Добавляем разделитель с тире

        # Применение MultiIndex
        df_joined.columns = pd.MultiIndex.from_tuples(multi_cols)

        # Выводим результат
        print(df_joined.to_string(index=False))


# Пример использования
if __name__ == "__main__":

    # Создаем игроков с разными карточками (можно передать список чисел при необходимости)
    player1 = Player(name="Лев", is_human=True)
    player2 = Player(name="Боб", is_human=False)
    player3 = Player(name="Виктор", is_human=False)
    player4 = Player(name="Алиса", is_human=False)

    # Создаем игровой раунд с четырьмя игроками
    game_round = PlayRound(player1, player2, player3, player4)
    game_round.run_play_round()
    print(f'Спасибо! Игра закончена на {game_round.move_num} ходу')
