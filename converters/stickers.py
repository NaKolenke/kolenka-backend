import re
from src import create_app
from src.model.models import Post, Comment, Message, User


def convert():
    create_app()

    print("Replacing stickers")

    stickers_set = set()

    def replace_sticker(text):
        if text:
            pattern = r'<img src="\/common\/templates\/skin\/start-kit\/assets\/images\/(.*?)\..*?">'
            items = re.findall(pattern, text)
            for i in items:
                stickers_set.add(i)
            text = re.sub(pattern, r":\1:", text)

            pattern = r'<img src="\/common\/templates\/skin\/start-kit\/assets\/images\/(.*?)\..*?" />'
            items = re.findall(pattern, text)
            for i in items:
                stickers_set.add(i)
            text = re.sub(pattern, r":\1:", text)

            pattern = r'<img src="http:\/\/k\.faisu\.net\/kreguzda\/images\/smilies\/(.*?)\..*?" />'
            items = re.findall(pattern, text)
            for i in items:
                stickers_set.add(i)
            return re.sub(pattern, r":\1:", text)
        return None

    for p in Post.select():
        p.text = replace_sticker(p.text)
        p.cut_text = replace_sticker(p.cut_text)
        p.save()

    for p in Comment.select():
        p.text = replace_sticker(p.text)
        p.save()

    for p in Message.select():
        p.text = replace_sticker(p.text)
        p.save()

    for p in User.select():
        p.about = replace_sticker(p.about)
        p.save()

    print(stickers_set)
