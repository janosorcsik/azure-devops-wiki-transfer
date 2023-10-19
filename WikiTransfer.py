from Wiki import Wiki

class WikiTransfer:
  def __init__(self, currentWiki: Wiki, newWiki: Wiki):
    self.currentWiki = currentWiki
    self.newWiki = newWiki


  def transfer(self, path, newPath):
      # Get source page content and information for "source wiki"
      try:
        page = self.currentWiki.get_page(path)
      except Exception as e:
        print(e)
        return
      # Upload page to target wiki based on target path and "got" page content
      try:
        self.newWiki.upload_page(newPath+"/"+page.name, page)
        print("Page name: {}\n Old Path: {}\n New Path: {}".format(page.name, "/".join(path.split('/')[:-1]), newPath +"/"+page.name))
      except Exception as e:
        print(e)
      # If any subpages are found for the get_page function, repeat the above
      for subpage in page.childPages:
        self.transfer(subpage['path'], newPath+"/"+page.name)
