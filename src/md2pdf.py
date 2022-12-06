"""
md2pdf: render markdown file to pdf
"""

def markdown_transform(src) -> dict:
	import frontmatter # https://pypi.org/project/python-frontmatter/
	import markdown

	file_parts = frontmatter.load(src)
	parser = markdown.Markdown(extensions=['codehilite', 'fenced_code', 'toc'])
	return {
		'html_content': parser.convert(file_parts.content),
		'metadata': file_parts.metadata,
	}


def html_transform(data_dict, template='template.html') -> str:
	import jinja2
	env = jinja2.Environment(loader=jinja2.FileSystemLoader("./templates"))
	tmpl = env.get_template(template)
	data = tmpl.render(data_dict)
	return data

def main():
	from io import StringIO
	import argparse
	import xhtml2pdf.pisa as pisa

	parser = argparse.ArgumentParser("md2pdf", description='Build PDF eBook from markdown files')
	parser.add_argument('--input', '-i', type=str, help='Markdown input')
	parser.add_argument('--output', '-o', type=str, help='PDF eBook output')
	parser.add_argument('--template', '-t', type=str, default='', help='Template file for rendering html')
	parser.add_argument('--trace', type=bool, default=False, help='When enable, will render html to a trace.html file for debugging purpose')

	args = parser.parse_args()
	
	md_data = markdown_transform(args.input)

	template = f"{md_data['metadata'].get('layout', args.template)}.html"
	data = html_transform(md_data, template)
	
	if args.trace:
		with open('trace.html', 'wt') as file_dest:
			file_dest.write(data)
	
	# Shortcut for dumping all logs to the screen
	pisa.showLogging()
	with open(args.output, 'wb') as pdf_file:
		pdf = pisa.CreatePDF(StringIO(data), pdf_file, context_meta={
			'author': md_data['metadata'].get('author', ''),
			'subject': md_data['metadata'].get('subject', ''),
			'title': md_data['metadata'].get('title', ''),
		})

	if pdf.err:
		print(f"*** {pdf.err} ERRORS OCCURRED")

if __name__ == "__main__":
	main()
