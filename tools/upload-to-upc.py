#!/usr/bin/env python
import csv, sys, xmlrpc.client

##### Configuration

# General setup
inputFile = "input.csv"
rpc_key = '' # obtain it at upcdatabase.com

##### End configuration

def upload(ean, description, system):
  if ean.startswith("EAN-13:"):
    ean = ean[-13:] # the service does not expect this prefix
  with xmlrpc.client.ServerProxy("https://www.upcdatabase.com/xmlrpc") as proxy:
    params = {
      "rpc_key": rpc_key,
      "ean": ean,
      "description": description,
      "size": system}
    result = proxy.writeEntry(params)
    print(result["message"], end=". ", flush=True)

    return result["status"] == "success"

def main():
  with open(inputFile, mode='r') as csvFile:
    reader = csv.reader(csvFile)
    for row in reader:
      if len(row) < 5:
        continue
      ean = row[1]
      description = row[2] + " [" + row[4] + "]" # "title [region]"
      system = row[0]
      print("Uploading entry:", description, end="... ", flush=True)
      if upload(ean, description, system):
        print("Success!")
      else:
        print("Failed.")

if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    sys.exit()
