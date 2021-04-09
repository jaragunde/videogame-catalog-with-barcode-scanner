#!/usr/bin/env python
import csv, requests, sys, subprocess, xmlrpc.client
from bs4 import BeautifulSoup

##### Configuration

# General setup
command = ["zbarcam", "/dev/video2"] # Fetch EANs with the zbarcam tool
#command = ["./fake-code.py"] # Fake EAN generation, useful for testing
#command = False # Set False to type EANs manually
outputFile = "output.csv"
rpc_key = '' # obtain it at upcdatabase.com
mobyGamesSearchOn = True

# Per-system defaults: leave only one of the above

# PS3 defaults
system = "PS3"
idPrefix = "BLES-"
defaultRegion = "ES"

# Wii defaults
system = "Wii"
idPrefix = "RVL-"
defaultRegion = "ESP"

##### End configuration

def lookup(ean):
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
    params = {"rpc_key": rpc_key, "ean": ean}
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
    if system == "PS3":
      siteTitle = siteTitle[:-25] # remove " for PlayStation 3 (20xx)" suffix
    return siteTitle

  return False

def regionFromWiiId(id):
  # Wii ids are like RVL-RSRP-UKV, where the last three letters
  # apparently represent the region (e.g. UKV, ESP, EUR)
  return id[-3:]

def saveCSVRow(outputFile, row):
  with open(outputFile, mode='a') as csvFile:
    csv.writer(csvFile).writerow(row)

def processEntry(eanInputFile):
  ean = eanInputFile.readline().rstrip()
  if not ean:
    return False
  print("Code read:", ean)

  defaultNameMessage = " (empty to skip)"
  searchResult = False
  if rpc_key:
    searchResult = lookup(ean)
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

  print("Product ID [prefix=", idPrefix, "]", sep="", end=": ", flush=True)
  input = sys.stdin.readline().rstrip().upper()
  if system == "PS3" and (
      input.startswith("BCES") or input.startswith("BLES") or
      input.startswith("BCUS") or input.startswith("BLUS")):
    id = input
  else:
    id = idPrefix + input

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

  if system == "Wii":
    global defaultRegion
    defaultRegion = regionFromWiiId(id)

  print("Region [default=", defaultRegion, "]", sep="", end=": ", flush=True)
  region = sys.stdin.readline().rstrip().upper()
  if not region:
    region = defaultRegion

  print("Comments", end=": ", flush=True);
  comments = sys.stdin.readline().rstrip()

  saveCSVRow(outputFile, [system, ean, name, id, region, comments])
  print("Saved to", outputFile)

  return True

def main():
  if command:
    with subprocess.Popen(command, stdout=subprocess.PIPE,
        encoding='UTF-8') as proc:
      while True:
        print("Waiting for barcode scanner...")
        # Loop until there's no more ean data from subprocess
        if not processEntry(proc.stdout):
          break
  else:
    while True:
      print("EAN code (empty to exit)", end=": ", flush=True)
      if not processEntry(sys.stdin):
        break


if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    sys.exit()
