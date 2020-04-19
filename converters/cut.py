import re
from src import create_app
from src.model.models import Post
from src.endpoints.posts import process_cut


def process_text(text):
    # move closing tag before cut
    # <cut></p> -> </p><cut/>
    # <cut></div> -> </div><cut/> span
    text = text.replace("<cut>", "<cut name=" "> </cut>")
    text = text.replace("<cut/>", "<cut name=" "> </cut>")

    text = text.replace("<cut></p>", "</p><cut>")
    text = text.replace("<cut></div>", "</div><cut>")
    text = text.replace("<cut></span>", "</span><cut>")

    return text


def convert():
    create_app()

    for post in Post.select():
        if not post.text:
            continue
        post.text = process_text(post.text)

        cut_info = process_cut(post.text)
        post.has_cut = cut_info["has_cut"]
        post.cut_text = cut_info["text_before_cut"]
        post.cut_name = cut_info["cut_name"]

        post.save()
