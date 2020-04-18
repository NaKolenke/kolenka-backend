from converters import achievements
from converters import betacontent
from converters import blogs
from converters import comments
from converters import cut
from converters import nbsp
from converters import posts
from converters import spoilers
from converters import stickers
from converters import users
from converters import videos
from converters import votes


def convert(convert_type):
    if convert_type == "achievements":
        achievements.convert()
    elif convert_type == "betacontent":
        betacontent.convert()
    elif convert_type == "blogs":
        blogs.convert()
    elif convert_type == "comments":
        comments.convert()
    elif convert_type == "cut":
        cut.convert()
    elif convert_type == "nbsp":
        nbsp.convert()
    elif convert_type == "posts":
        posts.convert()
    elif convert_type == "spoilers":
        spoilers.convert()
    elif convert_type == "stickers":
        stickers.convert()
    elif convert_type == "users":
        users.convert()
    elif convert_type == "videos":
        videos.convert()
    elif convert_type == "votes":
        votes.convert()
