from functools import partial

import bleach
from bleach import Cleaner
from bleach.linkifier import LinkifyFilter
from bs4 import BeautifulSoup
from markdown import Markdown
from flask import Markup

# Based on
# https://github.com/Wenzil/mdx_bleach/blob/master/mdx_bleach/whitelist.py
#
# License: MIT

ALLOWED_TAGS = [
	"h1", "h2", "h3", "h4", "h5", "h6", "hr",
	"ul", "ol", "li",
	"p",
	"br",
	"pre",
	"code",
	"blockquote",
	"strong",
	"em",
	"a",
	"img",
	"table", "thead", "tbody", "tr", "th", "td",
	"div", "span",
]

ALLOWED_CSS = [
	"highlight", "codehilite",
	"hll", "c", "err", "g", "k", "l", "n", "o", "x", "p", "ch", "cm", "cp", "cpf", "c1", "cs",
	"gd", "ge", "gr", "gh", "gi", "go", "gp", "gs", "gu", "gt", "kc", "kd", "kn", "kp", "kr",
	"kt", "ld", "m", "s", "na", "nb", "nc", "no", "nd", "ni", "ne", "nf", "nl", "nn", "nx",
	"py", "nt", "nv", "ow", "w", "mb", "mf", "mh", "mi", "mo", "sa", "sb", "sc", "dl", "sd",
	"s2", "se", "sh", "si", "sx", "sr", "s1", "ss", "bp", "fm", "vc", "vg", "vi", "vm", "il",
]

def allow_class(_tag, name, value):
	return name == "class" and value in ALLOWED_CSS

ALLOWED_ATTRIBUTES = {
	"h1": ["id"],
	"h2": ["id"],
	"h3": ["id"],
	"h4": ["id"],
	"a": ["href", "title"],
	"img": ["src", "title", "alt"],
	"code": allow_class,
	"div": allow_class,
	"span": allow_class,
}

ALLOWED_PROTOCOLS = ["http", "https", "mailto"]

md = None


def render_markdown(source):
	html = md.convert(source)

	cleaner = Cleaner(
			tags=ALLOWED_TAGS,
			attributes=ALLOWED_ATTRIBUTES,
			protocols=ALLOWED_PROTOCOLS,
			filters=[partial(LinkifyFilter, callbacks=bleach.linkifier.DEFAULT_CALLBACKS)])
	return cleaner.clean(html)


def init_app(app):
	global md

	md = Markdown(extensions=app.config["FLATPAGES_MARKDOWN_EXTENSIONS"],
			extension_configs=app.config["FLATPAGES_EXTENSION_CONFIG"],
			output_format="html5")

	@app.template_filter()
	def markdown(source):
		return Markup(render_markdown(source))


def get_headings(html: str):
	soup = BeautifulSoup(html, "html.parser")
	headings = soup.find_all(["h1", "h2", "h3"])

	root = []
	stack = []
	for heading in headings:
		this = { "link": heading.get("id") or "", "text": heading.text, "children": [] }
		this_level = int(heading.name[1:]) - 1

		while this_level <= len(stack):
			stack.pop()

		if len(stack) > 0:
			stack[-1]["children"].append(this)
		else:
			root.append(this)

		stack.append(this)

	return root
