import csv, sqlite3

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


def importFromCSVFile(db, file):
  with open(file) as csvFile:
    for row in csv.reader(csvFile):
      ean = row[1]
      if ean.startswith("EAN-13:"):
        ean = ean[-13:] # remove prefix
      db.execute("""INSERT INTO games
          (ean, system, name, productid, region, comment)
          VALUES (?,?,?,?,?,?)""",
          (ean, row[0], row[2], row[3], row[4], row[5]))
    db.commit()
