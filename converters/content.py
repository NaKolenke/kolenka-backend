import os
import ntpath
import re
import hashlib
import magic
from shutil import copyfile
from src.model.models import Content
from converters.models import TuMresourceTarget, TuMresource

content_root = "/var/www/old.kolenka/uploads/"


def get_path_from_mres(res):
    # @uploads/images/00/34/17/2017/06/11/0u28e7688f-12112fc6-41888ff5.png
    path = res.path_url.replace("@uploads/", content_root)

    return path


def get_path_from_url(url):
    url = url.replace('src="', "")
    url = url.replace('href="', "")
    url = url.replace('"', "")
    # /uploads/images/00/34/17/2017/06/11/0u28e7688f-12112fc6-41888ff5.png
    path = url.replace("/uploads/", content_root)

    return path


def create_content(
    content_from, content_res_type, content_res_id, user_id, year, month
):
    path = None
    if content_from:
        # http://kolenka.su/uploads/images/00/01/41/avatar/0u5b935089-6bff5537-1ba510f2.png
        path = content_from.replace("http://kolenka.su/uploads/", content_root)

    mresource_query = TuMresourceTarget.select().where(
        (TuMresourceTarget.target_type == content_res_type)
        & (TuMresourceTarget.target == content_res_id)
    )

    if mresource_query.count() > 0:
        res_id = mresource_query.get().mresource
        res = TuMresource.get(TuMresource.mresource == res_id)
        path = get_path_from_mres(res)

    if path == "0":
        path = None

    if path:
        return upload_image(user_id, str(year), str(month), path)
    return None


def replace_uploads_in_text(user, text):
    if text is None:
        return text

    text = text.replace("kolenka.su", "kolenka.net")
    text = text.replace("http://kolenka.net", "https://kolenka.net")
    text = text.replace("https://kolenka.net/", "/")

    blogs_url = r"href=\"\/blog\/([\w\-_]*)\/([\w\-_.]*)([#\w]*).*?\""

    def blog_repl(m):
        blog = m.group(1)
        post = m.group(2)
        comment = m.group(3)

        if post:
            post = post.replace(".html", "")
            url = 'href="/posts/' + post + "/"
            if comment:
                url = url + comment
            url = url + '"'
            return url
        else:
            return 'href="/blogs/' + blog + '/"'

    text = re.sub(blogs_url, blog_repl, text)

    profile_url = r"href=\"\/profile\/([\w\-_]*)\/\""

    def profile_repl(m):
        name = m.group(1)
        return 'href="/users/' + name + '/"'

    text = re.sub(profile_url, profile_repl, text)

    image_src = r'(src="\/uploads\/.*?")'

    def src_repl(m):
        url = m.group(1)
        mres = url.replace('src="/', "@")[:-1]
        res = TuMresource.get_or_none(TuMresource.path_url == mres)
        if not res:
            year = url.split("/")[6]
            month = url.split("/")[7]
            if month[0] == "0":
                month = month[1]

            path = get_path_from_url(url)
        else:
            year = res.date_add.year
            month = res.date_add.month

            path = get_path_from_mres(res)

        if path == "0":
            path = None

        if path:
            content = upload_image(user.id, year, month, path)

            if content:
                return 'src="/content/' + str(content.id) + '/"'
            else:
                return 'src="broken-url"'
        else:
            print("Can't get resource path:" + str(url))

    a_href = r'(href="\/uploads\/.*?")'

    def href_repl(m):
        url = m.group(1)
        mres = url.replace('href="/', "@")[:-1]
        res = TuMresource.get_or_none(TuMresource.path_url == mres)
        if not res:
            year = url.split("/")[5]
            month = url.split("/")[6]

            path = get_path_from_url(url)
        else:
            year = res.date_add.year
            month = res.date_add.month

            path = get_path_from_mres(res)

        if path == "0":
            path = None

        if path:
            content = upload_image(user.id, year, month, path)
            if content:
                return 'href="/content/' + str(content.id) + '/"'
            else:
                return 'href="broken-url"'
        else:
            print("Can't get resource path:" + str(url))

    text = re.sub(image_src, src_repl, text)
    text = re.sub(a_href, href_repl, text)

    return text


def upload_image(user_id, year, month, path):
    if path:
        if not os.path.isfile(path):
            print("Can't find file at path " + path)
            return None
        name = md5(path)
        _, ext = ntpath.splitext(path)
        filename = os.path.join(
            "uploads/", str(user_id) + "/" + str(year) + "/" + str(month) + "/"
        )
        os.makedirs(filename, exist_ok=True)
        # filename = secure_filename(filename)
        new_path = filename + name + ext

        copyfile(path, new_path)

        c_mime = magic.from_file(new_path, mime=True)
        c_size = os.stat(new_path).st_size

        return Content.create(
            user=user_id, path=os.path.abspath(new_path), mime=c_mime, size=c_size
        )
    return None


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
