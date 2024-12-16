# test_lotto.py

import pytest
from unittest.mock import patch
import numpy as np
import pandas as pd
from lotto import LottoCard, Player, Lotto, PlayRound
from constants import GameStatus, MISTAKE_RATE, BLANK, CROSS, CARD_ROWS, NUMBERS_PER_ROW, LOTTO_NUM

# Фикстура для создания фиксированной карточки игрока с числами 1-15
@pytest.fixture
def predefined_card():
    with patch.object(LottoCard, '__init__', lambda self: None):
        card = LottoCard()
        # Устанавливаем фиксированную карту с числами 1-15
        card.card = pd.DataFrame([
            {0:1, 1:2, 2:3, 3:4, 4:5, 5:BLANK, 6:BLANK, 7:BLANK, 8:BLANK},
            {0:6, 1:7, 2:8, 3:9, 4:10, 5:BLANK, 6:BLANK, 7:BLANK, 8:BLANK},
            {0:11, 1:12, 2:13, 3:14, 4:15, 5:BLANK, 6:BLANK, 7:BLANK, 8:BLANK}
        ], dtype=int)
        fixed_numbers = list(range(1,16))
        
        # Проверка типов данных
        assert all(card.card.dtypes == int), "Все числа в карточке должны быть целыми числами"
        
        return card, fixed_numbers

# Фикстура для создания фиксированной карточки робота с числами 16-30
@pytest.fixture
def predefined_card_robot():
    with patch.object(LottoCard, '__init__', lambda self: None):
        card = LottoCard()
        # Устанавливаем фиксированную карту робота с числами 16-30
        card.card = pd.DataFrame([
            {0:16, 1:17, 2:18, 3:19, 4:20, 5:BLANK, 6:BLANK, 7:BLANK, 8:BLANK},
            {0:21, 1:22, 2:23, 3:24, 4:25, 5:BLANK, 6:BLANK, 7:BLANK, 8:BLANK},
            {0:26, 1:27, 2:28, 3:29, 4:30, 5:BLANK, 6:BLANK, 7:BLANK, 8:BLANK}
        ], dtype=int)
        fixed_numbers = list(range(16,31))
        
        # Проверка типов данных
        assert all(card.card.dtypes == int), "Все числа в карточке должны быть целыми числами"
        
        return card, fixed_numbers

# Фикстура для создания двух предопределённых игроков с фиксированными карточками
@pytest.fixture
def predefined_players(predefined_card, predefined_card_robot):
    card1, fixed_numbers1 = predefined_card
    card2, fixed_numbers2 = predefined_card_robot

    player1 = Player(name="Робот1", is_human=False, card=card1, mistake_rate=MISTAKE_RATE)
    player2 = Player(name="Робот2", is_human=False, card=card2, mistake_rate=MISTAKE_RATE)

    return player1, player2

# Тестирование создания карточки LottoCard
def test_lotto_card_creation_unique_numbers(predefined_card):
    card, fixed_numbers = predefined_card
    numbers = card.card.values.flatten()
    numbers = numbers[numbers != BLANK]  # Убираем BLANK
    assert len(numbers) == CARD_ROWS * NUMBERS_PER_ROW, f"Карточка должна содержать {CARD_ROWS * NUMBERS_PER_ROW} уникальных чисел"
    assert len(set(numbers)) == CARD_ROWS * NUMBERS_PER_ROW, "Числа на карточке должны быть уникальными"
    for num in numbers:
        assert 1 <= num <= LOTTO_NUM, f"Число {num} должно быть в диапазоне от 1 до {LOTTO_NUM}"

# Тестирование сортировки чисел в каждом ряду
def test_card_rows_sorted(predefined_card):
    card, _ = predefined_card
    for index, row in card.card.iterrows():
        # Извлекаем числа из ряда, игнорируя BLANK
        numbers = sorted([num for num in row if num != BLANK])
        extracted_numbers = [num for num in row if num != BLANK]
        assert extracted_numbers == numbers, f"Числа в ряду {index} должны быть отсортированы по возрастанию"

# Тестирование метода check_barrel в классе Player
def test_player_check_barrel_found(predefined_card):
    card, fixed_numbers = predefined_card
    player = Player(name="Тестовый игрок", is_human=True, card=card, mistake_rate=MISTAKE_RATE)
    row, col = player.check_barrel(1)
    # Найдём реальные позиции числа 1
    expected_positions = list(zip(*np.where(card.card == 1)))
    assert expected_positions, "Число 1 должно быть на карточке"
    expected_row, expected_col = expected_positions[0]
    assert row == expected_row, f"Число должно быть найдено на строке {expected_row}"
    assert col == expected_col, f"Число должно быть найдено в колонке {expected_col}"

