import json
import os

def parse():
    def read_json_file(file_path):
        """
        Reads a JSON file and returns its content.

        :param file_path: Path to the JSON file
        :return: Content of the JSON file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            print(f"The file {file_path} does not exist.")
        except json.JSONDecodeError:
            print(f"The file {file_path} is not a valid JSON file.")
        return None


    def delete_files_with_language(directory, language):
        """
        Deletes JSON files that have a specified language in the meta info.

        :param directory: Path to the directory containing JSON files
        :param language: Language to look for in the meta section
        """
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                file_path = os.path.join(directory, filename)
                json_content = read_json_file(file_path)
                if json_content and 'meta' in json_content and json_content['meta'].get('language') == language:
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")


    directory_path = './parser/json_docs'
    language_to_delete = 'en'
    delete_files_with_language(directory_path, language_to_delete)

    def write_json_file(file_path, data):
        """
        Writes the content to a JSON file.

        :param file_path: Path to the JSON file
        :param data: Content to be written to the JSON file
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except IOError:
            print(f"Could not write to file {file_path}.")

    def find_max_header_level_and_update_meta(json_content):
        """
        Finds the maximum header level in the JSON content and updates the meta with h1 text.

        :param json_content: Content of the JSON file
        :return: Maximum header level found
        """
        max_header_level = 0
        h1_text = None

        if json_content and 'content' in json_content:
            for item in json_content['content']:
                if 'type' in item and item['type'].startswith('h'):
                    try:
                        level = int(item['type'][1])
                        if level > max_header_level:
                            max_header_level = level
                        if level == 1 and h1_text is None:
                            h1_text = item.get('text', '')
                    except ValueError:
                        continue

        if h1_text:
            if 'meta' not in json_content:
                json_content['meta'] = {}
            json_content['meta']['h1_text'] = h1_text

        return max_header_level

    def process_json_files(directory):
        """
        Processes all JSON files in the specified directory to find the maximum header level
        and update the meta section with h1 text.

        :param directory: Path to the directory containing JSON files
        """
        max_header_level_overall = 0
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                file_path = os.path.join(directory, filename)
                json_content = read_json_file(file_path)
                max_header_level = find_max_header_level_and_update_meta(json_content)
                if max_header_level > max_header_level_overall:
                    max_header_level_overall = max_header_level
                write_json_file(file_path, json_content)

        print(f"Maximum header level found across all JSON files: h{max_header_level_overall}")

    process_json_files(directory_path)

    def process_links_in_text(item):
        """
        Processes the links in the text, placing the URLs in parentheses after the words they belong to,
        and deletes the links key whether it contains links or is empty.

        :param item: Item containing text and links
        """
        if 'links' in item:
            if item['links']:
                for link in item['links']:
                    link_text = link['text']
                    link_url = link['url']
                    if link_text != "" and link_text != " ":
                        item['text'] = item['text'].replace(link_text, f"{link_text} ({link_url})")
            del item['links']

    def process_content(content):
        """
        Processes the content to merge links into text.

        :param content: Content of the JSON file
        :return: Modified content
        """
        for item in content:
            if 'text' in item:
                process_links_in_text(item)
            if 'content' in item:
                process_content(item['content'])
            if 'items' in item:  # Check if there are nested items to process
                process_content(item['items'])

    def update_json_files(directory):
        """
        Updates all JSON files in the specified directory with the processed content.

        :param directory: Path to the directory containing JSON files
        """
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                file_path = os.path.join(directory, filename)
                json_content = read_json_file(file_path)
                if json_content and 'content' in json_content:
                    process_content(json_content['content'])

                    with open(file_path, 'w', encoding='utf-8') as file:
                        json.dump(json_content, file, ensure_ascii=False, indent=4)
                    # print(f"Updated file: {file_path}")
                else:
                    print(f"No content found in file: {file_path}")

    update_json_files(directory_path)

    def concat_consecutive_paragraphs(content):
        """
        Concatenates consecutive paragraphs into one with '\n' as separator.

        :param content: Content of the JSON file
        :return: Modified content
        """
        new_content = []
        i = 0
        while i < len(content):
            item = content[i]
            if item.get('type') == 'paragraph':
                paragraphs = [item['text']]
                i += 1
                while i < len(content) and content[i].get('type') == 'paragraph':
                    paragraphs.append(content[i]['text'])
                    i += 1
                concatenated_text = "\n".join(paragraphs)
                new_content.append({
                    "type": "paragraph",
                    "text": concatenated_text
                })
            else:
                if 'content' in item:
                    item['content'] = concat_consecutive_paragraphs(item['content'])
                new_content.append(item)
                i += 1
        return new_content

    def process_json_files(directory):
        """
        Processes all JSON files in the specified directory to concatenate consecutive paragraphs into one.

        :param directory: Path to the directory containing JSON files
        """
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                file_path = os.path.join(directory, filename)
                json_content = read_json_file(file_path)
                if json_content and 'content' in json_content:
                    json_content['content'] = concat_consecutive_paragraphs(json_content['content'])

                    with open(file_path, 'w', encoding='utf-8') as file:
                        json.dump(json_content, file, ensure_ascii=False, indent=4)
                    print(f"Updated file: {file_path}")

    process_json_files(directory_path)

    def concat_list_items_to_previous_block(content):
        """
        Concatenates texts from unordered and ordered items and places them into the previous block,
        then deletes the unordered/ordered section.

        :param content: Content of the JSON file
        :return: Modified content
        """
        new_content = []
        for i, item in enumerate(content):
            if item.get('type') in ['unordered', 'ordered']:
                previous_item = new_content[-1] if new_content else None
                if previous_item:
                    # Concatenate list items text
                    list_texts = [f"{list_item['text']}" if item.get('type') == 'ordered' else list_item['text'] 
                                  for idx, list_item in enumerate(item.get('items', []))]
                    concatenated_text = "\n".join(list_texts)
                    # Append the concatenated text to the previous block
                    if previous_item.get('type') == 'paragraph':
                        previous_item['text'] += "\n" + concatenated_text
                    else:
                        if 'content' not in previous_item:
                            previous_item['content'] = []
                        has_paragraph = False
                        for sub_item in previous_item['content']:
                            if sub_item.get('type') == 'paragraph':
                                sub_item['text'] += "\n" + concatenated_text
                                has_paragraph = True
                                break
                        if not has_paragraph:
                            previous_item['content'].append({
                                "type": "paragraph",
                                "text": concatenated_text
                            })
                continue  # Skip adding the unordered/ordered item to new_content
            if 'content' in item:
                item['content'] = concat_list_items_to_previous_block(item['content'])
            new_content.append(item)
        return new_content

    def process_json_files(directory):
        """
        Processes all JSON files in the specified directory to concatenate consecutive paragraphs into one.

        :param directory: Path to the directory containing JSON files
        """
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                file_path = os.path.join(directory, filename)
                json_content = read_json_file(file_path)
                if json_content and 'content' in json_content:
                    json_content['content'] = concat_list_items_to_previous_block(json_content['content'])

                    with open(file_path, 'w', encoding='utf-8') as file:
                        json.dump(json_content, file, ensure_ascii=False, indent=4)
                    print(f"Updated file: {file_path}")

    process_json_files(directory_path)

    def parse_table(item):
        """ Format the contents of a table with column alignment. """
        rows = item.get('rows', [])
        if not rows:
            return ["---Table Start---", "No rows available in table", "---Table End---"]

        # Determine the maximum number of columns in the table
        max_cols = max(len(row) for row in rows)
        col_widths = [0] * max_cols  # Initialize column widths

        # Calculate the maximum width of each column
        for row in rows:
            for i, cell in enumerate(row):
                cell_text = cell.get('text', 'No cell text available')
                if i < len(col_widths):  # Ensure we don't go out of bounds
                    col_widths[i] = max(col_widths[i], len(cell_text))
                else:  # If the column is beyond the current width, add it
                    col_widths.append(len(cell_text))

        # Create table rows with left-aligned text
        formatted_rows = ["---Table Start---"]
        for row in rows:
            aligned_row = []
            for i, cell in enumerate(row):
                cell_text = cell.get('text', 'No cell text available')
                aligned_row.append(cell_text.ljust(col_widths[i] if i < len(col_widths) else 0))
            formatted_rows.append(" | ".join(aligned_row))
        formatted_rows.append("---Table End---")

        return formatted_rows

    def concat_texts(content):
        """
        Concatenates texts from headers, paragraphs, and tab_label, inserting type tags.

        :param content: Content of the JSON file
        :return: Concatenated text with type tags
        """
        concatenated_text = []
        for item in content:
            if item.get('type') in ['h1', 'h2', 'h3', 'h4', 'h5', 'paragraph', 'code']:
                try:
                    text = item['text']
                except:
                    print(item.get('type'))
                tag = f"{item['type']}{item['type']}{item['type']}"
                concatenated_text.append(f"{tag}\n{text}")
            if item.get('type') == 'admonition':
                title = item['title']
                tag = f"{item['type']}{item['type']}{item['type']}"
                concatenated_text.append(f"{tag}\n{title}")
                if 'content' in item:
                    concatenated_text.append(concat_texts(item['content']))
            if item.get('type') == 'details':
                title = item['summary']
                tag = f"{item['type']}{item['type']}{item['type']}"
                concatenated_text.append(f"{tag}\n{title}")
                if 'content' in item:
                    concatenated_text.append(concat_texts(item['content']))
            if item.get('type') == 'table':
                formatted_table = parse_table(item)
                concatenated_text.extend(formatted_table)
            if 'tab_label' in item:
                text = item['tab_label']
                tag = 'tab_label'
                concatenated_text.append(f"\n{text}")
            if 'content' in item:
                concatenated_text.append(concat_texts(item['content']))
        return "\n".join(concatenated_text)

    def process_json_files(input_directory, output_directory):
        """
        Processes all JSON files in the specified directory to concatenate texts and produce a final JSON
        with only initial 'meta' and the concatenated text, saving them to a different directory.

        :param input_directory: Path to the directory containing input JSON files
        :param output_directory: Path to the directory to save output JSON files
        """
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        for filename in os.listdir(input_directory):
            if filename.endswith('.json'):
                input_file_path = os.path.join(input_directory, filename)
                json_content = read_json_file(input_file_path)
                if json_content and 'content' in json_content:
                    concatenated_text = concat_texts(json_content['content'])
                    new_json_content = {
                        "meta": json_content['meta'],
                        "text": concatenated_text
                    }

                    output_file_path = os.path.join(output_directory, filename)
                    with open(output_file_path, 'w', encoding='utf-8') as file:
                        json.dump(new_json_content, file, ensure_ascii=False, indent=4)
                    print(f"Processed file: {filename} and saved to: {output_file_path}")

    input_directory_path = './parser/json_docs/' 
    output_directory_path = './parser/processed_docs/'
    process_json_files(input_directory_path, output_directory_path)