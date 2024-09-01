import os
import sys
import ebooklib
import math
import re
import ntpath
import warnings
from bs4 import BeautifulSoup
from bs4 import MarkupResemblesLocatorWarning
from ebooklib import epub


def set_output_file_name_with_path(input_file_name_with_path):
    # ntpath instead of os.path because https://stackoverflow.com/a/8384788
    input_file_base_path, input_file_name = ntpath.split(input_file_name_with_path)
    input_file_name_root, input_file_name_ext = ntpath.splitext(input_file_name)

    output_file_name = input_file_name_root.replace("___BIONIC.kepub", "___BIONIC___LIGHTWEIGHT.kepub") + input_file_name_ext
    output_file_name_with_path = input_file_base_path + output_file_name

    return output_file_name_with_path

def modify_html(html_content):
    html_cleared_from_double_span = html_content.replace("</span></span>", "</span>")
    html_content_cleared = re.sub(r"<span class=\"koboSpan\" id=\"kobo(\.[0-9]+)+\">(.*?)</span>", r"\2", html_cleared_from_double_span)

    return str(BeautifulSoup(html_content_cleared, "html.parser"))

def modify_epub(input_file, output_file):
    book = epub.read_epub(input_file, {"ignore_ncx": True})  # "ignore_ncx" cf https://github.com/aerkalov/ebooklib/issues/296

    styles = book.get_items_of_type(ebooklib.ITEM_STYLE)
    styles_list = []
    
    for style in styles:
        style_item = book.get_item_with_href(style.get_name())
        styles_list.append(style_item)

    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        for style in styles_list:
            item.add_link(href=style.get_name(), rel="stylesheet", type="text/css")

        modified_content = modify_html(item.content.decode())
        item.content = modified_content.encode('utf-8')

    epub.write_epub(output_file, book)

if __name__ == "__main__":
    warnings.filterwarnings('ignore', category=MarkupResemblesLocatorWarning)  # cf https://stackoverflow.com/a/62659006

    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print("Usage: python kepub_to_lightweight_kepub.py input_file.epub [output_file.epub]")
        sys.exit(1)

    input_file = sys.argv[1]

    if len(sys.argv) == 2:
        output_file = set_output_file_name_with_path(input_file)
    else:
        output_file = sys.argv[2]

    if not os.path.exists(input_file):
        print(f"Error: {input_file} does not exist.")
        sys.exit(1)

    modify_epub(input_file, output_file)
    print(f"[INFO] lightweight KEPUB file saved as {output_file}")
