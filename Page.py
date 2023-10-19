# Imports
from dataclasses import dataclass, field
import re
from typing import List, Optional
# Define page as object via class method
@dataclass
class Page:
  name: str
  path: str
  content: str
  childPages: Optional[List[str]]
  attachments: List[str] = field(default_factory=list)

  def __post_init__(self):
    self.attachments = self.get_attachments(self.content)

  # Get_Attachments function - Use regex to find any information relating to page attachments
  # Attachments appended to list in page object
  def get_attachments(self, content: str) -> list:
    start_regex = r".\]\("
    end_regex = r"(?:(?<=[a-z])|(?<=ps1))\)"
    links = []
    splits = re.split(start_regex, content)
    for index, split in enumerate(splits):
      if "/.attachments" in split:
        links.append(re.split(end_regex, split, 1)[0])
        print(links)
    return links