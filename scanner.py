#!/usr/bin/env python
import csv, requests, sys, subprocess, xmlrpc.client
from bs4 import BeautifulSoup
import sqliteBackend

##### Configuration

# General setup
command = ["zbarcam", "/dev/video2"] # Fetch EANs with the zbarcam tool
#command = ["./fake-code.py"] # Fake EAN generation, useful for testing
#command = False # Set False to type EANs manually
upcDatabaseRpcKey = '' # obtain it at upcdatabase.com
mobyGamesSearchOn = True
defaultRegion = "ES"
backend = "CSV" # Possible values are "CSV" and "SQLite"

##### End configuration

# Globals
system = ""
lastIdPrefix = ""

# Known product ID prefixes, used to identify the system
knownIdPrefixesPerSystem = {
  "PS?": [  # PSX and PS2 games use the same prefixes
    "SCES", # 1st-party, European region
    "SLES", # 3rd-party, European region
  ],
  "PS3": [
    "BCES", # 1st-party, European region
    "BLES", # 3rd-party, European region
    "BCUS", # 1st-party, US region
    "BLUS", # 3rd-party, US region
  ],
  "PS4": [
    "CUSA", # European region
  ],
  "PSP": [
    "UCES", # 1st-party, European region
    "ULES", # 3rd-party, European region
  ],
  "GBA": [
    "AGB", # all regions
  ],
  "GC": [
    "DOL", # all regions
  ],
  "NDS": [
    "NTR", # all regions
  ],
  "Wii": [
    "RVL", # all regions
  ],
  "WiiU": [
    "WUP", # all regions
  ],
  "Switch": [
    "HAC", # all regions
  ],
}

def searchOnUpcDatabase(ean):
  print("Searching UPC database...", end=" ", flush=True)
  if ean.startswith("EAN-13:"):
    ean = ean[-13:] # the service does not expect this prefix
  # This is an example of a successful response:
  # {'found': True, 'size': 'PS3', 'message': 'Database entry found',
  #  'description': 'metal gear solid 4 guns of the patriots',
  #  'status': 'success', 'issuerCountryCode': 'de', 'issuerCountry': 'Germany',
  #  'ean': '4012927051122', 'pendingUpdates': 0,
  #  'lastModifiedUTC': DateTime, 'noCacheAfterUTC': DateTime}
  with xmlrpc.client.ServerProxy("https://www.upcdatabase.com/xmlrpc") as proxy:
    params = {"rpc_key": upcDatabaseRpcKey, "ean": ean}
    result = proxy.lookup(params)
    if result["status"] == "success" and result["found"]:
      return result["description"]
    return False

def searchOnMobyGames(searchString):
  # Makes use of DuckDuckGo !bang API.
  print("Searching MobyGames, powered by DuckDuckGo...", end=" ",
      flush=True)
  if searchString.startswith("EAN-13:"):
    searchString = searchString[-13:] # the service does not expect this prefix

  # DDG returns the actual URL of the MobyGames search service in the "Redirect"
  # field, we get this URL and do a new request with it
  ddgRequest = requests.get(
      "https://api.duckduckgo.com/?q=!mobygames+{}&no_redirect=1&format=json"
      .format(searchString))
  mobyRequest = requests.get(ddgRequest.json()["Redirect"])
  parsedSite = BeautifulSoup(mobyRequest.text, "html.parser")

  # We expect that MobyGames gives us the page dedicated to the game when the
  # search is successful; then we parse the <title> tag to get it
  titles = parsedSite.find_all("title")
  if (len(titles) > 0):
    siteTitle = titles[0].getText()
    if siteTitle == "Quick Search":
      # We did not get the game page but the search page instead, it means no
      # results were found
      return False

    siteTitle = siteTitle[:-12] # remove " - MobyGames" suffix from title
    if system == "PS3" or system == "PS4":
      siteTitle = siteTitle[:-25] # remove " for PlayStation 3 (20xx)" suffix
    if system == "PSP":
      siteTitle = siteTitle[:-15] # remove " for PSP (20xx)" suffix
    return siteTitle

  return False

def regionFromNintendoId(id):
  # Nintendo ids are like RVL-RSRP-UKV, where the last three letters
  # apparently represent the region (e.g. UKV, ESP, EUR)
  return id[-3:]

def setupDatabase(outputFile):
  if backend == "CSV":
    # We don't need a setup. The "db handle" is actually the file name
    # TODO: check if file can be opened in write mode at this point
    return outputFile
  elif backend == "SQLite":
    return sqliteBackend.setupDatabaseFile(outputFile)

def saveRow(dbHandle, system, ean, name, id, region, comments):
  if backend == "CSV":
    saveCSVRow(dbHandle, [system, ean, name, id, region, comments])
  elif backend == "SQLite":
    sqliteBackend.saveRow(dbHandle, system, ean, name, id, region, comments)

