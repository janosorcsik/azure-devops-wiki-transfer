# Imports
from os import replace
import re
import uuid


class Translator():
  # Convert Attachment Markdown content to Confluence-Readable format
  # If any attachments found, converted to one of two types depending on extension
  @staticmethod
  def attachments_markdown_to_confluence_xml(content: str) -> str:
    print(f"DEBUG: Input content preview: {content[:200]}...")  # Debug
    
    # Keressük az img tageket
    img_pattern = r'<img[^>]*src="(/.attachments/[^"]+)"[^>]*/?>' 
    matches = re.findall(img_pattern, content)
    print(f"DEBUG: Found image matches: {matches}")  # Debug
    
    if not matches:
      return content
      
    imageFileExtensions = [".jpeg", ".png", ".jpg", ".gif"]
    
    for attachment_path in matches:
      # Kivesszük a fájlnevet az útvonalból
      fileName = attachment_path.split('/')[-1]
      print(f"DEBUG: Processing file: {fileName}")  # Debug
      
      # Keressük meg az eredeti img taget
      img_tag_pattern = r'<img[^>]*src="' + re.escape(attachment_path) + r'"[^>]*/?>' 
      img_matches = re.findall(img_tag_pattern, content)
      
      if img_matches:
        original_img_tag = img_matches[0]
        print(f"DEBUG: Original img tag: {original_img_tag}")  # Debug
        
        # Ellenőrizzük, hogy kép-e
        if any(ext in fileName.lower() for ext in imageFileExtensions):
          # Próbáljuk fájlnév alapú hivatkozással - ez automatikusan működik Confluence-ban
          confluenceLink = f"<ac:image><ri:attachment ri:filename=\"{fileName}\" /></ac:image>"
        else:
          confluenceLink = f"<ac:structured-macro ac:name=\"view-file\" ac:schema-version=\"1\" ac:macro-id=\"{uuid.uuid4()}\"><ac:parameter ac:name=\"name\">{fileName}</ac:parameter><ac:parameter ac:name=\"height\">250</ac:parameter></ac:structured-macro>"
        
        print(f"DEBUG: Confluence link: {confluenceLink}")  # Debug
        content = content.replace(original_img_tag, confluenceLink)
        
    print(f"DEBUG: Final content preview: {content[:200]}...")  # Debug
    return content

  @staticmethod
  def modify_link_location(content: str) -> str:

    links = re.findall(r"src=\"/.attachments/.*\"", content)
    for link in links:
      file = link.split("/")[2]
      content = content.replace(link, f"src=\"{file}")
    return content
