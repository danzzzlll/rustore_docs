from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup, Tag
import sys

import json
import os
from urllib.parse import urljoin
from datetime import datetime
import secrets

sys.setrecursionlimit(1_000_000)


def generate_filename():
    # Generate a random URL-safe text string, each character is approximately 6 bits of randomness.
    # Adjust the length as necessary; here, 18 characters from urlsafe give us about 24-27 characters when base64 encoded
    random_string = secrets.token_urlsafe(18)
    return random_string[:25]  # Trim to exactly 25 characters


def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


def get_meta_information(soup, driver):
    language_meta = soup.find('meta', {'name': 'docusaurus_locale'})
    language = language_meta['content'] if language_meta else 'unknown'
    doc_section = ''
    url_parts = driver.current_url.split('/')
    if 'developers' in url_parts:
        doc_section = 'developers'
    elif 'users' in url_parts:
        doc_section = 'users'
    elif 'sdk' in url_parts:
        doc_section = 'sdk'
    elif 'api' in url_parts:
        doc_section = 'api'
    elif 'guides' in url_parts:
        doc_section = 'guides'

    return {
        "language": language,
        "parse_date": datetime.now().isoformat(),
        "current_url": driver.current_url,
        "doc_section": doc_section  # This holds the documentation section
    }


def handle_header(element):
    return {
        "type": element.name,
        "text": element.get_text(strip=True),
        "content": []  # This can later include nested elements if necessary
    }


def handle_admonition(element, base_url):
    # Determine the type of admonition based on its class attribute
    admonition_type = 'unknown'
    if 'theme-admonition-note' in element.get('class', []):
        admonition_type = 'note'
    elif 'theme-admonition-caution' in element.get('class', []):
        admonition_type = 'caution'
    elif 'theme-admonition-warning' in element.get('class', []):
        admonition_type = 'warning'
    elif 'theme-admonition-info' in element.get('class', []):
        admonition_type = 'info'

    admonition_data = {
        "type": "admonition",
        "admonition_type": admonition_type,
        "title": element.find('div', class_='admonitionHeading_Gvgb').get_text(strip=True),
        "content": []
    }

    # Process the content of the admonition block
    content_area = element.find('div', class_='admonitionContent_BuS1')
    for content_element in content_area.children:
        if content_element.name == 'p':
            paragraph_data = {
                "type": "paragraph",
                "text": content_element.get_text(strip=True),
                "links": []
            }
            links = content_element.find_all('a')
            for link in links:
                paragraph_data["links"].append({
                    "text": link.get_text(strip=True),
                    "url": urljoin(base_url, link['href'])
                })
            admonition_data['content'].append(paragraph_data)
        # Additional types like lists, etc., can be added here with similar logic

    return admonition_data


def handle_list(element, base_url):
    list_data = {
        "type": "ordered" if element.name == 'ol' else "unordered",
        "items": []
    }
    # Avoid nested lists affecting the output
    list_items = element.find_all('li', recursive=False)
    for item in list_items:
        item_data = {
            "text": item.get_text(strip=True),
            "links": []
        }
        links = item.find_all('a')
        for link in links:
            item_data["links"].append({
                "text": link.get_text(strip=True),
                "url": urljoin(base_url, link['href'])
            })
        list_data["items"].append(item_data)

    return list_data


def handle_code_block(element):
    if 'theme-code-block' in element.get('class', []):
        # Extract all text within the code block while preserving spacing and formatting
        code_content = ''.join([str(text)
                               for text in element.stripped_strings])
        return {
            "type": "code",
            "text": code_content  # Change 'content' to 'text' to match your requirement
        }
    return None


def handle_paragraph(element):
    return {
        "type": "paragraph",
        "text": element.get_text(strip=True)
    }


def handle_table(element, base_url):
    table_data = {
        "type": "table",
        "headers": [],
        "rows": []
    }

    # First, check if the table has a thead element
    thead = element.find('thead')
    if thead:
        header_elements = thead.find_all('th')
    else:
        # If no thead, assume the first row (<tr>) in the table body (<tbody> or direct child) is the header
        header_elements = element.find('tr').find_all('th') if element.find(
            'tr').find_all('th') else element.find('tr').find_all('td')

    # Extract headers
    table_data['headers'] = [header.get_text(
        strip=True) for header in header_elements]

    # Start extracting rows from the next row after the header row if no <thead>, otherwise from the first row in <tbody>
    tbody = element.find('tbody') if element.find('tbody') else element
    rows_to_parse = tbody.find_all(
        'tr')[1:] if not thead else tbody.find_all('tr')

    # Extract rows
    for row in rows_to_parse:
        row_data = []
        cells = row.find_all('td')
        for cell in cells:
            cell_content = {
                "text": ' '.join(cell.stripped_strings),
                "links": []
            }
            # Extract links within the cell
            links = cell.find_all('a')
            for link in links:
                cell_content["links"].append({
                    "text": link.get_text(strip=True),
                    "url": urljoin(base_url, link['href'])
                })
            row_data.append(cell_content)
        table_data['rows'].append(row_data)

    return table_data


