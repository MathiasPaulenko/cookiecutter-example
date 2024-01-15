from flask import render_template
from markdown_it import MarkdownIt

from arc.settings.settings_manager import Settings
from arc.web.app.home import bp as help_bp


@help_bp.route('/help/readme/')
def readme():
    """
        Render the readme file.
    :return:
    """
    with open(f"{Settings.BASE_PATH.get(force=True)}/README.md") as f:
        md = (
            MarkdownIt('commonmark', {'breaks': True, 'html': True, 'linkify': True,})
        )
        text = f.read()
        text = text.replace('arc/web', '')
        readme_data = md.render(text)
    return render_template(
        'help/readme.html', page_title="Readme",
        readme=readme_data,
        active_page="help"
    )
