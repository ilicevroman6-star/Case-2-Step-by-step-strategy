from game.models.event import RandomEvent


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