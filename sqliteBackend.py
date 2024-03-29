import sqlite3

def setupDatabaseFile(file):
  db = sqlite3.connect(file)
  tableFound = db.execute("""SELECT name FROM sqlite_schema
      WHERE type='table' AND name='games'""").fetchone()
  if not tableFound:
    print("First-time setup of database file")
    db.execute("""CREATE TABLE games(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        system TEXT NOT NULL,
        name TEXT NOT NULL,
        ean INTEGER,
        productid TEXT,
        region TEXT,
        comment TEXT)""")
  return db


def clearEANPrefix(ean):
  if ean.startswith("EAN-13:"):
    ean = ean[-13:] # remove prefix
  return ean


def saveRow(db, system, ean, name, id, region, comments):
  ean = clearEANPrefix(ean)
  db.execute("""INSERT INTO games
      (ean, system, name, productid, region, comment)
      VALUES (?,?,?,?,?,?)""",
      (ean, system, name, id, region, comments))
  db.commit()


def findDuplicateEan(db, ean):
  ean = clearEANPrefix(ean)
  row = db.execute("""SELECT ean, system, name, productid, region, comment
      FROM games WHERE EAN=?""",
      (ean,)).fetchone()
  if row:
    return {
      "ean": row[0],
      "system": row[1],
      "name": row[2],
      "productid": row[3],
      "region": row[4],
      "comment": row[5]
    }
  else:
    return False
