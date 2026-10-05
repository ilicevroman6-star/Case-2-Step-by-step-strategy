# Монополия на льду

Пошаговая стратегия на 4 игроков: менеджеры хоккейных клубов набирают
очки престижа, покупают арены, тренируют выносливость, проходят
допинг-контроль и участвуют в трансферах. Побеждает тот, кто первым
наберёт **30 очков престижа** (или лидирует по ним на момент завершения круга).

- Движок: Python 3.11+ + Pygame 2.x
- Разрешение окна: 1280×720
- Состояние: 19 экранов UI (S01–S19), конечный автомат `app_state`

---

## Стек и требования

| Компонент | Версия | Примечание |
|---|---|---|
| Python | 3.11 и выше | проверено на 3.13.7 |
| pygame | 2.5+ | графика и события |
| ОС | Windows / Linux / macOS | тестировалось на Windows 10/11 |

Шрифты интерфейса — **Oswald** (заголовки) и **Inter** (текст).
Если `.ttf`-файлов нет в `assets/fonts/`, тема автоматически откатится
на системный `Arial` — игра запустится, но вёрстка будет «не по макету».

---

## Структура проекта

```
PythonProject16/
├── main.py                     # точка входа: роутер состояний
├── README.md
├── requirements.txt
├── assets/
│   └── fonts/
│       ├── oswald.ttf
│       └── inter.ttf
└── game/
    ├── config.py               # палитра, шрифты, параметры доски
    ├── logic/
    │   ├── game_state.py       # генератор хода take_turn()
    │   └── events_pool.py      # пул событий/карточек
    ├── models/
    │   ├── player.py           # Player: ресурсы, флаги состояния
    │   ├── action.py
    │   └── event.py
    ├── ui/
    │   ├── theme.py            # кэш шрифтов, тени, свечения
    │   ├── button.py           # кнопка с состояниями active/disabled/...
    │   ├── panel.py
    │   ├── event_modal.py      # модальные окна S06–S16
    │   ├── widgets.py          # мини-виджеты: пилюля ресурса, прогресс-бар
    │   ├── board_view.py       # доска 8×8, 28 клеток по периметру
    │   ├── player_card.py      # карточка игрока
    │   └── screens/
    │       ├── base_screen.py  # интерфейс экрана
    │       ├── main_menu.py    # S01
    │       ├── game_board.py   # S04 — основной экран партии
    │       └── victory.py      # S19
    └── tests/
        ├── test_logic.py
        └── test_plan.md
```

---

## Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/ilicevroman6-star/Case-2-Step-by-step-strategy.git
cd Case-2-Step-by-step-strategy
```

### 2. Виртуальное окружение

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (cmd):**
```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Зависимости

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Если `requirements.txt` ещё нет — создайте со строкой:
```
pygame>=2.5.0
```

или установите вручную:
```bash
pip install pygame
```

### 4. Шрифты (опционально, но рекомендуется)

Скачайте и положите в `assets/fonts/`:

- **Oswald** → https://fonts.google.com/specimen/Oswald (`oswald.ttf`)
- **Inter** → https://fonts.google.com/specimen/Inter (`inter.ttf`)

Без них игра запустится на Arial — все тексты отобразятся, но
заголовки не будут набраны «капителью», как в макете.

---

## Запуск

### Через PyCharm

1. Откройте проект.
2. **File → Settings → Project → Python Interpreter → Add Interpreter → Select existing**.
3. Укажите путь к уже существующему окружению:
   ```
   <проект>\.venv\Scripts\python.exe
   ```
4. Убедитесь, что `pygame` виден в списке пакетов интерпретатора.
5. Правый клик по `main.py` → **Run 'main'**.

### Через терминал

Из корня проекта:

```bash
python main.py
```

или как модуль (если `game/` — пакет с `__init__.py`):

```bash
python -m game.main
```

### Ожидаемое поведение

- Открывается окно 1280×720 с заголовком «Монополия на льду v1.1».
- Стартовый экран — **S01 · Главное меню** с двумя кнопками.
- «Новая игра» → **S04 · Поле**: доска 8×8, 4 карточки игроков по углам,
  кнопка «🎲 Бросить кости» внизу по центру.
- Клик по кнопке → запускается генератор хода, последовательно открываются
  модалки S06 / S08–S16.
- Победа: кто-то набрал 30 престижа после доигранного круга → экран S19.

---

## Управление

| Действие | Кнопка |
|---|---|
| Совершить ход | ЛКМ по «🎲 Бросить кости» |
| Выбор в модалке | ЛКМ по кнопке активного состояния |
| Выход | Крестик ОС либо `Esc` на экране S19 |

---

## Устранение неполадок

**`ImportError: cannot import name 'BOARD_CELLS' from 'game.config'`**
В `game/config.py` отсутствует константа. Добавьте:
```python
BOARD_CELLS = 8
```

**`AttributeError: 'NoneType' object has no attribute 'send'`**
Модальное окно осталось висеть после `StopIteration`. Проверьте,
что `_modal_click` и `_finish_turn` в `game/ui/screens/game_board.py`
сбрасывают `self.current_modal = None` до вызова `.send()`.

**`ValueError: not enough values to unpack (expected 3, got 2)`**
Генератор `take_turn()` yield'ит 2 значения, а UI ждёт 3. Используйте
хелпер `_next_step()` в `GameBoardScreen`, который принимает оба формата.

**Кнопка «Бросить кости» не видна / уехала под экран**
В `__init__` у `roll_btn` координата `y` + высота должны быть
`<= 720`. При `board_size=540` безопасное значение `y=640, h=44`.

**На доске под фишками видны полупрозрачные пятна**
Функция `glow_circle` в `game/ui/theme.py` использует
`BLEND_PREMULTIPLIED` при недомноженной альфе. Уберите
`special_flags` в `blit` — альфа-композит pygame сработает сам.

**PyCharm: «Environment .venv already exists in the specified folder»**
В диалоге Add Interpreter выберите **Select existing** и укажите
`<проект>\.venv\Scripts\python.exe` вместо создания нового.

**Чёрный экран / окно не открывается**
Проверьте, что pygame видит видео-драйвер:
```bash
python -c "import pygame; pygame.init(); print(pygame.display.get_driver())"
```
На сервере без X11 может понадобиться `SDL_VIDEODRIVER=dummy` для тестов,
но не для интерактивной игры.

---

## Тесты

```bash
python -m pytest game/tests/
```

Файл `test_plan.md` описывает ручной чек-лист сценариев (проверка
модалок, цепочки ходов, победы после доигранного круга).

---

## Соглашения разработки

- **UI = данные + отрисовка.** Никакая логика игры не живёт в `ui/`.
  Логика хода — только в `game/logic/game_state.py`.
- **Модалка закрывается первой.** Если в обработчике кнопки есть
  шанс получить `StopIteration`, ставьте `self.current_modal = None`
  **до** `next()/send()`.
- **Один экран — один класс.** Каждый экран наследуется от
  `BaseScreen` и реализует `handle_event / update / draw`.
- **Палитра — только из `config.COLORS`.** Хардкод HEX в UI-коде
  запрещён, иначе тема разъедется.
- **Размер доски — из `config.BOARD_CELLS`.** Никаких магических `8`
  в модулях доски.

---

## Лицензия

Учебный проект в рамках кейса «Case-2 · Step-by-step strategy».
Внешние ресурсы: Pygame (LGPL), Oswald и Inter (SIL OFL).