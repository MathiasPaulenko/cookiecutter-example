In order to update the translation files you need to execute the following command in the root folder:

```
pybabel compile --domain=<po_file_without_extension> --directory=arc/settings/locale --use-fuzzy
```

For example:

```
pybabel compile --domain=html_reports --directory=arc/settings/locale --use-fuzzy
```
