import flexx
import requests
from queue import Queue
import time


def fetch(url, cursor, q):
    data = requests.get(url + "?" + cursor, verify=False).json()["data"]
    for p in data["posts"]:
        q.put(p)
    return data["nextCursor"]


def iter_hot(url):
    cursor = ""
    q = Queue()
    while q:
        if q.empty():
            cursor = fetch(url, cursor, q)
        yield q.get()


from flexx import flx


class PostLoader(flx.PyComponent):
    def init(self, section):
        super().init()

        url = f"https://9gag.com/v1/group-posts/group/{section}/type/hot"

        self.it = iter_hot(url)
        self.ui = UI(self)

    @flx.action
    def next(self):
        post = next(self.it)
        self.ui.set_post(post)


class UI(flx.JsComponent):
    CSS = """
    img {
        position: absolute;
        margin: auto;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
    }
    """

    def init(self, pl):
        self.img = flx.ImageWidget()

        self.pl = pl
        self.next()

    def next(self):
        global window
        post = self.pl.next()
        window.setTimeout(self.next, 5000)

    @flx.action
    def set_post(self, post):
        self.img.set_source(post["images"]["image700"]["url"])


if __name__ == "__main__":
    import sys

    section = sys.argv[1]

    app = flx.App(PostLoader, section)
    app.launch("app")  # to run as a desktop app
    flx.run()
