from src.utils import sanitize


def test_sanitize():
    html = '<p><strong><span style="color:rgb(59, 67, 81);">Жирный текст</span></strong></p><p><em>Нихрена себе тут интервалы между строками, зачем так много?</em></p><p><u>Подчёркнутый</u></p><p><s>Зачёркнутый</s></p><p>Параграф? Что делает кнопка "Параграф" в нашем редакторе вообще? Она как будто нажата и не отжимается.</p><p><span style="color:rgb(255, 178, 67);">Ну цвет текста, это понятно. Только выглядит как пипетка - кажется будто можно её взять и подобрать цвет со скриншота сайта или какой-то загруженной картинки. Странновато чуть.</span></p><h1>Заголовок 1</h1><h2>2</h2><h3>3</h3><h4>4</h4><h5>5</h5><h6>6</h6><p>Хотелось бы чтоб панель инструментов WYSIWYG-редактора скроллилась вниз по мере увеличения текста поста. А то вот досюда допечатал и уже надо скроллить обратно наверх каждый раз. Или чтоб она дублировалась внизу поста. Но это хуже, т. к. в середине поста её всё равно не будет.</p><p>Для первого теста хватит, думаю.</p><p>И я почему-то не могу выбрать опубликовать пост в блог "На Коленке". Чё это?</p>'
    new_html = sanitize(html)
    assert len(html) == len(new_html) - 2  # -2 for added spaces in styles

    html = '<h2><div style="text-align:right;">hey bois</div></h2><ol><li><p>this is mu</p><table><tbody><tr><td><p></p></td><td><p></p><div style="text-align:center;">Привет</div><p></p></td><td><p></p></td></tr><tr><td><p>Это пример</p></td><td><p></p></td><td><p></p></td></tr><tr><td><p></p></td><td><p></p></td><td><p>Таблицы</p></td></tr></tbody></table></li></ol>'
    new_html = sanitize(html)
    assert len(html) == len(new_html) - 2  # -2 for added spaces in styles

    html = 'http://veloc1.me'
    new_html = sanitize(html)
    assert new_html == '<a href="http://veloc1.me" rel="nofollow">http://veloc1.me</a>'

    html = '<p>Some text</p><cut></cut>'
    new_html = sanitize(html)
    assert new_html == '<p>Some text</p><cut></cut>'
