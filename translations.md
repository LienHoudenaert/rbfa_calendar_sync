# Translations

This project uses [Flask-Babel](https://python-babel.github.io/flask-babel/) for multilingual support.

Currently supported languages:

* English (`en`)
* Dutch (`nl`)

Translations are stored in:

```text
translations/
└── nl/
    └── LC_MESSAGES/
        ├── messages.po
        └── messages.mo
```

## Translation Workflow

When new translatable text is added to Python files or HTML templates, the translation files need to be updated.

### 1. Mark text for translation

In Python:

```python
from flask_babel import gettext as _

message = _('Search a club')
```

In Jinja templates:

```html
<h1>{{ _('SEARCH A CLUB') }}</h1>
```

### Variables in translations

Do not put Jinja variables directly inside a translation string.

Incorrect:

```html
{{ _('No clubs found for {{ search }}, please try again!') }}
```

Correct:

```html
{{ _('No clubs found for %(search)s, please try again!', search=search) }}
```

This allows Babel to extract the complete string correctly.

---

## Extract Translatable Strings

Run the following command from the root of the project:

```bash
pybabel extract -F babel.cfg -o messages.pot .
```

This scans the Python and HTML template files and creates:

```text
messages.pot
```

The `.pot` file is the translation template containing all translatable strings found in the application.

---

## Update Existing Translations

After extracting the latest strings, update the existing language files:

```bash
pybabel update -i messages.pot -d translations
```

This updates files such as:

```text
translations/nl/LC_MESSAGES/messages.po
```

Existing translations are preserved, and new untranslated strings are added automatically.

---

## Translate the `.po` File

Open:

```text
translations/nl/LC_MESSAGES/messages.po
```

You will find entries like:

```po
msgid "Search"
msgstr ""
```

Add the Dutch translation:

```po
msgid "Search"
msgstr "Zoeken"
```

### Example with variables

```po
#, python-format
msgid "No clubs found for %(search)s, please try again!"
msgstr "Geen clubs gevonden voor %(search)s. Probeer het opnieuw!"
```

Make sure the variable name remains the same in both `msgid` and `msgstr`.

---

## Fuzzy Translations

After running `pybabel update`, some translations may be marked as fuzzy:

```po
#, fuzzy
msgid "Search"
msgstr "Zoeken"
```

Fuzzy translations are not compiled or used by Flask-Babel.

After reviewing the translation, remove:

```po
#, fuzzy
```

The entry should become:

```po
msgid "Search"
msgstr "Zoeken"
```

---

## Compile Translations

After translating the `.po` files, compile them into `.mo` files:

```bash
pybabel compile -d translations
```

Flask-Babel uses the compiled `.mo` files at runtime.

You should see output similar to:

```text
compiling catalog translations/nl/LC_MESSAGES/messages.po to translations/nl/LC_MESSAGES/messages.mo
```

---

# Complete Translation Update Workflow

Whenever translatable text changes:

```bash
pybabel extract -F babel.cfg -o messages.pot .
pybabel update -i messages.pot -d translations
```

Then:

1. Open `translations/nl/LC_MESSAGES/messages.po`
2. Translate the new strings.
3. Review and remove any `#, fuzzy` flags where appropriate.

Finally compile:

```bash
pybabel compile -d translations
```

---

## Quick Reference

### Extract strings

```bash
pybabel extract -F babel.cfg -o messages.pot .
```

### Update translation files

```bash
pybabel update -i messages.pot -d translations
```

### Compile translations

```bash
pybabel compile -d translations
```

### Full workflow

```bash
pybabel extract -F babel.cfg -o messages.pot .
pybabel update -i messages.pot -d translations
pybabel compile -d translations
```
