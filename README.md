<img src="logo.png"/>

![Kolenka CI](https://github.com/NaKolenke/kolenka-backend/workflows/Kolenka%20CI/badge.svg)
[![Hits-of-Code](https://hitsofcode.com/github/NaKolenke/kolenka-backend)](https://hitsofcode.com/view/github/NaKolenke/kolenka-backend)

kolenka.net - это сайт небольшого коммьюнити разработчиков игр. В этом репозитории лежит бекенд всего сайта. У нас есть блоги, в которые пользователи могут писать посты, а другие пользователи могут комментировать эти посты.

## Используемые инструменты

* Python 3
* Flask
* peewee

## Подготовка к работе

Для начала необходимо установить [poetry](https://python-poetry.org/)

`$ poetry install`

скачает все необходимые зависимости.

Далее, запускаем новую сессию:

`$ poetry shell`

Все переменые подгрузятся автоматически.

Запуск сервера:

`$ flask run`

Далее, открываем localhost:5000, должна открыться приветственная страница

Чтобы выйти из сессии:

`$ exit`

## Как помочь

Выбери задачу из [таск-трекера](https://github.com/NaKolenke/kolenka-doc/projects/1), сделай форк, внеси изменения, протестируй, сделай пулл-реквест. Все просто!


## Конвертирование старой базы в новую

Перенести данные можно, используя `python main.py convert`. После этого нужно починить автоинкремент:

Для postgresql

```
SELECT 'SELECT SETVAL(' ||
       quote_literal(quote_ident(PGT.schemaname) || '.' || quote_ident(S.relname)) ||
       ', COALESCE(MAX(' ||quote_ident(C.attname)|| '), 1) ) FROM ' ||
       quote_ident(PGT.schemaname)|| '.'||quote_ident(T.relname)|| ';'
FROM pg_class AS S,
     pg_depend AS D,
     pg_class AS T,
     pg_attribute AS C,
     pg_tables AS PGT
WHERE S.relkind = 'S'
    AND S.oid = D.objid
    AND D.refobjid = T.oid
    AND D.refobjid = C.attrelid
    AND D.refobjsubid = C.attnum
    AND T.relname = PGT.tablename
ORDER BY S.relname;
```

После этого нужно применить вывод этой команды
