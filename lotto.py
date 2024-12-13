# lotto.py
# Игра в лото

import random
import numpy as np
import pandas as pd
from constants import GameStatus

class LottoCard:
    
    def __init__(self):
        # Список цифр от 1 до 90
        self.numbers = list(range(1, 91))
        self.card = self._create_card()
        # Пустой df для ходов игрока

    def _create_card(self):        
        card_rows=[]
        for _ in range(3):
            card_dict = {k: 0 for k in range(9)}
            row_numbers = sorted(random.sample(self.numbers,k=5))
            row_indices = sorted(random.sample(list(range(9)),k=5))
            # Заполнение нужных записей в словаре
            card_dict.update(zip(row_indices, row_numbers))
            card_rows.append(card_dict)
            # удаляем выбранные цифры из списка
            self.numbers = [num for num in self.numbers if num not in row_numbers]
        
        card = pd.DataFrame(card_rows)
        print('Сгенерил карту:\n', card)
        return card

class Player:
        
    def __init__(self, name: str, is_human: bool = True):

        # Инициализируем игрока
        self.name = name
        self.card = LottoCard()
        self.is_human = is_human
        self.moves = {'row':[],'col':[]}

    def check_barrel(self, barrel):
        # Проверяем наличие номера бочонка на карточке
        # Если есть - возвращаем индексы
        row_idx, col_idx = np.where(self.card.card == barrel)
        
        if row_idx.size: # Если число найдено, позиции не пустые
            return row_idx[0], col_idx[0]
        else:
            # Если нет, возвращаем 2 х None
            return None, None

    def update_moves_list(self,row_idx,col_idx,barrel):

        #  обновляем список ходов 
        self.moves['row'].append(row_idx)
        self.moves['col'].append(col_idx)
        print(f'Игрок {self.name} вычеркнул бочонок {barrel} на строке {row_idx} в столбце {col_idx}')

        # Проверяем окончание игры
        if len(self.moves['row']) < 15:
            return GameStatus.NEXT_MOVE
        else:
            return GameStatus.WIN

    def check_move(self, strike_out,barrel):
        
        # Проверяем ход игрока
        row_idx, col_idx = self.check_barrel(barrel)
        barrel_on_card = row_idx is not None

        # Моделируем у робота возможность ошибки
        if not self.is_human:
            # робот не ошибается в 99% случаев
            if random.random() > 0.01:
                strike_out = barrel_on_card
            else:            
                # в 5% случаев инвертируем правильный результат    
                strike_out = not barrel_on_card

        if barrel_on_card and strike_out:
            # Если цифра нашлась (индекс не None) и команда "Вычеркнуть"
            # то верный ход
            return self.update_moves_list(row_idx,col_idx,barrel)
        elif not barrel_on_card and not strike_out:
            # верный пропуск хода
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
        # готовит df для печати текущего состояния карты игрока
        # Шаг 1: Преобразуем DataFrame в строки и заменяем 'nan' на пустую строку
        df_str = self.card.card.astype(str).replace('0', '')
        row_idx = self.moves['row']
        col_idx =self.moves['col']

        # Если список индексов непустой, произведем замену цифр на прочерки
        if row_idx and col_idx:
            
            # Шаг 3: Присваиваем прочерки в указанных позициях
            df_str.values[row_idx, col_idx] = '-'

        # Шаг 4: Возвращаем актуализированную таблицу
        return df_str
    
# Класс для генерации бочонков лото
class Lotto:
    def __init__(self, max_number: int = 90):
        self.numbers = list(range(1, max_number + 1))
        random.shuffle(self.numbers)

    def draw(self):
        return self.numbers.pop() if self.numbers else None

class PlayRound:

    def __init__(self, *players: 'Player'):
        
        if not (2 <= len(players) <= 5):
            raise ValueError("Количество игроков должно быть от 2 до 5.")
        self.players = list(players)  # Преобразуем кортеж в список для удобства
        self.lotto = Lotto()
        self.move_num = 0
    
    def run_play_round(self):
        
        # Запускает один раунд игры со списком игроков
        players_list= ', '.join([f'{player.name} ({'Человек' if player.is_human else 'Робот'})'for player in self.players])
        print(f"Начало игрового раунда! Игроки: {players_list}")
        print('Карточки игроков:')
        self.print_cards()
        
        # Цикл игры

        while (barrel := self.lotto.draw()):
            self.move_num+=1
            print(f"Выбран бочонок: {barrel}")

            # Ходы всех игроков
            for player in self.players:
                if player.is_human:
                    input_text = input(f'Ваш ход, {player.name}. Зачеркнуть цифру? (y/n): ')
                    strike_out = input_text.strip().lower() in ['y', 'yes', 'да', '1']

                else:
                    # Робот не делает ходов 
                    strike_out = None

                status = player.check_move(strike_out, barrel)
                
                if status == GameStatus.WIN:
                    self.print_cards()
                    print(f'Поздравляю! {player.name} выиграл(а)!')
                    return
                elif status == GameStatus.LOOSE:

                    print(f'{player.name} проиграл(а) и выбывает из игры!')
                    if len(self.players) >= 2:
                        self.players.remove(player)

                    if len(self.players) == 2:
                        continue
                    elif len(self.players) == 1: 
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
        # Печатаем карточки всех игроков в один ряд

        headers = [f"{player.name} (Зачеркнуто: {len(player.moves['row'])})" for player in self.players]
        df_cards = [player.show_card() for player in self.players]

        # Создаём DataFrame-разделитель
        separator = pd.DataFrame({'|': ['|'] * len(df_cards[0])})

        # Объединяем DataFrame и добавляем разделитель между ними, кроме последнего
        dfs_with_separators = [
            pd.concat([df, separator], axis=1) for df in df_cards[:-1]
            ] + [df_cards[-1]]  # Последний DataFrame без разделителя

        # Объединяем все части по горизонтали
        df_joined = pd.concat(dfs_with_separators, axis=1)

        # Формирование многоуровневых заголовков
        multi_cols = []
        for i, header in enumerate(headers):
            card_cols = df_cards[i].columns
            for col in card_cols:
                multi_cols.append((header, col))
            if i < len(headers) - 1:
                multi_cols.append(('|'))

        # Применение MultiIndex
        df_joined.columns = pd.MultiIndex.from_tuples(multi_cols)

        # Убиваем заголовки второго уровня
        # df_joined.columns = df_joined.columns.droplevel(1)

        # Выводим результат
        print(df_joined.to_string(index=False))

# Пример использования
if __name__ == "__main__":

    # Создаем игроков
    player1 = Player(name="Алиса", is_human=False)
    player2 = Player(name="Боб", is_human=False)  # Робот
    player3 = Player(name="Виктор", is_human=False)  # Робот

    # Создаем игровой раунд с двумя игроками
    game_round = PlayRound(player1, player2, player3)
    game_round.run_play_round()
    print(f'Спасибо! Игра закончена на {game_round.move_num} ходу')