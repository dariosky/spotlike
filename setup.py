from distutils.core import setup

setup(
    name='songlike',
    version='1.0',
    py_modules=['main'],
    install_require=['click'],
    author='Dario Varotto',
    author_email='dariosky+sl@gmail.com',
    description='A bot to ameliorate your Spotify experience',
    entry_points='''
        [console_scripts]
        songlike=main:cli
    '''
)
