"""Convert Markdown to HTML file.

Required Python modules:

    pip3 install Markdown markdown-checklist

- http://pypi.python.org/pypi/Markdown
- https://github.com/FND/markdown-checklist
"""

# Usage:
#   shell> python markdown2html.py path/to/file.md path/to/output/dir

import sys
import subprocess
import markdown

from markdown_checklist.extension import ChecklistExtension

# Markdown extensions
MD_EXTENSIONS = [
    'toc',
    'meta',
    'extra',
    'footnotes',
    'admonition',
    'tables',
    'attr_list',
    ChecklistExtension(),
]

# Get file name
filename = sys.argv[1]
# Get file name without file extension
filename_without_ext = filename.split('/')[-1].replace('.md', '')

# Get output directory
output_dir = sys.argv[2]

# Get other options and convert them to a dict.
args = sys.argv[3:]
cmd_opts = {}
for arg in args:
    if '=' in arg:
        (var, value) = arg.split('=')
        cmd_opts[var] = value

# Get article title
if 'title' not in cmd_opts:
    cmd_opts['title'] = subprocess.check_output("""grep 'Title:' %s |awk -F'Title: ' '{print $2}'""" % filename)
cmd_opts['title'] = cmd_opts['title'].strip()

# Set output file name
output_html_file = output_dir + '/' + filename_without_ext + '.html'
if 'output_filename' in cmd_opts:
    output_html_file = output_dir + '/' + cmd_opts['output_filename']

# Set HTML head
html = """<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <title>%(title)s</title>
        <link rel="stylesheet" type="text/css" href="./css/markdown.css" />
    </head>
    <body>
""" % cmd_opts

# Add navigation items.
# Link to iRedMail.org
html += """
    <div id="navigation">
    <a href="https://www.iredmail.org" target="_blank">
        <img alt="iRedMail web site"
             src="./images/logo-iredmail.png"
             style="vertical-align: middle; height: 30px;"
             />&nbsp;
        <span>iRedMail</span>
    </a>
    """ % cmd_opts

# Add link to index page in article pages.
if 'add_index_link' in cmd_opts:
    html += """&nbsp;&nbsp;//&nbsp;&nbsp;<a href="./index.html">Document Index</a>"""

html += """</div>"""

# Read markdown file and render as HTML body
# Handle unicode characters with web.safeunicode
orig_content = str(open(filename).read())
html += markdown.markdown(orig_content, extensions=MD_EXTENSIONS)

html += """<div class="footer">
    <p style="text-align: center; color: grey;">All documents are available in <a href="https://github.com/iredmail/docs/">GitHub repository</a>, and published under <a href="http://creativecommons.org/licenses/by-nd/3.0/us/" target="_blank">Creative Commons</a> license. You can <a href="https://github.com/iredmail/docs/archive/master.zip">download the latest version</a> for offline reading. If you found something wrong, please do <a href="https://www.iredmail.org/contact.html">contact us</a> to fix it.</p>
</div>"""

html += '</body></html>'

# Write to file
f = open(output_html_file, 'w')
f.write(html)
f.close()
