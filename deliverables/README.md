# Deliverables

Working area for generated client documents — the output of
`tools/new_document.py`. One subfolder per client:

```
deliverables/
  Contoso_Concrete_LLC/
    Contoso_Concrete_LLC__Data_Migration_Design__20260901.docx
```

File names follow the deliverable naming convention:

```
<Client_Name>__<Document_Title>__<YYYYMMDD>.docx
```

Double underscores separate the three fields; spaces inside a field become
single underscores.

## Caution

Files here may contain client-confidential content. Generated deliverables are
not committed by default — commit deliberately, only when there is a reason to
version a particular document, and check what is in it first.