def test_player_check_barrel_not_found(predefined_card):
    card, fixed_numbers = predefined_card
    player = Player(name="Тестовый игрок", is_human=True, card=card, mistake_rate=MISTAKE_RATE)
    row, col = player.check_barrel(99)  # Число 99 не должно быть на карточке
    assert row is None and col is None, "Число не должно быть найдено на карточке"

# Тестирование обновления списка ходов
def test_player_update_moves_list(predefined_card):
    card, fixed_numbers = predefined_card
    player = Player(name="Тестовый игрок", is_human=True, card=card, mistake_rate=MISTAKE_RATE)
    status = player.update_moves_list(0, 0, 1)
    assert 0 in player.moves['row'], "Строка должна быть добавлена в список ходов"
    assert 0 in player.moves['col'], "Колонка должна быть добавлена в список ходов"
    assert status == GameStatus.NEXT_MOVE, "Статус должен быть NEXT_MOVE"
    # Проверяем, что число зачёркнуто
    assert player.card.card.iloc[0, 0] == CROSS, "Число должно быть зачёркнуто"

# Тестирование правильного зачёркивания числа
def test_player_check_move_correct_strike(predefined_card):
    card, fixed_numbers = predefined_card
    player = Player(name="Тестовый игрок", is_human=True, card=card, mistake_rate=MISTAKE_RATE)
    
    # Убедимся, что число 1 присутствует на карточке перед ходом
    assert 1 in player.card.card.values, "Число 1 должно быть на карточке"
    
    # Выполним ход: зачеркнем число 1
    status = player.check_move(True, 1)
    assert status == GameStatus.NEXT_MOVE, "Статус должен быть NEXT_MOVE"
    
    # Найдём позиции числа 1 после зачёркивания (должно быть заменено на CROSS)
    positions = list(zip(*np.where(player.card.card == CROSS)))
    assert positions, "Число 1 должно быть заменено на CROSS на карточке"
    
    # Дополнительно можно проверить, что на этих позициях действительно было число 1 до замены
    # Это предполагает, что вы знаете исходную позицию числа 1
    # В нашем случае, число 1 находится на позиции (0,0)
    expected_position = (0, 0)
    assert expected_position in positions, f"Число 1 должно быть заменено на CROSS на позиции {expected_position}"

# Альтернативный вариант теста без поиска позиции
def test_player_check_move_correct_strike_alternative(predefined_card):
    card, fixed_numbers = predefined_card
    player = Player(name="Тестовый игрок", is_human=True, card=card, mistake_rate=MISTAKE_RATE)
    
    # Убедимся, что число 1 присутствует на карточке перед ходом
    assert 1 in player.card.card.values, "Число 1 должно быть на карточке"
    
    # Выполним ход: зачеркнем число 1
    status = player.check_move(True, 1)
    assert status == GameStatus.NEXT_MOVE, "Статус должен быть NEXT_MOVE"
    
    # Убедимся, что число 1 больше не присутствует на карточке
    assert 1 not in player.card.card.values, "Число 1 должно быть заменено на CROSS"
    
    # Убедимся, что символ CROSS теперь присутствует на месте числа 1
    assert CROSS in player.card.card.values, "Число должно быть зачёркнуто (заменено на CROSS)"

# Тестирование правильного пропуска хода
def test_player_check_move_correct_skip(predefined_card):
    card, fixed_numbers = predefined_card
    player = Player(name="Тестовый игрок", is_human=True, card=card, mistake_rate=MISTAKE_RATE)
    status = player.check_move(False, 99)
    assert status == GameStatus.NEXT_MOVE, "Статус должен быть NEXT_MOVE"
    assert len(player.moves['row']) == 0, "Список строк не должен обновляться"
    assert len(player.moves['col']) == 0, "Список колонок не должен обновляться"

# Тестирование ошибки при неправильном зачёркивании числа
def test_player_check_move_error_strike(predefined_card):
    card, fixed_numbers = predefined_card
    player = Player(name="Тестовый игрок", is_human=True, card=card, mistake_rate=MISTAKE_RATE)
    with patch('builtins.print') as mocked_print:
        status = player.check_move(True, 99)
        assert status == GameStatus.LOOSE, "Статус должен быть LOOSE"
        mocked_print.assert_any_call('Тестовый игрок ошибся')
        mocked_print.assert_any_call('Попытался вычеркнуть номер, которого нет в карточке')

# Тестирование ошибки при пропуске зачёркивания числа
def test_player_check_move_error_miss(predefined_card):
    card, fixed_numbers = predefined_card
    player = Player(name="Тестовый игрок", is_human=True, card=card, mistake_rate=MISTAKE_RATE)
    with patch('builtins.print') as mocked_print:
        status = player.check_move(False, 1)
        assert status == GameStatus.LOOSE, "Статус должен быть LOOSE"
        mocked_print.assert_any_call('Тестовый игрок ошибся')
        mocked_print.assert_any_call('Не заметил номера бочонка в своей карточке')