def handle_details(element, base_url):
    details_data = {
        "type": "details",
        "summary": element.find('summary').get_text(strip=True),
        "content": []
    }

    # Get content inside the <details> tag after <summary>
    # Assuming the next div contains the details content
    content_area = element.find('div')
    for content_element in content_area.descendants:
        if content_element.name == 'p':
            paragraph_data = {
                "type": "paragraph",
                "text": content_element.get_text(strip=True),
                "links": []
            }
            links = content_element.find_all('a')
            for link in links:
                paragraph_data["links"].append({
                    "text": link.get_text(strip=True),
                    "url": urljoin(base_url, link['href'])
                })
            details_data['content'].append(paragraph_data)
        elif content_element.name == 'ul' or content_element.name == 'ol':
            list_data = handle_list(content_element, base_url)
            details_data['content'].append(list_data)

    return details_data


def handle_tabs(element, base_url):
    tabs_data = []
    # Extract all tab labels and associated content areas
    tabs = element.select('.tabs__item')
    tab_panels = element.select('.tabItem_Ymn6')

    # Process each tab and its content
    for tab, panel in zip(tabs, tab_panels):
        tab_label = tab.get_text(strip=True)
        tab_content_list = []

        # Process each item within the tab content area
        for item in panel.select('li'):
            paragraph = item.find('p')
            if paragraph:
                # Convert all links to absolute URLs
                links = [{'text': link.get_text(strip=True), 'url': urljoin(
                    base_url, link['href'])} for link in paragraph.find_all('a')]
                tab_content_list.append({
                    "type": "paragraph",
                    "text": paragraph.get_text(strip=True),
                    "links": links
                })

        # Add the processed tab to the tabs data list
        tabs_data.append({
            "tab_label": tab_label,
            "content": tab_content_list
        })

    return tabs_data


def parse_content(soup, base_url):
    content_area = soup.select_one('.theme-doc-markdown.markdown')
    if not content_area:
        return []

    content_list = []
    for element in content_area.children:
        if isinstance(element, Tag):
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                content_list.append(handle_header(element))
            elif element.name == 'p':
                if content_list and isinstance(content_list[-1], dict) and 'content' in content_list[-1]:
                    content_list[-1]['content'].append(
                        handle_paragraph(element))
            elif element.name in ['ul', 'ol']:
                content_list.append(handle_list(element, base_url))
            elif element.name == 'table':
                content_list.append(handle_table(element, base_url))
            elif element.name == 'div' and 'tabs-container' in element.get('class', []):
                content_list.extend(handle_tabs(element, base_url))
            elif 'theme-admonition' in element.get('class', []):
                content_list.append(handle_admonition(element, base_url))
            elif element.name == 'details':
                content_list.append(handle_details(element, base_url))
            elif 'theme-code-block' in element.get('class', []):
                code_block = handle_code_block(element)
                if code_block:
                    content_list.append(code_block)

    return content_list


def scrape_site(driver, url, base_url, visited, output_directory):
    normalized_url = url.split('#')[0]
    if normalized_url in visited or not normalized_url.startswith(base_url):
        return

    visited.add(normalized_url)
    try:
        driver.get(normalized_url)
        sleep(2)  # Simulate user behavior
        soup = BeautifulSoup(driver.page_source, 'lxml')
        meta_info = get_meta_information(soup, driver)
        content_data = parse_content(soup, base_url)
        create_directory(output_directory)
        filename = os.path.join(output_directory, f"{generate_filename()}.json")

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({"meta": meta_info, "content": content_data},
                      f, indent=4, ensure_ascii=False)
        print(f"Saved {filename}")

        # Recursively scrape found links
        for link in soup.find_all('a', href=True):
            href = urljoin(normalized_url, link['href'].split('#')[0])
            if href.startswith(base_url) and href not in visited:
                scrape_site(driver, href, base_url, visited, output_directory)
    except Exception as e:
        error_message = f"Error processing {normalized_url}: {str(e)}"
        with open("errors_url.txt", "a") as error_file:
            error_file.write(error_message + '\n')
        print(error_message)


def parse_rustore():
    start_url = 'https://rustore.ru/help'
    visited = set()
    options = Options()
    options.headless = True
    service = Service(executable_path='chromedriver.exe')
    output_directory = './parser/json_docs'
    with webdriver.Chrome(service=service, options=options) as driver:
        scrape_site(driver, start_url, start_url, visited, output_directory)

