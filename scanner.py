#!/usr/bin/env python
import csv, sys, subprocess, xmlrpc.client

# Configuration
command = ["zbarcam", "/dev/video2"]
#command = ["./fake-code.py"]
outputFile = "ps3.csv"
system = "PS3"
idPrefix = "BLES-"
defaultRegion = "ES"
rpc_key = '' # obtain it at upcdatabase.com

def lookup(ean):
  ean = ean[-13:] # remove prefix 'EAN-13:'
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

def regionFromWiiId(id):
  # Wii ids are like RVL-RSRP-UKV, where the last three letters
  # apparently represent the region (e.g. UKV, ESP, EUR)
  return id[-3:]

def saveCSVRow(outputFile, row):
  with open(outputFile, mode='a') as csvFile:
    csv.writer(csvFile).writerow(row)

def main():
  with subprocess.Popen(command, stdout=subprocess.PIPE) as proc:
    while True:
      line = proc.stdout.readline()
      if not line:
        break
      ean = line.decode('UTF-8').rstrip()
      print("Code read:", ean)

      defaultNameMessage = ""
      if rpc_key:
        print("Searching UPC database...", end=" ", flush=True)
        searchResult = lookup(ean)
        if searchResult:
          print("Match!")
          defaultNameMessage = " [default=" + searchResult + "]"
        else:
          print("Not found")

      print("Product name", defaultNameMessage, sep="", end=": ", flush=True);
      name = sys.stdin.readline().rstrip().title()
      if not name and searchResult:
        name = searchResult.title()

      print("Product ID [prefix=", idPrefix, "]", sep="", end=": ", flush=True)
      id = idPrefix + sys.stdin.readline().rstrip().upper()

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

if __name__ == "__main__":
  main()