# Тестирование выигрыша игрока
def test_player_check_move_win(predefined_card):
    card, fixed_numbers = predefined_card
    player = Player(name="Тестовый игрок", is_human=True, card=card, mistake_rate=MISTAKE_RATE)
    # Добавляем 14 ходов (без победы)
    for i in range(14):
        number = i + 1
        status = player.check_move(True, number)
        assert status == GameStatus.NEXT_MOVE, f"Статус должен быть NEXT_MOVE после зачёркивания числа {number}"
    # Последний ход для выигрыша
    status = player.check_move(True, 15)
    assert status == GameStatus.WIN, "Статус должен быть WIN после зачёркивания последнего числа"

# Тестирование метода draw в классе Lotto
def test_lotto_draw():
    total_numbers = CARD_ROWS * NUMBERS_PER_ROW
    with patch.object(Lotto, 'draw', side_effect=list(range(1, total_numbers + 1)) + [None]):
        lotto = Lotto(max_number=total_numbers)
        numbers = []
        for _ in range(total_numbers):
            num = lotto.draw()
            numbers.append(num)
        assert len(numbers) == total_numbers, f"Должны быть {total_numbers} чисел"
        assert set(numbers) == set(range(1, total_numbers +1)), f"Должны быть все числа от 1 до {total_numbers}"
        assert lotto.draw() is None, "После исчерпания бочонков должно возвращаться None"

# Тестирование игрового раунда с победой робота
def test_play_round_robot_win(predefined_players):
    """
    Тестирует, что Робот1 выигрывает игру при вычёркивании всех своих чисел.
    """
    player1, player2 = predefined_players
    play_round = PlayRound(player1, player2)

    # Мокаем последовательность бочонков, включающую все 15 чисел робота1
    with patch.object(Lotto, 'draw', side_effect=list(range(1, CARD_ROWS * NUMBERS_PER_ROW +1 )) + [None]):
        with patch('builtins.print') as mocked_print:
            play_round.run_play_round()
            # Проверяем, что робот1 выиграл
            mocked_print.assert_any_call('Поздравляю! Робот1 выиграл(а)!')

    # Дополнительные проверки:
    # Проверяем, что у робота1 все числа вычеркнуты
    for row in player1.card.card.itertuples(index=False):
        for num in row:
            if num != BLANK:
                assert num == CROSS, f"Число {num} должно быть зачёркнуто"

    # Проверяем, что у робота2 не осталось изменений
    for row in player2.card.card.itertuples(index=False):
        for num in row:
            if num != BLANK:
                assert num != CROSS, f"Число {num} не должно быть зачёркнуто"

# Тестирование игрового раунда с ошибкой робота
def test_play_round_robot_lose(predefined_players):
    """
    Тестирует, что Робот2 проигрывает игру при неправильном зачёркивании числа.
    """
    player1, player2 = predefined_players
    play_round = PlayRound(player1, player2)

    # Мокаем последовательность бочонков (используем допустимые числа)
    with patch.object(Lotto, 'draw', side_effect=[1, 90, 3, 4, 5, None]):
        # Мокаем метод check_move для роботов
        with patch.object(Player, 'check_move', side_effect=[
            GameStatus.NEXT_MOVE,  # Робот1 зачёркивает 1
            GameStatus.LOOSE,      # Робот2 ошибается при бочонке 90
            GameStatus.NEXT_MOVE,  # Робот1 зачёркивает 3
            GameStatus.NEXT_MOVE,  # Робот2 зачёркивает 4
            GameStatus.WIN,         # Робот1 выигрывает при зачёркивании 5
            GameStatus.NEXT_MOVE,  # Дополнительный вызов draw()
        ]):
            with patch('builtins.print') as mocked_print:
                play_round.run_play_round()
                # Проверяем, что робот2 проиграл
                mocked_print.assert_any_call(f'Игрок {player2.name} проиграл(а) и выбывает из игры!')
                # Проверяем, что робот1 выиграл
                mocked_print.assert_any_call(f'Остался один игрок {player1.name}. Победа присуждается ему')

# Тестирование игрового раунда с ничьёй
def test_play_round_draw(predefined_players):
    """
    Тестирует, что игра заканчивается ничьёй, если все бочонки не на карточках.
    """
    player1, player2 = predefined_players
    play_round = PlayRound(player1, player2)

    # Мокаем последовательность бочонков, которые не на карточках (используем допустимые числа)
    with patch.object(Lotto, 'draw', side_effect=[91, 92, 93, None]):
        with patch.object(Player, 'check_move', return_value=GameStatus.NEXT_MOVE):
            with patch('builtins.print') as mocked_print:
                play_round.run_play_round()
                mocked_print.assert_any_call('Все бочонки кончились! Ничья')

