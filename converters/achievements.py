import re
from converters import content
from src import create_app
from src.model.models import User, Achievement, AchievementUser


old_ach = """
{if $oUserProfile->getDisplayName() == 'Hrenzerg'}<img src="/common/templates/skin/start-kit/assets/images/achi_nakolennik1_first_place.png" title="За победу в Наколеннике №01">{/if}
{if $oUserProfile->getDisplayName() == 'Hrenzerg'}<img src="/common/templates/skin/start-kit/assets/images/achi_nakolennik1.png" title="За участие в Наколеннике №01">{/if}
{if $oUserProfile->getDisplayName() == 'Snuux'}<img src="/common/templates/skin/start-kit/assets/images/achi_nakolennik1.png" title="За участие в Наколеннике №01">{/if}
{if $oUserProfile->getDisplayName() == 'Tetsuwan'}<img src="/common/templates/skin/start-kit/assets/images/achi_nakolennik1.png" title="За участие в Наколеннике №01">{/if}
{if $oUserProfile->getDisplayName() == 'TheDreik'}<img src="/common/templates/skin/start-kit/assets/images/achi_nakolennik1.png" title="За участие в Наколеннике №01">{/if}
{if $oUserProfile->getDisplayName() == 'Мурка'}<img src="/common/templates/skin/start-kit/assets/images/achi_nakolennik1.png" title="За участие в Наколеннике №01">{/if}
{if $oUserProfile->getDisplayName() == 'Arlekin'}<img src="/common/templates/skin/start-kit/assets/images/achi_nakolennik2_first_place.png" title="За победу в Наколеннике №02">{/if}
{if $oUserProfile->getDisplayName() == 'injir'}<img src="/common/templates/skin/start-kit/assets/images/achi_nakolennik2_first_place.png" title="За победу в Наколеннике №02">{/if}
{if $oUserProfile->getDisplayName() == 'Arlekin'}<img src="/common/templates/skin/start-kit/assets/images/achi_nakolennik2.png" title="За участие в Наколеннике №02">{/if}
{if $oUserProfile->getDisplayName() == 'injir'}<img src="/common/templates/skin/start-kit/assets/images/achi_nakolennik2.png" title="За участие в Наколеннике №02">{/if}
{if $oUserProfile->getDisplayName() == 'andreymust19'}<img src="/common/templates/skin/start-kit/assets/images/achi_nakolennik2.png" title="За участие в Наколеннике №02">{/if}
{if $oUserProfile->getDisplayName() == 'DarkDes'}<img src="/common/templates/skin/start-kit/assets/images/achi_nakolennik2.png" title="За участие в Наколеннике №02">{/if}
{if $oUserProfile->getDisplayName() == 'Rat_on_psilocybin'}<img src="/common/templates/skin/start-kit/assets/images/achi_nakolennik2.png" title="За участие в Наколеннике №02">{/if}
{if $oUserProfile->getDisplayName() == 'razzle_dazzle'}<img src="/common/templates/skin/start-kit/assets/images/achi_nakolennik2.png" title="За участие в Наколеннике №02">{/if}
{if $oUserProfile->getDisplayName() == 'Praron'}<img src="/common/templates/skin/start-kit/assets/images/achi_nakolennik2.png" title="За участие в Наколеннике №02">{/if}
{if $oUserProfile->getDisplayName() == 'Kot211'}<img src="/common/templates/skin/start-kit/assets/images/achi_nakolennik2.png" title="За участие в Наколеннике №02">{/if}
{if $oUserProfile->getDisplayName() == 'DarkDes'}<img src="/common/templates/skin/start-kit/assets/images/achi_nakolennik2.png" title="За участие в Наколеннике №02">{/if}
{if $oUserProfile->getDisplayName() == 'Xitilon'}<img src="/common/templates/skin/start-kit/assets/images/achi_nakolennik2.png" title="За участие в Наколеннике №02">{/if}
{if $oUserProfile->getDisplayName() == 'DarkDes'}<img src="/common/templates/skin/start-kit/assets/images/achi_barraсuda.png" title='За участие в "BARRACUDA — Конкурс чит-кодов!"'>{/if}
{if $oUserProfile->getDisplayName() == 'Xitilon'}<img src="/common/templates/skin/start-kit/assets/images/achi_barraсuda.png" title='За участие в "BARRACUDA — Конкурс чит-кодов!"'>{/if}
{if $oUserProfile->getDisplayName() == 'Raseri'}<img src="/common/templates/skin/start-kit/assets/images/achi_barraсuda.png" title='За участие в "BARRACUDA — Конкурс чит-кодов!"'>{/if}
{if $oUserProfile->getDisplayName() == 'Kozinaka'}<img src="/common/templates/skin/start-kit/assets/images/achi_barraсuda.png" title='За участие в "BARRACUDA — Конкурс чит-кодов!"'>{/if}
{if $oUserProfile->getDisplayName() == 'Raseri'}<img src="/common/templates/skin/start-kit/assets/images/achi_barraсuda_first_place.png" title='За победу в "BARRACUDA — Конкурс чит-кодов!"'>{/if}
{if $oUserProfile->getDisplayName() == 'stray_stoat'}<a href="http://kolenka.su/blog/ps/kuda-ne-uvodyat-mechty.html"><img src="/uploads/images/00/00/13/2015/09/10/0u5b8b2db3-54c46949-283dd710.png" title='Просто слова: лауреат'></a>{/if}
{if $oUserProfile->getDisplayName() == 'yeo'}<a href="http://kolenka.su/blog/ps/kuda-uvodyat-mechty-dzhekson.html/"><img src="/uploads/images/00/00/13/2015/09/10/0u5b8b2db3-54c46949-283dd710.png" title='Просто слова: лауреат'></a>{/if}
{if $oUserProfile->getDisplayName() == 'Cotton'}<a href="http://kolenka.su/blog/ps/i-may-not-be-the-right-one.html"><img src="/uploads/images/00/00/13/2015/09/10/0u5b8b2db3-54c46949-283dd710.png" title='Просто слова: лауреат'></a>{/if}
{if $oUserProfile->getDisplayName() == 'Raseri'}<a href="http://kolenka.su/blog/ps/nastoyashhaya-mechta-dolzhna-byt-neosushhestvimoj-da.html"><img src="/uploads/images/00/00/13/2015/09/10/0u5b8b2db3-54c46949-283dd710.png" title='Просто слова: лауреат'></a>{/if}
{if $oUserProfile->getDisplayName() == 'Kozinaka'}<a href="http://kolenka.su/blog/ps/kogda-ya-v-pervyj-raz-popal-pod-mashinu.html"><img src="/uploads/images/00/00/13/2015/09/10/0u5b8b2db3-54c46949-283dd710.png" title='Просто слова: лауреат'></a>{/if}
{if $oUserProfile->getDisplayName() == 'mylittlekafka'}<a href="http://kolenka.su/blog/ps/dotdotdot.html"><img src="/uploads/images/00/00/13/2015/09/10/0u6b865ba9-54e240da-7508832e.png" title='Просто слова: участник'></a>{/if}
{if $oUserProfile->getDisplayName() == 'DarkDes'}<a href="http://kolenka.su/blog/ps/karl-lavrekin.html"><img src="/uploads/images/00/00/13/2015/09/10/0u6b865ba9-54e240da-7508832e.png" title='Просто слова: участник'></a>{/if}
{if $oUserProfile->getDisplayName() == 'MekaGem'}<a href="http://kolenka.su/blog/ps/muzhik-i-d6.html"><img src="/uploads/images/00/00/13/2015/09/10/0u6b865ba9-54e240da-7508832e.png" title='Просто слова: участник'></a>{/if}
{if $oUserProfile->getDisplayName() == 'NoPlaceForYoungAzat'}<a href="http://kolenka.su/blog/ps/tosty-s-klubnichnym-dzhemom-ili-goluboj-rassvet-na-zolotom-saturne.html"><img src="/uploads/images/00/00/13/2015/09/10/0u6b865ba9-54e240da-7508832e.png" title='Просто слова: участник'></a>{/if}
{if $oUserProfile->getDisplayName() == 'Hrenzerg'}<a href="http://kolenka.su/blog/ps/pyatyj-sentyabr.html"><img src="/uploads/images/00/00/13/2015/09/10/0u6b865ba9-54e240da-7508832e.png" title='Просто слова: участник'></a>{/if}
{if $oUserProfile->getDisplayName() == 'Xitilon'}<a href="http://kolenka.su/blog/ps/fantazyor-dolzhen-sidet-v-mirke-verno.html"><img src="/uploads/images/00/00/13/2015/09/10/0u6b865ba9-54e240da-7508832e.png" title='Просто слова: участник'></a>{/if}
{if $oUserProfile->getDisplayName() == 'Raseri'}<a href="http://kolenka.su/blog/ps/mechta-programmista.html"><img src="/uploads/images/00/00/13/2015/09/10/0u2144adc3-60623fea-247a4656.png" title='Просто слова: выдающийся графоман'></a>{/if}
{if $oUserProfile->getDisplayName() == 'mylittlekafka'}<img src="/common/templates/skin/start-kit/assets/images/zvukolennik1ntp.png" title="Звуколенник №1, победа в номинации «Не всё так просто»">{/if}
{if $oUserProfile->getDisplayName() == 'qb60'}<img src="/common/templates/skin/start-kit/assets/images/zvukolennik1_dolgo.png" title="Звуколенник №1, победа в номинации «Битва будет долгой»">{/if}
{if $oUserProfile->getDisplayName() == 'Xeneder'}<img src="/common/templates/skin/start-kit/assets/images/zvukolennik1_evil.png" title="Звуколенник №1, победа в номинации «Само воплощение зла»">{/if}
{if $oUserProfile->getDisplayName() == 'Cotton'}<img src="/common/templates/skin/start-kit/assets/images/zvukolennik1.png" title="За участие в «Звуколеннике №1»">{/if}
{if $oUserProfile->getDisplayName() == 'mylittlekafka'}<img src="/common/templates/skin/start-kit/assets/images/zvukolennik1.png" title="За участие в «Звуколеннике №1»">{/if}
{if $oUserProfile->getDisplayName() == 'Xitilon'}<img src="/common/templates/skin/start-kit/assets/images/zvukolennik1.png" title="За участие в «Звуколеннике №1»">{/if}
{if $oUserProfile->getDisplayName() == 'qb60'}<img src="/common/templates/skin/start-kit/assets/images/zvukolennik1.png" title="За участие в «Звуколеннике №1»">{/if}
{if $oUserProfile->getDisplayName() == 'Esdeer'}<img src="/common/templates/skin/start-kit/assets/images/zvukolennik1.png" title="За участие в «Звуколеннике №1»">{/if}
{if $oUserProfile->getDisplayName() == 'veloc1'}<img src="/common/templates/skin/start-kit/assets/images/zvukolennik1.png" title="За участие в «Звуколеннике №1»">{/if}
{if $oUserProfile->getDisplayName() == 'mrrk'}<img src="/common/templates/skin/start-kit/assets/images/zvukolennik1.png" title="За участие в «Звуколеннике №1»">{/if}
{if $oUserProfile->getDisplayName() == 'Xeneder'}<img src="/common/templates/skin/start-kit/assets/images/zvukolennik1.png" title="За участие в «Звуколеннике №1»">{/if}
{if $oUserProfile->getDisplayName() == 'DarkDes'}<img src="/common/templates/skin/start-kit/assets/images/zvukolennik1.png" title="За участие в «Звуколеннике №1»">{/if}
{if $oUserProfile->getDisplayName() == 'veloc1'}<img src="/common/templates/skin/start-kit/assets/images/welding_dress.png" title="За многочисленную техническую помощь с сайтом">{/if}
{if $oUserProfile->getDisplayName() == 'f2d'}<img src="/common/templates/skin/start-kit/assets/images/welding_white_bg.png" title="За многочисленную помощь с рисованием для сайта">{/if}
{if $oUserProfile->getDisplayName() == 'pevzi'}<img src="/common/templates/skin/start-kit/assets/images/cup_1_pad.png" title="За первое место в «Чашечке геймдева»">{/if}
{if $oUserProfile->getDisplayName() == 'Xeneder'}<img src="/common/templates/skin/start-kit/assets/images/cup_1_pad.png" title="За второе место в «Чашечке геймдева»">{/if}
{if $oUserProfile->getDisplayName() == 'DarkDes'}<img src="/common/templates/skin/start-kit/assets/images/cup_1_pad.png" title="За третье место в «Чашечке геймдева»">{/if}
{if $oUserProfile->getDisplayName() == 'pevzi'}<img src="/common/templates/skin/start-kit/assets/images/cup_1.png" title="За участие в «Чашечке геймдева»">{/if}
{if $oUserProfile->getDisplayName() == 'Xeneder'}<img src="/common/templates/skin/start-kit/assets/images/cup_1.png" title="За участие в «Чашечке геймдева»">{/if}
{if $oUserProfile->getDisplayName() == 'DarkDes'}<img src="/common/templates/skin/start-kit/assets/images/cup_1.png" title="За участие в «Чашечке геймдева»">{/if}
{if $oUserProfile->getDisplayName() == 'Rs11'}<img src="/common/templates/skin/start-kit/assets/images/cup_1.png" title="За участие в «Чашечке геймдева»">{/if}
{if $oUserProfile->getDisplayName() == 'razzle_dazzle'}<img src="/common/templates/skin/start-kit/assets/images/cup_1.png" title="За участие в «Чашечке геймдева»">{/if}
{if $oUserProfile->getDisplayName() == 'PixelPanda'}<img src="/common/templates/skin/start-kit/assets/images/cup_1.png" title="За участие в «Чашечке геймдева»">{/if}
{if $oUserProfile->getDisplayName() == 'Tetsuwan'}<img src="/common/templates/skin/start-kit/assets/images/cup_1.png" title="За участие в «Чашечке геймдева»">{/if}
{if $oUserProfile->getDisplayName() == '0cd2bdbaac'}<a href="http://kolenka.su/blog/complete_games/grinder.html"><img src="/images/achi/achi_grinder.png" title="grinder Best score"></a>{/if}
{if $oUserProfile->getDisplayName() == 'Oxnard'}<a href="http://kolenka.su/blog/nakolennik03/"><img src="/images/achi/n3_car_v1_front.png" title="За победу в Наколеннике №03"></a>{/if}
{if $oUserProfile->getDisplayName() == 'markertat'}<a href="http://kolenka.su/blog/nakolennik03/"><img src="/images/achi/n3_clock_v5.png" title="За участие в Наколеннике №03"></a>{/if}
{if $oUserProfile->getDisplayName() == 'PixelPanda'}<a href="http://kolenka.su/blog/nakolennik03/"><img src="/images/achi/n3_clock_v1_side.png" title="За участие в Наколеннике №03"></a>{/if}
{if $oUserProfile->getDisplayName() == 'korteh'}<a href="http://kolenka.su/blog/nakolennik03/"><img src="/images/achi/n3_clock_v3.png" title="За участие в Наколеннике №03"></a>{/if}
{if $oUserProfile->getDisplayName() == '711'}<img src="/common/templates/skin/start-kit/assets/images/zv2uch.png" title="За участие в «Звуколеннике №2»">{/if}
{if $oUserProfile->getDisplayName() == 'Хлопчатый призрак'}<img src="/common/templates/skin/start-kit/assets/images/zv2uch.png" title="За участие в «Звуколеннике №2»">{/if}
{if $oUserProfile->getDisplayName() == 'Oxnard'}<img src="/common/templates/skin/start-kit/assets/images/zv2uch.png" title="За участие в «Звуколеннике №2»">{/if}
{if $oUserProfile->getDisplayName() == 'mrrk'}<img src="/common/templates/skin/start-kit/assets/images/zv2uch.png" title="За участие в «Звуколеннике №2»">{/if}
{if $oUserProfile->getDisplayName() == 'DeepestLore'}<img src="/common/templates/skin/start-kit/assets/images/zv2uch.png" title="За участие в «Звуколеннике №2»">{/if}
{if $oUserProfile->getDisplayName() == 'qb60'}<img src="/common/templates/skin/start-kit/assets/images/zv2uch.png" title="За участие в «Звуколеннике №2»">{/if}
{if $oUserProfile->getDisplayName() == 'Talver'}<img src="/common/templates/skin/start-kit/assets/images/zv2uch.png" title="За участие в «Звуколеннике №2»">{/if}
{if $oUserProfile->getDisplayName() == 'hostel_games'}<img src="/common/templates/skin/start-kit/assets/images/zv2uch.png" title="За участие в «Звуколеннике №2»">{/if}
{if $oUserProfile->getDisplayName() == 'LePrianik'}<img src="/common/templates/skin/start-kit/assets/images/zv2uch.png" title="За участие в «Звуколеннике №2»">{/if}
{if $oUserProfile->getDisplayName() == 'mylittlekafka'}<img src="/common/templates/skin/start-kit/assets/images/zv2uch.png" title="За участие в «Звуколеннике №2»">{/if}
{if $oUserProfile->getDisplayName() == 'uwantuwanto'}<img src="/common/templates/skin/start-kit/assets/images/zv2uch.png" title="За участие в «Звуколеннике №2»">{/if}
{if $oUserProfile->getDisplayName() == 'Raseri'}<img src="/common/templates/skin/start-kit/assets/images/zv2uch.png" title="За участие в «Звуколеннике №2»">{/if}
{if $oUserProfile->getDisplayName() == 'Xitilon'}<img src="/common/templates/skin/start-kit/assets/images/zv2uch.png" title="За участие в «Звуколеннике №2»">{/if}
{if $oUserProfile->getDisplayName() == 'Channard'}<img src="/common/templates/skin/start-kit/assets/images/zv2uch.png" title="За участие в «Звуколеннике №2»">{/if}
{if $oUserProfile->getDisplayName() == 'Rs11'}<img src="/common/templates/skin/start-kit/assets/images/zv2uch.png" title="За участие в «Звуколеннике №2»">{/if}
{if $oUserProfile->getDisplayName() == 'InfernalGrape'}<img src="/common/templates/skin/start-kit/assets/images/zv2uch.png" title="За участие в «Звуколеннике №2»">{/if}
{if $oUserProfile->getDisplayName() == '711'}<img src="/common/templates/skin/start-kit/assets/images/zv2winner.png" title="За победу в «Звуколеннике №2»">{/if}
{if $oUserProfile->getDisplayName() == 'Хлопчатый призрак'}<img src="/common/templates/skin/start-kit/assets/images/zv2winner.png" title="За победу в «Звуколеннике №2»">{/if}
{if $oUserProfile->getDisplayName() == 'Oxnard'}<img src="/common/templates/skin/start-kit/assets/images/zv2winner.png" title="За победу в «Звуколеннике №2»">{/if}
{if $oUserProfile->getDisplayName() == 'DeepestLore'}<img src="/common/templates/skin/start-kit/assets/images/zv2choose.png" title="Номинация «Выбор ведущего» в «Звуколеннике №2»">{/if}
{if $oUserProfile->getDisplayName() == 'Хлопчатый призрак'}<img src="/common/templates/skin/start-kit/assets/images/zv2choose.png" title="Номинация «Выбор ведущего» в «Звуколеннике №2»">{/if}
{if $oUserProfile->getDisplayName() == 'qb60'}<img src="/common/templates/skin/start-kit/assets/images/zv2choose.png" title="Номинация «Выбор ведущего» в «Звуколеннике №2»">{/if}
{if $oUserProfile->getDisplayName() == '711'}<img src="/common/templates/skin/start-kit/assets/images/zv2orig.png" title="Номинация «За оригинальность» в «Звуколеннике №2»">{/if}
{if $oUserProfile->getDisplayName() == 'Esdeer'}<img style="display:none;" src="/common/templates/skin/start-kit/assets/images/zv2esdeer.png" title="За то, что песенку свою не стал выкладывать :(">{/if}
{if $oUserProfile->getDisplayName() == 'DarkDes'}<img src="/images/achi/anima11.png" title="Анимаколенник №1, первое место">{/if}
{if $oUserProfile->getDisplayName() == 'Rs11'}<img src="/images/achi/anima22.png" title="Анимаколенник №1, второе место">{/if}
{if $oUserProfile->getDisplayName() == 'Rubel'}<img src="/images/achi/anima33.png" title="Анимаколенник №1, третье место">{/if}
{if $oUserProfile->getDisplayName() == 'mylittlekafka'}<img src="/images/achi/anima44.png" title="Анимаколенник №1, четвёртое место (но в сердце Разери всё равно первое)">{/if}
{if $oUserProfile->getDisplayName() == 'alexmakovsky'}<img src="/images/achi/anima55.png" title="Анимаколенник №1, пятое место">{/if}
{if $oUserProfile->getDisplayName() == 'Raseri'}<img src="/images/achi/raseri.jpg" title="М-м… до тех пор, пока к какому-нибудь конкурсу не нарисую иконки в течение двух недель после его завершения.">{/if}
{if $oUserProfile->getDisplayName() == 'DarkDes'}<img src="/uploads/images/00/00/28/2017/04/24/0ub65118a0-5775eb00-18a65c45.png" title="За участие в «Анимаколеннике №1»">{/if}
{if $oUserProfile->getDisplayName() == 'Rs11'}<img src="/uploads/images/00/00/28/2017/04/24/0ub65118a0-5775eb00-18a65c45.png" title="За участие в «Анимаколеннике №1»">{/if}
{if $oUserProfile->getDisplayName() == 'Rubel'}<img src="/uploads/images/00/00/28/2017/04/24/0ub65118a0-5775eb00-18a65c45.png" title="За участие в «Анимаколеннике №1»">{/if}
{if $oUserProfile->getDisplayName() == 'mylittlekafka'}<img src="/uploads/images/00/00/28/2017/04/24/0ub65118a0-5775eb00-18a65c45.png" title="За участие в «Анимаколеннике №1»">{/if}
{if $oUserProfile->getDisplayName() == 'alexmakovsky'}<img src="/uploads/images/00/00/28/2017/04/24/0ub65118a0-5775eb00-18a65c45.png" title="За участие в «Анимаколеннике №1»">{/if}
{if $oUserProfile->getDisplayName() == 'Rogue85'}<img src="/uploads/images/00/00/28/2017/04/24/0ub65118a0-5775eb00-18a65c45.png" title="За участие в «Анимаколеннике №1»">{/if}
{if $oUserProfile->getDisplayName() == 'Xitilon'}<img src="/uploads/images/00/00/28/2017/04/24/0ub65118a0-5775eb00-18a65c45.png" title="За участие в «Анимаколеннике №1»">{/if}
"""  # noqa


def convert():
    create_app()

    pattern = r".*?getDisplayName\(\) == '(?P<username>.*?)'}(?P<meta>.*?)<img.*src=\"(?P<image>.*?)\" title=['\"](?P<title>.*)['\"]"  # noqa

    achievements = []

    image_base_path = "/var/www/old.kolenka"

    creator = User.get_or_none(User.username == "Xitilon")

    lines = old_ach.split("\n")
    for line in lines:
        m = re.search(pattern, line)
        if m:
            username = m.group("username")

            user = User.get_or_none(User.username == username)
            if user is None:
                print(f"Cannot find user {username}")
                continue

            image = m.group("image")
            title = m.group("title")
            meta = m.group("meta")

            created_achivement = None
            for a in achievements:
                if a.title == title:
                    created_achivement = a
                    break
            if created_achivement is None:
                img = content.upload_image(creator.id, 2020, 3, image_base_path + image)
                created_achivement = Achievement.create(title=title, image=img)
                achievements.append(created_achivement)
            else:
                img = created_achivement.image
            AchievementUser.create(
                achievement=created_achivement, user=user, comment=meta
            )
