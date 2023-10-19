# Imports
from os import replace
import re
import uuid 


class Translator():
  # Convert Attachment Markdown content to Confluence-Readable format
  # If any attachments found, converted to one of two types depending on extension
  @staticmethod
  def attachments_markdown_to_confluence_xml(content: str) -> str:
    fileRegex = "src=\"/.attachments\/.*\""
    matches = re.findall(fileRegex, content)
    if not matches:
      return content
    imageFileExtentions = [".jpeg", ".png", "jpg"]
    fileNames = [match.split('/')[2] for match in matches if "http" not in match and "." in match]
    replaceRegex = "<img alt=\".*\" src=\".*\".*/>"
    imageFileExtentions = ["jpeg", "png", "jpg"]
    for fileName in fileNames:
      attachementString = re.search(replaceRegex, content).group()
      if any(x in attachementString for x in imageFileExtentions):
        # filename includeds a closing " which is why there is no closing 
        confluenceLink = f"<ac:image><ri:attachment ri:filename=\"{fileName} /></ac:image>"
      else:
        confluenceLink = f"<ac:structured-macro ac:name=\"view-file\" ac:schema-version=\"1\" ac:macro-id=\"{uuid.uuid4()}\"><ac:parameter ac:name=\"name\"><ri:attachment ri:filename=\"{fileName} /></ac:parameter><ac:parameter ac:name=\"height\">250</ac:parameter></ac:structured-macro>"
      #print("Confluence Link: ", confluenceLink)
      content = content.replace(attachementString, confluenceLink)
      #print(content)
    return content

  @staticmethod
  def modify_link_location(content: str) -> str:

    links = re.findall("src=\"/.attachments\/.*\"", content)
    for link in links:
      file = link.split("/")[2]
      content = content.replace(link, f"src=\"{file}")
    return content