# ADO_Wiki_Transfer

Script developed to allow easy restructuring and transferral of Azure DevOps Wiki Documentation to another Wiki within the same organization (Confluence).

## Prerequisites

1. Use pip to install (amongst others) the python-dotenv and atlassian-python-api modules:

  ```python
  pip install -r .\requirements.txt
  ```

2. Create .env file and add the following:

  ```shell
  ADO_USERNAME=<ADO EMAIL>
  ADO_PAT=<ADO PAT>
  CONFLUENCE_USERNAME=<CONFLUENCE EMAIL>
  CONFLUENCE_PAT=<CONFLUENCE PAT>
  ```

**Note:**

- To generate a PAT for Azure DevOps; follow the documentation [here](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=preview-page)
- To generate a PAT for Confluence; follow the documentation [here](https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html)

---

## Running the Script

As things stand, the script multiple arguments for the transfer to run, for authentication purposes and for defining the wikis, these are all currently hardcoded as the variables are only referenced once in main.py:

The arguments are:

- **Authentication**:
  - ADO_USERNAME: as above
  - ADO_PAT: as above
  - CONFLUENCE_USERNAME: as above
  - CONFLUENCE_PAT: as above
- **Azure DevOps Wiki Class**:
  - ADO Organization
  - ADO Project
  - ADO Project Wiki Name
  - ADO_USERNAME
  - ADO_PAT
- **Confluence Wiki Class**:
  - Subdomain
  - CONFLUENCE_USERNAME
  - CONFLUENCE_PAT
  - Confluence Space
  - ADO Wiki Attachment Directory

Following this definition, the current and new wiki arguments e.g. Azure DevOps -> Confluence are supplied to the WikiTransfer module which is defined as a variable **transfer**. This module is then called to use its transfer function to transfer the current wiki page (location defined as the first input) to the desired location (second input).

The page path is defined similar to that of a file system:

- **Path**: The path to the page you wish to transfer (including the page name) e.g. *page1/subpage1/sub-subpage1*
- **newPath**: The path to the header page which you wish to store the page being transferred under e.g. *newPage1/newSubPage1*

During the running of the script:

- The wikiTransfer obtains the information from the page in the current wiki
- If the wiki is to be transferred to Confluence and contains markdown, the markdown is converted to html via the translator module (translator.py)
- The content (regardless of if converted to html or not) is uploaded to the new location.
- Any attachments within the page are extracted from the ADO document and uploaded to the new page (Confluence or ADO wiki)

---

## Areas for Optimization

- Attachment upload - still a bit temperamental
- General code tidying
- Possibility of deciding Azure DevOps or Confluence as the target wiki
- Markdown Conversions - So far only spotted markdown tables to be an issue
