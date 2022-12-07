"""
md2pdf: render markdown file to pdf
"""
import argparse
from io import StringIO
from pathlib import Path

import frontmatter  # https://pypi.org/project/python-frontmatter/
import jinja2
import markdown
import xhtml2pdf.pisa as pisa


def markdown_to_html(content: str) -> str:
	"""
	transform markdown to html
	"""
	parser = markdown.Markdown(extensions=['codehilite', 'fenced_code', 'toc'])
	return parser.convert(content)


def markdown_preprocessing(src) -> dict:
	"""
	Preprocessing the markdown file.

	Extract the Front Matter header to save into metadata key
	Remaining content is in the markdown_content key
	"""

	file_parts = frontmatter.load(src)
	p = Path(__file__).parent.parent
	file_parts.metadata['STATIC_URL'] = f'{p}'

	return {
		'markdown_content': file_parts.content,
		'metadata': file_parts.metadata,
	}


def html_transform(data_dict: dict, layout_template: str) -> str:
	"""
	Render data with jinja2 template
	"""
	p = Path(__file__).parent.parent / 'templates'
	env = jinja2.Environment(loader=jinja2.FileSystemLoader(p))
	tmpl = env.get_template(layout_template)
	data = tmpl.render(data_dict)
	return data


def pdf_render(html, dest_file, metadata):
	# Shortcut for dumping all logs to the screen
	pisa.showLogging()
	with open(dest_file, 'wb') as pdf_file:
		pdf = pisa.CreatePDF(StringIO(html), pdf_file, context_meta={
			'author': metadata.get('author', ''),
			'subject': metadata.get('subject', ''),
			'title': metadata.get('title', ''),
		})

	if pdf.err:
		print(f"*** {pdf.err} ERRORS OCCURRED")


def main():
	parser = argparse.ArgumentParser("md2pdf", description='Build PDF eBook from markdown files')
	parser.add_argument('--input', '-i', type=str, help='Markdown input')
	parser.add_argument('--output', '-o', type=str, help='PDF eBook output')
	parser.add_argument('--layout', '-l', type=str, default='', help='Layout template to render html to final form')
	parser.add_argument('--trace', type=bool, default=False, help='When enable, will render html to a trace.html file for debugging purpose')

	args = parser.parse_args()
	
	md_data = markdown_preprocessing(args.input)
	metadata = md_data['metadata']
	layout = metadata.get('layout', args.layout)
	if not layout:
		print(f"*** Must specify the layout, either in front matter of md file or in command line argument (--layout)")
		return
	layout = f"{layout}.html"

	md_data['html_content'] = markdown_to_html(md_data['markdown_content'])
	html = html_transform(md_data, layout)
	
	if args.trace:
		with open('trace.html', 'wt') as file_dest:
			file_dest.write(html)

	pdf_render(html, args.output, metadata)	

if __name__ == "__main__":
	main()