def saveCSVRow(outputFile, row):
  with open(outputFile, mode='a') as csvFile:
    csv.writer(csvFile).writerow(row)
  print("Saved to", outputFile)

def findDuplicateEan(dbHandle, ean):
  if backend == "CSV":
    # Not implemented for CSVs
    return False
  elif backend == "SQLite":
    return sqliteBackend.findDuplicateEan(dbHandle, ean)

def processEntry(dbHandle, eanInputFile):
  ean = eanInputFile.readline().rstrip()
  if not ean:
    return False
  print("Code read:", ean)

  duplicate = findDuplicateEan(dbHandle, ean)
  if duplicate:
    print("Existing entry found in DB:",
        "EAN: %s" % duplicate["ean"],
        "System: %s" % duplicate["system"],
        "Name: %s" % duplicate["name"],
        "Product ID: %s" % duplicate["productid"],
        "Region: %s" % duplicate["region"],
        "Comment: %s" % duplicate["comment"],
        sep="\n\t", flush=True)
    print("Do you want to add a new, duplicate entry? [y/n]", end=": ", flush=True)
    input = sys.stdin.readline().strip().upper()
    if input == "N":
      # skip to next EAN
      return True

  defaultNameMessage = " (empty to skip)"
  searchResult = False
  if upcDatabaseRpcKey:
    searchResult = searchOnUpcDatabase(ean)
    if searchResult:
      print("Match!")
      defaultNameMessage = " [default=" + searchResult + "]"
    else:
      print("Not found")

  if not searchResult and mobyGamesSearchOn:
    searchResult = searchOnMobyGames(ean)
    if searchResult:
      print("Match!")
      defaultNameMessage = " [default=" + searchResult + "]"
    else:
      print("Not found")

  global lastIdPrefix
  print("Product ID [prefix=", lastIdPrefix, "]", sep="", end=": ", flush=True)
  input = sys.stdin.readline().rstrip().upper()

  # Identify system from product ID prefix. Notice that, if the user did not
  # type a prefix, the search for knownSystem will fail and the previously saved
  # system will be reused.
  # If users need to change between systems PSX <-> PS2, the workaround is to
  # re-type the prefix to force the question.
  found = False
  global system
  for knownSystem, knownPrefixes in knownIdPrefixesPerSystem.items():
    if input[:4] in knownPrefixes:
      found = True
      system = knownSystem
      lastIdPrefix = input[:4]
      break

    if input[:3] in knownPrefixes:
      found = True
      system = knownSystem
      lastIdPrefix = input[:3]
      break

  if not found and lastIdPrefix != "":
    # We assume the user didn't type the prefix and we use the lastIdPrefix
    id = lastIdPrefix + "-" + input
  else:
    # The user typed the prefix and we found it in knownIdPrefixesPerSystem
    id = input

  if system == "" or system == "PS?":
    print("Cannot guess system from product ID, please type", end=": ",
        flush=True)
    system = sys.stdin.readline().rstrip()

  if not searchResult and mobyGamesSearchOn:
    searchResult = searchOnMobyGames(id)
    if searchResult:
      print("Match!")
      defaultNameMessage = " [default=" + searchResult + "]"
    else:
      print("Not found")

  print("Product name", defaultNameMessage, sep="", end=": ", flush=True);
  name = sys.stdin.readline().rstrip().title()
  if not name:
    if searchResult:
      name = searchResult.title()
    else:
      # skip to next EAN
      return True

  global defaultRegion
  if system in ["GC","NDS", "Wii","WiiU","Switch"]:
    defaultRegion = regionFromNintendoId(id)

  print("Region [default=", defaultRegion, "]", sep="", end=": ", flush=True)
  region = sys.stdin.readline().rstrip().upper()
  if not region:
    # User didn't type, use saved default
    region = defaultRegion
  else:
    # Save typed region for the next time
    defaultRegion = region

  print("Comments", end=": ", flush=True);
  comments = sys.stdin.readline().rstrip()

  saveRow(dbHandle, system, ean, name, id, region, comments)

  return True

def main():
  if len(sys.argv) == 1:
    print("Error: missing database file argument.",
        "Usage: scanner.py [CSV FILE]",  sep="\n");
    sys.exit()
  if len(sys.argv) > 2:
    print("Warning: multiple files provided, ignoring all but first one.",
        "Usage: scanner.py [CSV FILE]",  sep="\n");

  outputFile = sys.argv[1]
  dbHandle = setupDatabase(outputFile)

  if command:
    with subprocess.Popen(command, stdout=subprocess.PIPE,
        encoding='UTF-8') as proc:
      while True:
        print("Waiting for barcode scanner...")
        # Loop until there's no more ean data from subprocess
        if not processEntry(dbHandle, proc.stdout):
          break
  else:
    while True:
      print("EAN code (empty to exit)", end=": ", flush=True)
      if not processEntry(dbHandle, sys.stdin):
        break


if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    sys.exit()
