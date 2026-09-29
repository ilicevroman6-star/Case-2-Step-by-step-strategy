from game.models.event import RandomEvent
import random


# 1. Глобальные события, которые наступают для игрока в начале хода.
def contract(player, positive):
    if positive:
        player.money += 10
        return '💸 Лига подписала рекордный контракт, все получают субсидию.'
    else:
        player.money -= 15
        return '📉 Рейтинги упали, спонсоры урезали финансирование.'

def game_calendar(player, positive):
    if positive:
        player.stamina += 4
        return '😋 Клубы имеют удобный календарь игр.'
    else:
        player.stamina -= 7
        return '🫪 Клубам предстоит неделя плотных матчей, которые идут друг за другом.'

def fan_activity(player, positive):
    if positive:
        player.reputation += 3
        return '🥳 Каникулярная неделя позволяет болельщикам посещать больше матчей.'
    else:
        player.reputation -= 2
        return '😔 Несколько поражений подряд отбили желание некоторых болельщиков ходить на матчи.'

def taxes(player, positive):
    if positive:
        player.money += 6
        return '✈️ Компании партнеры согласились оплатить перелет команде.'
    else:
        player.rent *= 2
        return '💵 В стране подорожали услуги авиакомпаний из за введения новых налогов.'

def abroad_activity(player, positive):
    if positive:
        player.money += 5
        player.reputation += 2
        return '🌐 Лига подписала новый договор о сотрудничестве между странами по развитию спорта.'
    else:
        player.money -= 3
        player.reputation -= 3
        return '❌ Лига разорвала контракт с иностранной компанией.'

def marketing(player, positive):
    if positive:
        player.money += 5
        player.reputation += 4
        return '📈 Продажи атрибутики резко выросли.'
    else:
        player.money -= 4
        player.reputation -= 2
        return '☹︎ Фабрика товаров атрибутики завезла много брака.'

EVENTS_POOL = [
    RandomEvent(
        id="contract",
        title="Контракт с Лигой",
        apply_func=contract
    ),
    RandomEvent(
        id="game_calendar",
        title="Календарь игр",
        apply_func=game_calendar
    ),
    RandomEvent(
        id="fan_activity",
        title="Активность фанатов",
        apply_func=fan_activity
    ),
    RandomEvent(
        id="taxes",
        title="Налоги и перелеты",
        apply_func=taxes
    ),
    RandomEvent(
        id="abroad_activity",
        title="Международная деятельность",
        apply_func=abroad_activity
    ),
    RandomEvent(
        id="marketing",
        title="Маркетинговая кампания",
        apply_func=marketing
    )
]

# 2. Локальные события на клетках random.
def transfer(player, positive):
    player.money += 8
    return '💸 Другой клуб выкупил вашего игрока.'

def star_game(player, positive):
    player.reputation += 3
    return '⭐️ На вашей арене провели событие года.'

def charity_auction(player, positive):
    player.money += 5
    return '👕 Клуб успешно продал ретро джерси.'

def youngsters(player, positive):
    player.stamina += 3
    return '🧒 Из молодежной команды пришел талантливый игрок.'

def gov_grant(player, positive):
    player.money += 10
    return '🏛️ За вклад в развитие регионального спорта вам выплатили 10 денежных единиц.'

def full_house(player, positive):
    player.reputation += 3
    return '🏟️ Клуб собрал аншлаг на предсезонном матче.'

def mascot(player, positive):
    player.reputation += 1
    return '🦊 Новый клубный маскот привлек болельщиков.'

def cooperation(player, positive):
    player.money += 4
    return '🎬 Киносервис продлил с вами сотрудничество.'

def new_equipment(player, positive):
    player.stamina += 3
    return '🧖 В термальных зонах установили еще одну сауну.'

def good_luck(player, positive):
    player.stamina += 2
    player.reputation += 2
    return '🔥 Команда поймала кураж.'

def asset_loss(player, positive):
    # Проверяем, есть ли у игрока вообще выкупленные арены.
    if getattr(player, 'owned_arenas', []):
        # Случайно выбираем одну из его арен и удаляем её из списка владения.
        lost_arena_id = random.choice(player.owned_arenas)
        player.owned_arenas.remove(lost_arena_id)
        return f'🏦 Вы задолжали банку. Отбирается арена №{lost_arena_id}.'
    else:
        # Альтернативный сценарий на случай, если арен для изъятия нет.
        player.money = max(0, player.money - 10)
        return '🏦 Вы задолжали банку. Так как у вас нет арен, банк списал штраф 10 монет.'

def stadium_brawl(player, positive):
    player.money -= 3
    player.reputation -= 3
    return '👊 Фанаты вашего клуба устроили потасовку с гостями. Клуб оштрафован Лигой.'

def bus_breakdown(player, positive):
    player.stamina -= 2
    return '🚌 Команде пришлось добираться своим ходом.'

def transfer_compensation(player, positive):
    player.money -= 7
    return '📜 Вы нарушили условия проведения сделки.'

def intense_training(player, positive):
    player.stamina -= 3
    return '🏋️ Тренер провел интенсивную тренировку.'

