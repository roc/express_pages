import ast
import difflib
import os
import pprint
import re
import urllib3

from bs4 import BeautifulSoup

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
PAGES_PATH = BASE_PATH + '/pages/'

pp = pprint.PrettyPrinter(indent=4)
http = urllib3.PoolManager()

express_html = http.request(
    'GET',
    "http://expressjs.com/4x/api.html"
).data.decode('utf-8')
soup = BeautifulSoup(express_html)

sections = []
section_title_tags = soup.find_all('h2')
section_tags = soup.find_all('section')


def next_element(elem):
    while elem is not None:
        # Find next element, skip NavigableString objects
        elem = elem.next_sibling
        if hasattr(elem, 'name'):
            return elem


def create_directories_from_section_titles(titles):
    for title in titles:
        section_title = title.get_text().lower()
        sections.append(section_title)
        directory = PAGES_PATH + section_title
        # pp.pprint("making section " + title.get_text().lower())

        if not os.path.exists(directory):
            os.makedirs(directory)


def find_directory(title):
    title_split = re.split(r'[.|\-]', title)
    section_abbr = title_split[0]
    if len(title_split) > 1:
        name = title_split[1]
        # import pdb; pdb.set_trace()
        section_match = [s for s in sections if section_abbr in s][0]
        # pp.pprint(section_match)
        # pp.pprint("found " + section_match + " using " + section_abbr)
        return {
            "section": section_match,
            "title": name
        }


def write_page(page):
    soup = BeautifulSoup(page)
    h3_id = False
    if soup.find('h3') is not None:
        h3_id = soup.find('h3').get('id')

    if h3_id:
        directory_and_name = find_directory(h3_id)
        if directory_and_name is not None:
            file_obj = directory_and_name

            page_file_path = ''.join([
                PAGES_PATH,
                file_obj['section'],
                '/',
                file_obj['title'],
                '.html'
            ])
            pp.pprint("writing to " + page_file_path)
            page_file = open(page_file_path, 'w')
            page_file.write(page)
            page_file.close()


def gather_pages_from_sections(sections):
    pages = []
    for section_tag in sections:
        page = [str(section_tag)]
        elem = next_element(section_tag)
        while elem and elem.name != 'section':
            page.append(str(elem))
            elem = next_element(elem)
        pages.append('\n'.join(page))

    return pages


def write_pages(pages):
    for page in pages:
        write_page(page)


create_directories_from_section_titles(section_title_tags)
pages = gather_pages_from_sections(section_tags)
write_pages(pages)
