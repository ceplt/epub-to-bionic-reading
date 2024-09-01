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


# ------ Params ------

BOLD_TEXT_PERCENTAGE = 40
UPPER_ROUNDING = True  # better results with True

# --------------------


def set_output_file_name_with_path(input_file_name_with_path):
    # ntpath instead of os.path because https://stackoverflow.com/a/8384788
    input_file_base_path, input_file_name = ntpath.split(input_file_name_with_path)
    input_file_name_root, input_file_name_ext = ntpath.splitext(input_file_name)

    output_file_name = input_file_name_root + "___BIONIC" + input_file_name_ext
    output_file_name_with_path = input_file_base_path + output_file_name

    return output_file_name_with_path

def bionic_reading(text):
    alphanum_chars_pattern = "[0-9a-zA-Z]"
    text_without_spe_char_at_the_end = ""

    # if the word ends with , or : or ... or other, we don't want to count this char
    if re.match(alphanum_chars_pattern, text[-1]):
        text_without_spe_char_at_the_end = text
    else:
        text_without_spe_char_at_the_end = text[:-1]

    num_chars_to_bold = ""

    if UPPER_ROUNDING:
        num_chars_to_bold = math.ceil(len(text_without_spe_char_at_the_end)*(BOLD_TEXT_PERCENTAGE/100))
    else:
        num_chars_to_bold = math.floor(len(text_without_spe_char_at_the_end)*(BOLD_TEXT_PERCENTAGE/100))

    return '<b>' + text[:num_chars_to_bold] + '</b>' + text[num_chars_to_bold:]

def modify_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    for text_node in soup.find_all(string=True):
        if text_node.parent.name not in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            new_text = ' '.join([bionic_reading(word) for word in text_node.split()])
            if text_node[-1] == " ":
                new_text += " "
            elif text_node[0] == " ":
                new_text = " " + new_text
            new_text = " " + new_text
            new_text = new_text + " "
            new_text = re.sub(r"\s+", " ", new_text)

            # fix cases where we have <b></b> here, which then give <b/> in the final file
            # and which puts everything in bold in the ebook on the Kobo e-reader
            new_text_fixed = new_text.replace("<b></b>", "")
            
            text_node.replace_with(BeautifulSoup(new_text_fixed, "html.parser"))

    return str(soup)

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
        print("Usage: python epub_to_bionic_reading.py input_file.epub [output_file.epub]")
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
    print(f"[INFO] bionic reading EPUB file saved as {output_file}")
