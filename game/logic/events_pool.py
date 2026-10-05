from game.models.event import RandomEvent


# 1. Глобальные события, которые наступают для игрока в начале хода.
GLOBAL_EVENTS = [
    RandomEvent(
        event_id='E1',
        title='Контракт с Лигой',
        pos_effects={'money': 10},
        pos_text=' Лига подписала рекордный контракт, все получают субсидию.',
        neg_effects={'money': -15},
        neg_text=' Рейтинги упали, спонсоры урезали финансирование.',
    ),
    RandomEvent(
        event_id='E2',
        title='Календарь игр',
        pos_effects={'stamina': 4},
        pos_text=' Клубы имеют удобный календарь игр.',
        neg_effects={'stamina': -7},
        neg_text=(
            'Клубам предстоит неделя плотных матчей, '
            'которые идут друг за другом.'
        ),
    ),
    RandomEvent(
        event_id='E3',
        title='Активность фанатов',
        pos_effects={'reputation': 3},
        pos_text=(
            ' Каникулярная неделя позволяет болельщикам '
            'посещать больше матчей.'
        ),
        neg_effects={'reputation': -2},
        neg_text=(
            ' Несколько поражений подряд отбили желание '
            'некоторых болельщиков ходить на матчи.'
        ),
    ),
    RandomEvent(
        event_id='E4',
        title='Налоги и перелеты',
        pos_effects={'money': 6},
        pos_text='✈ Компании партнеры согласились оплатить перелет команде.',
        neg_effects={'rent_multiplier': 2},
        neg_text=(
            ' В стране подорожали услуги авиакомпаний '
            'из-за введения новых налогов.'
        ),
    ),
    RandomEvent(
        event_id='E5',
        title='Международная деятельность',
        pos_effects={'money': 5, 'reputation': 2},
        pos_text=(
            ' Лига подписала новый договор о сотрудничестве '
            'между странами по развитию спорта.'
        ),
        neg_effects={'money': -3, 'reputation': -3},
        neg_text=' Лига разорвала контракт с иностранной компанией.',
    ),
    RandomEvent(
        event_id='E6',
        title='Допинг комитет',
        pos_effects={'money': -12},
        pos_text=(
            'Приехали требовательные инспекторы. '
            'Цена честной проверки 12 денежных единиц.'
        ),
        neg_effects={'reputation': -3},
        neg_text=(
            'При выборе Темной проверки игрок теряет 3 репутации, '
            'потому что глава допинг комитета в отставке.'
        ),
    ),
    RandomEvent(
        event_id='E7',
        title='Билетная программа',
        pos_effects={'arena_price_modifier': -4},  # Уменьшение цены (умная система)
        pos_text=(
            'Ввели умную систему продажи билетов '
            '(Цена арены уменьшилась на 4 единицы).'
        ),
        neg_effects={'arena_price_modifier': 4},  # Увеличение цены
        neg_text=(
            'Продажа билетов сократилась '
            '(Цена арены увеличилась на 4 единицы).'
        ),
    ),
    RandomEvent(
        event_id='E8',
        title='Маркетинговая кампания',
        pos_effects={'money': 5, 'reputation': 4},
        pos_text=' Продажи атрибутики резко выросли.',
        neg_effects={'money': -4, 'reputation': -2},
        neg_text='☹︎ Фабрика товаров атрибутики завезла много брака.',
    ),
]

# 2. Локальные события на клетках random — ПОЛОЖИТЕЛЬНЫЕ (A1–A10).
RANDOM_POSITIVE = [
    RandomEvent(
        event_id='A1',
        title='Трансфер',
        pos_effects={'money': 8},
        pos_text=' Другой клуб выкупил вашего игрока.',
    ),
    RandomEvent(
        event_id='A2',
        title='Матч Звезд',
        pos_effects={'reputation': 3},
        pos_text='️ На вашей арене провели событие года.',
    ),
    RandomEvent(
        event_id='A3',
        title='Благотворительный аукцион',
        pos_effects={'money': 5},
        pos_text=' Клуб успешно продал ретро джерси.',
    ),
    RandomEvent(
        event_id='A4',
        title='Молодежка',
        pos_effects={'stamina': 3},
        pos_text=' Из молодежной команды пришел талантливый игрок.',
    ),
    RandomEvent(
        event_id='A5',
        title='Губернаторский грант',
        pos_effects={'money': 10},
        pos_text=(
            '🏛 За вклад в развитие регионального спорта '
            'вам выплатили 10 денежных единиц.'
        ),
    ),
    RandomEvent(
        event_id='A6',
        title='Аншлаг',
        pos_effects={'reputation': 4},
        pos_text='🏟 Клуб собрал аншлаг на предсезонном матче.',
    ),
    RandomEvent(
        event_id='A7',
        title='Маскот',
        pos_effects={'reputation': 1},
        pos_text=' Новый клубный маскот привлек болельщиков.',
    ),
    RandomEvent(
        event_id='A8',
        title='Сотрудничество',
        pos_effects={'money': 4},
        pos_text=' Киносервис продлил с вами сотрудничество.',
    ),
    RandomEvent(
        event_id='A9',
        title='Новое оборудование',
        pos_effects={'stamina': 3},
        pos_text=' В термальных зонах установили еще одну сауну.',
    ),
    RandomEvent(
        event_id='A10',
        title='Удача',
        pos_effects={'stamina': 2, 'reputation': 2},
        pos_text=' Команда поймала кураж.',
    ),
]


