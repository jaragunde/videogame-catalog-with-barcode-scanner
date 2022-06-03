#!/usr/bin/env python
import sys
import sqliteBackend

##### Configuration
databaseFile = "games.sqlite"


def main():
  if len(sys.argv) == 1:
    print("Error: missing CSV file argument.",
        "Usage: import-csv-int-db.py [CSV FILE] [CSV FILE] ...",
        "Imports rows from CSV files into a SQLite database.", sep="\n");
    sys.exit()

  db = sqliteBackend.setupDatabaseFile(databaseFile)

  for inputFile in sys.argv:
    if "import-csv-into-db.py" in inputFile:
      continue
    sqliteBackend.importFromCSVFile(db, inputFile)


if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    sys.exit()
