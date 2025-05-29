# Imports
from abc import ABC, abstractmethod
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import quote
import re
from atlassian import Confluence
from urllib.parse import unquote
from Page import Page
from translator import Translator
import markdown
from markdown.extensions.toc import TocExtension
# Define Wiki as its own class such that common functions can be assigned (get and upload page, split path)
class Wiki(ABC):
  @abstractmethod
  def get_page(self, path) -> Page:
    pass
  @abstractmethod
  def upload_page(self, path, page):
    pass

  def split_path(self, path):
    pageName = path.split('/')[-1]
    directory = "/".join(path.split('/')[:-1])
    return directory, pageName
# Azure DevOps Wiki Class
class AzureDevOpsWiki(Wiki):
  def __init__(self, organisation: str, projectName: str, wikiName: str, username: str, pat: str):
    self.wikiName = wikiName
    self.url = f"https://dev.azure.com/{organisation}/{projectName}/_apis/wiki/wikis/{wikiName}.wiki"
    self.basicAuth = HTTPBasicAuth(username, pat)

  # Get page function - Make get request based on parameters to get page content
  def get_page(self, path):
    path = quote(path)
    directory, pageName = self.split_path(path)
    try:
      res = requests.get(url = f"{self.url}/pages?includeContent=True&path={path}&api-version=6.0&recursionLevel=OneLevel", auth=self.basicAuth)
      if res.status_code == 404:
        raise Exception(res.json()["message"])
      if str(res.status_code)[0] == '4':
        raise Exception(f"Could not get data from wiki: {self.wikiName} ")
      page = dict(res.json())
      if "errorCode" in page:
        raise Exception(res.json()["message"])

      return Page(name=pageName, path=directory, content=page["content"], childPages=page["subPages"])

    except Exception as e:
      raise e


  # Upload page function - Use put request to upload content obtained from get request and function
  def upload_page(self, path, page: Page) -> None:
    res = requests.put(url = f"{self.url}/pages?includeContent=True&path={path}&api-version=6.0&recursionLevel=OneLevel", json={"content": page.content}, auth=self.basicAuth)
    if "errorCode" in res.json():
      raise Exception(res.json()["message"])

# Confluence Wiki Class
class ConfluenceWiki(Wiki):
  def __init__(self, subdomain: str, username: str, pat: str, space: str, attachementDirectory: str):
    self.confluence = Confluence(
      url=f"https://{subdomain}.atlassian.net",
      username=username,
      password=pat,
      cloud=True
    )
    self.space = space
    # Expandáljuk a ~ karaktert a teljes útvonalra
    import os
    self.attachementDirectory = os.path.expanduser(attachementDirectory)

  # Confluence Wiki Get page function - Make Get request to page based on input parameters
  def get_page(self, pageTitle):
    res = requests.get(url = f"{self.url}?title={pageTitle}&spaceKey={self.spaceKey}", auth=self.basicAuth)

  # Confluence wiki upload page function
  def upload_page(self, path, page: Page, attachementDirectory=None):
    # Define page content from get function and call Translator.py
    content = page.content
    translator = Translator()

    # Define page details as variables
    unquotedTitle = unquote(page.name)
    directory, pageName = self.split_path(path)
    parentPage = unquote(directory.split("/")[-1:][0])
    
    print(f"DEBUG: Processing page: {unquotedTitle}")
    print(f"DEBUG: Path: {path}")
    print(f"DEBUG: Directory: {directory}")
    print(f"DEBUG: Parent page: {parentPage}")

    #if not self.confluence.page_exists(self.space, parentPage):
    #  raise Exception("Parent page doesn't exist")

    #Remove Header HTML Tags (and replace with markdown or blank spaces)
    content = content.replace('<h2>', '##').replace('</h2>', " ").replace('<h3>', "###").replace('</h3>', " ")
    # Remove List-Related HTML Tags
    content = content.replace('<ul>', " ").replace('</ul>', " ").replace('<li>', "- ").replace('</li>', " ")
    # Remove Remaining HTML Tags
    content = content.replace('<br>', " ").replace('</br>'," ").replace('<pre>', " ")

    #Convert remaining markdown elements for easier conversion
    content = content.replace('<', "&lt;").replace('>', "&gt;").replace('[[_TOC_]]', "[TOC]")

    # Convert remaining markdown to confluence-readable html along with any attachments using translator.py
    html = markdown.markdown(content, extensions=['markdown.extensions.tables', 'toc'])

    if page.attachments:
      html = translator.attachments_markdown_to_confluence_xml(html)

    # attempt to create page and: add content, add attachments
    parentId = self.confluence.get_page_id(self.space, parentPage)
    createdPage = None  # Initialize createdPage
    
    try:
      createdPage = self.confluence.create_page(space=self.space, title=unquotedTitle, body=html, parent_id=parentId, representation='storage', editor='v2')
      print(f"Page created: {unquotedTitle}")
    except Exception as e:
      print(f"page {unquotedTitle} already exists! Trying to get and update existing page...")
      # If page already exists, get the existing page AND UPDATE IT
      try:
        createdPage = self.confluence.get_page_by_title(space=self.space, title=unquotedTitle)
        print(f"Found existing page: {unquotedTitle} with ID: {createdPage['id']}")
        
        # UPDATE THE EXISTING PAGE CONTENT
        print(f"Updating existing page content...")
        updated_page = self.confluence.update_page(
          page_id=createdPage['id'],
          title=unquotedTitle,
          body=html,
          representation='storage'
        )
        print(f"Successfully updated page: {unquotedTitle}")
        createdPage = updated_page
        
      except Exception as e2:
        print(f"Could not get/update existing page {unquotedTitle}: {str(e2)}")
        createdPage = None

    for attachment in page.attachments:
      try:
        attachment_path = self.attachementDirectory + attachment
        print(f"Attempting to upload: {attachment_path}")

        # Ellenőrizzük, hogy létezik-e a fájl
        import os
        if not os.path.exists(attachment_path):
            print(f"ERROR: File not found: {attachment_path}")
            continue

        # Ellenőrizzük, hogy van-e érvényes page ID
        if not createdPage or "id" not in createdPage:
            print(f"ERROR: No valid page ID for attachment: {attachment}")
            continue

        print(f"File exists, uploading to page ID: {createdPage['id']}")
        print(f"Page title: {createdPage['title']}")
        print(f"Space: {self.space}")
        print(f"File size: {os.path.getsize(attachment_path)} bytes")
        
        result = self.confluence.attach_file(
            attachment_path, 
            page_id=createdPage["id"], 
            title=createdPage['title'], 
            space=self.space
        )
        print(f"Confluence API result: {result}")
        print(f"SUCCESS: Uploaded {attachment}")

      except FileNotFoundError as e:
        print(f"FILE ERROR: {attachment} - File not found: {str(e)}")
      except PermissionError as e:
        print(f"PERMISSION ERROR: {attachment} - {str(e)}")
      except Exception as e:
        print(f"UPLOAD ERROR: {attachment} - {type(e).__name__}: {str(e)}")
        # Próbáljunk több információt kinyerni
        if hasattr(e, 'response'):
            print(f"HTTP Status: {e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'}")
            print(f"Response: {e.response.text if hasattr(e.response, 'text') else 'N/A'}")
    print("Page Uploaded!")