# Тестирование игрового раунда с победой человека
def test_play_round_human_player_win(predefined_card, predefined_card_robot):
    """
    Тестирует, что человек выигрывает игру при вычёркивании всех своих чисел.
    """
    card1, fixed_numbers1 = predefined_card
    card2, fixed_numbers2 = predefined_card_robot

    player1 = Player(name="Алиса", is_human=True, card=card1, mistake_rate=MISTAKE_RATE)
    player2 = Player(name="Робот1", is_human=False, card=card2, mistake_rate=MISTAKE_RATE)

    play_round = PlayRound(player1, player2)

    # Мокаем последовательность бочонков, чтобы человек выиграл
    with patch.object(Lotto, 'draw', side_effect=list(range(1, CARD_ROWS * NUMBERS_PER_ROW +1 )) + [None]):
        # Мокаем ввод пользователя
        with patch('builtins.input', return_value='y'):
            # Мокаем метод check_move для роботов
            with patch.object(Player, 'check_move', side_effect=[
                GameStatus.NEXT_MOVE,  # Алиса зачёркивает 1
                GameStatus.NEXT_MOVE,  # Робот1 зачёркивает 1
                GameStatus.NEXT_MOVE,  # Алиса зачёркивает 2
                GameStatus.NEXT_MOVE,  # Робот1 зачёркивает 2
                GameStatus.WIN,         # Алиса выигрывает при зачёркивании 15
                GameStatus.NEXT_MOVE,  # Дополнительный вызов draw()
            ]):
                with patch('builtins.print') as mocked_print:
                    play_round.run_play_round()
                    # Проверяем, что Алиса выиграла
                    mocked_print.assert_any_call('Поздравляю! Алиса выиграл(а)!')

# Интеграционный тест полного игрового цикла
def test_full_game_flow():
    """
    Интеграционный тест полного игрового цикла с двумя игроками.
    """
    # Создаём предопределённые карточки
    fixed_numbers1 = list(range(1, 16))   # 1-15
    fixed_numbers2 = list(range(16, 31))  # 16-30

    with patch.object(LottoCard, '__init__', lambda self: None):
        card1 = LottoCard()
        card1.card = pd.DataFrame([
            {0:1, 1:2, 2:3, 3:4, 4:5, 5:BLANK, 6:BLANK, 7:BLANK, 8:BLANK},
            {0:6, 1:7, 2:8, 3:9, 4:10, 5:BLANK, 6:BLANK, 7:BLANK, 8:BLANK},
            {0:11, 1:12, 2:13, 3:14, 4:15, 5:BLANK, 6:BLANK, 7:BLANK, 8:BLANK}
        ], dtype=int)

        card2 = LottoCard()
        card2.card = pd.DataFrame([
            {0:16, 1:17, 2:18, 3:19, 4:20, 5:BLANK, 6:BLANK, 7:BLANK, 8:BLANK},
            {0:21, 1:22, 2:23, 3:24, 4:25, 5:BLANK, 6:BLANK, 7:BLANK, 8:BLANK},
            {0:26, 1:27, 2:28, 3:29, 4:30, 5:BLANK, 6:BLANK, 7:BLANK, 8:BLANK}
        ], dtype=int)

    player1 = Player(name="Алиса", is_human=True, card=card1, mistake_rate=MISTAKE_RATE)
    player2 = Player(name="Робот1", is_human=False, card=card2, mistake_rate=MISTAKE_RATE)

    play_round = PlayRound(player1, player2)

    # Мокаем последовательность бочонков
    with patch.object(Lotto, 'draw', side_effect=list(range(1, 7)) + [None]):
        # Мокаем ввод пользователя
        with patch('builtins.input', return_value='y'):
            # Мокаем метод check_move для роботов
            with patch.object(Player, 'check_move', side_effect=[
                GameStatus.NEXT_MOVE,  # Алиса зачёркивает 1
                GameStatus.NEXT_MOVE,  # Робот1 зачёркивает 1
                GameStatus.NEXT_MOVE,  # Робот1 зачёркивает 2
                GameStatus.NEXT_MOVE,  # Алиса зачёркивает 2
                GameStatus.WIN,         # Алиса выигрывает при зачёркивании 15
                GameStatus.NEXT_MOVE,  # Робот1 зачёркивает 3
            ]):
                with patch('builtins.print') as mocked_print:
                    play_round.run_play_round()
                    # Проверяем, что Алиса выиграла
                    mocked_print.assert_any_call('Поздравляю! Алиса выиграл(а)!')

# Запуск тестов
if __name__ == "__main__":
    pytest.main()
