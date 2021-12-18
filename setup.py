from distutils.core import setup

setup(
    name="spotlike",
    version="0.0.1",
    py_modules=["main"],
    install_require=[
        "click",
        "spotipy",
        "cachetools",
    ],
    author="Dario Varotto",
    author_email="dariosky+spotlike@gmail.com",
    description="A bot to ameliorate your Spotify experience",
    entry_points="""
        [console_scripts]
        spotlike=main:cli
    """,
)