def show_cancellation(player, positive):
    player.reputation -= 2
    return '❌ Из-за проблем с техническим оборудованием шоу пришлось отменить.'

def interview(player, positive):
    player.reputation -= 2
    return '📢 Капитан команды дал скандальное интервью.'

def fine(player, positive):
    player.money -= 3
    return '📉 Лига оштрафовала клуб на 3 денежных единицы.'

def virus(player, positive):
    player.stamina -= 3
    return '🦠 Половина команды заболела.'

def lawsuit(player, positive):
    player.money -= 6
    return '⚖️ Клуб проиграл судебное дело и должен выплатить 6 денежных единиц.'

RANDOM_TILE_EVENTS = [
    RandomEvent(id="A1", title="Трансфер", apply_func=transfer),
    RandomEvent(id="A2", title="Матч Звезд", apply_func=star_game),
    RandomEvent(id="A3", title="Благотворительный аукцион", apply_func=charity_auction),
    RandomEvent(id="A4", title="Молодежка", apply_func=youngsters),
    RandomEvent(id="A5", title="Губернаторский грант", apply_func=gov_grant),
    RandomEvent(id="A6", title="Аншлаг", apply_func=full_house),
    RandomEvent(id="A7", title="Маскот", apply_func=mascot),
    RandomEvent(id="A8", title="Сотрудничество", apply_func=cooperation),
    RandomEvent(id="A9", title="Новое оборудование", apply_func=new_equipment),
    RandomEvent(id="A10", title="Удача", apply_func=good_luck),
    RandomEvent(id="B1", title="Лишение имущества за долги", apply_func=asset_loss),
    RandomEvent(id="B2", title="Драка на трибунах", apply_func=stadium_brawl),
    RandomEvent(id="B3", title="Поломка автобуса команды", apply_func=bus_breakdown),
    RandomEvent(id="B4", title="Компенсация трансфера", apply_func=transfer_compensation),
    RandomEvent(id="B5", title="Тренировка", apply_func=intense_training),
    RandomEvent(id="B6", title="Срыв предматчевого шоу", apply_func=show_cancellation),
    RandomEvent(id="B7", title="Интервью", apply_func=interview),
    RandomEvent(id="B8", title="Штраф", apply_func=fine),
    RandomEvent(id="B9", title="Вирус", apply_func=virus),
    RandomEvent(id="B10", title="Судебное дело", apply_func=lawsuit),
]

# 3. Локальные события на клетках медиа.
def autograph_session(player, positive):
    player.reputation += 2
    return '✍️ Клуб провел автограф-сессию, собрав огромную очередь фанатов.'

def fundraising(player, positive):
    player.reputation += 1
    return '🎒 Клуб запустил сбор средств на экипировку для детской спортивной школы. Пресса хвалит команду.'

def stick_gift(player, positive):
    player.reputation += 1
    return '🏒 Капитан вашей команды подарил свою клюшку юному болельщику на трибуне, фото разлетелось по крупным СМИ.'

def locker_room_video(player, positive):
    player.reputation += 3
    return '📹 Медиа-служба сняла ролик из раздевалки после победы, который залетел в тренды.'

def show_appearance(player, positive):
    player.reputation += 2
    return '📺 Ваш снайпер пришел на популярное хоккейное шоу и помог набрать популярность.'

def rumor_leak(player, positive):
    player.reputation -= 2
    return '🤫 Анонимный медиа-канал опубликовал слух о жесткой ссоре в раздевалке между тренером и игроками.'

def rude_response(player, positive):
    player.reputation -= 1
    return '🤬 Защитник вашей команды на эмоциях грубо ответил журналисту после поражения.'

def fans_ignore(player, positive):
    player.reputation -= 2
    return '🚌 После проигранного домашнего матча хоккеисты молча уехали со стадиона, отказавшись общаться с фан-сектором.'

def controversial_meme(player, positive):
    player.reputation -= 1
    return '📱 Пресс-служба клуба выложила в соцсети двусмысленный мем, который спровоцировал волну хейта.'

def boring_tactics(player, positive):
    player.reputation -= 2
    return '📺 Известный в прошлом хоккейный эксперт разнес тактику вашей команды в прямом эфире, назвав вашу игру «унылым автобусом».'

MEDIA_TILE_EVENTS = [
    RandomEvent(id="C1", title="Автограф-сессия", apply_func=autograph_session),
    RandomEvent(id="C2", title="Сбор средств", apply_func=fundraising),
    RandomEvent(id="C3", title="Подарок клюшки", apply_func=stick_gift),
    RandomEvent(id="C4", title="Ролик из раздевалки", apply_func=locker_room_video),
    RandomEvent(id="C5", title="Хоккейное шоу", apply_func=show_appearance),
    RandomEvent(id="C6", title="Слухи о ссоре", apply_func=rumor_leak),
    RandomEvent(id="C7", title="Грубый ответ", apply_func=rude_response),
    RandomEvent(id="C8", title="Игнорирование фанатов", apply_func=fans_ignore),
    RandomEvent(id="C9", title="Двусмысленный мем", apply_func=controversial_meme),
    RandomEvent(id="C10", title="Критика эксперта", apply_func=boring_tactics)
]