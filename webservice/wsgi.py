# if you have an old pysqlite version in your system:
# install `pip install pysqlite3-binary`
# patch the sqlite3 module to use pysqlite3 - to override old system sqlite
__import__("pysqlite3")
import sys

sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

# noinspection PyUnresolvedReferences
from webservice.apiserver import app as application