# 2. Локальные события на клетках random — ОТРИЦАТЕЛЬНЫЕ (B1–B10).
RANDOM_NEGATIVE = [
    RandomEvent(
        event_id='B1',
        title='Лишение имущества за долги',
        neg_effects={'action_type': 'lose_random_arena'},
        neg_text=' Вы задолжали банку. Отбирается 1 арена, случайно.',
    ),
    RandomEvent(
        event_id='B2',
        title='Драка на трибунах',
        neg_effects={'money': -3, 'reputation': -3},
        neg_text=(
            ' Фанаты вашего клуба устроили потасовку с гостями. '
            'Клуб оштрафован Лигой.'
        ),
    ),
    RandomEvent(
        event_id='B3',
        title='Поломка автобуса команды',
        neg_effects={'stamina': -2},
        neg_text=' Команде пришлось добираться своим ходом.',
    ),
    RandomEvent(
        event_id='B4',
        title='Компенсация трансфера',
        neg_effects={'money': -7},
        neg_text=' Вы нарушили условия проведения сделки.',
    ),
    RandomEvent(
        event_id='B5',
        title='Тренировка',
        neg_effects={'stamina': -3},
        neg_text=' Тренер провел интенсивную тренировку.',
    ),
    RandomEvent(
        event_id='B6',
        title='Срыв предматчевого шоу',
        neg_effects={'reputation': -2},
        neg_text=(
            ' Из-за проблем с техническим оборудованием '
            'шоу пришлось отменить.'
        ),
    ),
    RandomEvent(
        event_id='B7',
        title='Интервью',
        neg_effects={'reputation': -2},
        neg_text=' Капитан команды дал скандальное интервью.',
    ),
    RandomEvent(
        event_id='B8',
        title='Штраф',
        neg_effects={'money': -3},
        neg_text=' Лига оштрафовала клуб на 3 денежных единицы.',
    ),
    RandomEvent(
        event_id='B9',
        title='Вирус',
        neg_effects={'stamina': -3},
        neg_text=' Полкоманды заболело.',
    ),
    RandomEvent(
        event_id='B10',
        title='Судебное дело',
        neg_effects={'money': -6},
        neg_text=(
            '️ Клуб проиграл судебное дело и должен '
            'выплатить 6 денежных единиц.'
        ),
    ),
]


# Обратная совместимость: если где-то ещё импортируется старый список,
# он соберётся из двух частей. Новый код должен импортировать
# RANDOM_POSITIVE / RANDOM_NEGATIVE напрямую.
RANDOM_TILE_EVENTS = RANDOM_POSITIVE + RANDOM_NEGATIVE

# 3. Локальные события на клетках медиа.
MEDIA_POSITIVE = [
    RandomEvent('C1', 'Автограф-сессия',
        pos_effects={'reputation': 2},
        pos_text='Клуб провёл автограф-сессию, собрав огромную очередь фанатов.'),
    RandomEvent('C2', 'Сбор средств',
        pos_effects={'reputation': 1},
        pos_text='Клуб запустил сбор средств на экипировку для детской школы.'),
    RandomEvent('C3', 'Подарок клюшки',
        pos_effects={'reputation': 1},
        pos_text='Капитан подарил клюшку юному болельщику, фото в СМИ.'),
    RandomEvent('C4', 'Ролик из раздевалки',
        pos_effects={'reputation': 3},
        pos_text='Ролик после победы залетел в тренды.'),
    RandomEvent('C5', 'Хоккейное шоу',
        pos_effects={'reputation': 2},
        pos_text='Снайпер пришёл на шоу и поднял популярность клуба.'),
]

MEDIA_NEGATIVE = [
    RandomEvent('C6', 'Слухи о ссоре',
        neg_effects={'reputation': -2},
        neg_text='Анонимный канал опубликовал слух о ссоре в раздевалке.'),
    RandomEvent('C7', 'Грубый ответ',
        neg_effects={'reputation': -1},
        neg_text='Защитник грубо ответил журналисту после поражения.'),
    RandomEvent('C8', 'Игнорирование фанатов',
        neg_effects={'reputation': -2},
        neg_text='Хоккеисты молча уехали со стадиона, не пообщавшись с фанатами.'),
    RandomEvent('C9', 'Двусмысленный мем',
        neg_effects={'reputation': -1},
        neg_text='Пресс-служба выложила мем, спровоцировавший волну хейта.'),
    RandomEvent('C10', 'Критика эксперта',
        neg_effects={'reputation': -2},
        neg_text='Эксперт разнёс тактику команды в прямом эфире.'),
]

# Для обратной совместимости (если что-то ещё импортирует старый список)
MEDIA_TILE_EVENTS = MEDIA_POSITIVE + MEDIA_NEGATIVE