Videogame catalog with barcode scanner
======================================

This is a simple script to help catalog my videogames. It can retrieve a
barcode from the webcam using `zbarcam`, then look up the obtained EAN in
several online services, and merge the result with some data provided by the
user. Finally, data is saved to a local file in CSV format or a SQLite database.

How to use
----------

Open the `scanner.py` script and modify the `# Configuration` section in the
beginning according to your needs. Then run from your terminal, passing the
output file name as argument. Example:
```
$ ./scanner.py mygamedb.csv
```

Scan a code, then you will be prompted for the name of the item, its id,
description and some comments. You can leave some fields blank, they would
be filled by some default value if present.

The output CSV file will contain the following columns: system, ean, name, id,
region and comments.

NOTICE: You will have to get your own UPC Database key if you want to use that
service.
