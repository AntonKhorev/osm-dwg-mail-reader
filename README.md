# OSM DWG Mail Reader

A python script to read emails sent as replies from OTRS and prepare these emails to be resent as OSM messages.

## Usage

To read an email fed from stdin:

```python
from dwg_mail_reader import DwgMailReader
mail = DwgMailReader()
mail.readFromFile(sys.stdin)
```

After that you'll have access to the following properties:

```python
mail.osm_user_names # array of strings
mail.subject # string
mail.body # string
```

Now you can send a message with subject and body to every user by whatever means you have.

## Assumptions

- *To* email header contains OSM user name like this: `OsmUserName <anything@any.domain.name>`
- Email body has an utf8-encoded html part

## Why

The problem is that an email with a reply from an OTRS system contains the message in html and plaintext formats. OSM's messaging system however expects messages in [kramdown](https://kramdown.gettalong.org/). kramdown is kind of both a subset and a superset of html.

kramdown is a subset of html because tags are limited. But then OTRS-allowed tags are also limited. These limitations don't quite match, notably for `<blockquote>` elements which you get when you reply. Or you're supposed to get them but OTRS decided to not let you have them and give you nonstandard `<div type=cite>` instead. These divs need to be replaced. There are also limitations about where block-level html element can be present in kramdown. Basically, they better [start on a new line](https://kramdown.gettalong.org/syntax.html#html-blocks).

The previous paragraph is true only if we ignore the kramdown-specific syntax which you can mix with html. Since you already have your message in html format, you don't need to use this syntax. Instead you need to prevent parts of the message to be treated as kramdown. So you need to escape kramdown-specific character sequences. It would seem to be obvious that we need to just pass the html through [kramdown's html parser](https://kramdown.gettalong.org/parser/html.html). But we still need to handle `<blockquote>` somehow and maybe we don't want to install kramdown to do just the escaping. Let's just steal [kramdown's escaping code](https://github.com/gettalong/kramdown/blob/0b0a9e072f9a76e59fe2bbafdf343118fb27c3fa/lib/kramdown/converter/kramdown.rb#L74).
