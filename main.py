# Imports
import os
import argparse
from dotenv import load_dotenv, find_dotenv
from Page import Page
from Wiki import AzureDevOpsWiki, ConfluenceWiki
from WikiTransfer import WikiTransfer

# Load .env file for environment variables
load_dotenv(find_dotenv())

def init_argparse() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
    description="Copy Azure Devops Wiki pages from one wiki to another"
  )
  parser.add_argument(
      "path", help="path to page (including page name)"
  )
  parser.add_argument(
      "newPath", help="location to copy wiki page to"
  )
#   parser.add_argument(
#       "currentWikiUrl", help="Current wiki API URL"
#   )
#   parser.add_argument(
#       "newWikiUrl", help="New wiki API URL"
#   )
  return parser


def main():
  # Load ADO and Confluence Authentication Variables from .env file
  ADO_USERNAME = os.getenv('ADO_USERNAME')
  ADO_PAT = os.getenv('ADO_PAT')
  CONFLUENCE_PAT = os.getenv('CONFLUENCE_PAT')
  CONFLUENCE_USERNAME = os.getenv('CONFLUENCE_USERNAME')
  parser = init_argparse()

  # Define source and target wikis by calling Wiki.py classes where appropriate
  currentWiki = AzureDevOpsWiki("taxually", "Taxsure", "Taxsure", ADO_USERNAME, ADO_PAT)
  newWiki = ConfluenceWiki("lumatax", CONFLUENCE_USERNAME, CONFLUENCE_PAT, "CW", "~/Developer/Work/Taxsure.wiki")

  # Define transfer object by calling WikiTransfer.py class based on source and target wiki variables
  transfer = WikiTransfer(currentWiki, newWiki)

  # Call transfer function from WikiTransfer.py - if the target wiki is a Confluence space, the last part of the path should be the parent page name
  transfer.transfer("/", "CW")

if __name__ == "__main__":
  main()
