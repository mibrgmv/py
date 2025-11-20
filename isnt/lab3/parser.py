import pandas as pd
import re
import time
from typing import List

DEFAULT_PAGES = 5


def expand_page_range(start, end, reverse=False):
    start_num = int(re.search(r'\d+', start).group())
    start_has_ob = 'об' in start.lower()

    end_num = int(re.search(r'\d+', end).group())
    end_has_ob = 'об' in end.lower()

    result = []

    if reverse:
        if not start_has_ob:
            result.append(str(start_num))
            start_num -= 1

        for page in range(start_num, end_num, -1):
            result.append(f"{page} об.")
            if page > end_num:
                result.append(str(page))

        if end_has_ob:
            result.append(f"{end_num} об.")
    else:
        for page_num in range(start_num, end_num + 1):
            if page_num == start_num:
                if start_has_ob:
                    result.append(f"{page_num} об.")
                else:
                    result.append(str(page_num))
                    if page_num < end_num:
                        result.append(f"{page_num} об.")
            elif page_num == end_num:
                if end_has_ob:
                    result.append(str(page_num))
                    result.append(f"{page_num} об.")
                else:
                    result.append(str(page_num))
            else:
                result.append(str(page_num))
                result.append(f"{page_num} об.")

    return result


def expand_default_pages(num_pages=DEFAULT_PAGES):
    result = []
    for page in range(1, num_pages + 1):
        result.append(str(page))
        result.append(f"{page} об.")
    return result


def parse_single_archive(archive_num, pages_text):
    result = []

    if not pages_text or pages_text.strip() == '':
        pages = expand_default_pages(DEFAULT_PAGES)
        for page in pages:
            result.append(f"ПД {archive_num} л. {page}")
        return result

    pattern = r'(\d+\s*об\.?(?:\s*[—–\-]\s*\d+\s*об?\.?)?|\d+(?:\s*[—–\-]\s*\d+)?)'
    matches = re.finditer(pattern, pages_text)

    for match in matches:
        page_spec = match.group(1).strip()
        page_spec = page_spec.replace('—', '-').replace('–', '-')

        if '-' in page_spec:
            parts = re.split(r'\s*-\s*', page_spec)
            if len(parts) == 2:
                start = parts[0].strip()
                end = parts[1].strip()

                start_num = int(re.search(r'\d+', start).group())
                end_num = int(re.search(r'\d+', end).group())

                reverse = start_num > end_num
                expanded = expand_page_range(start, end, reverse)

                for page in expanded:
                    result.append(f"ПД {archive_num} л. {page}")
        else:
            result.append(f"ПД {archive_num} л. {page_spec}")

    if not result:
        pages = expand_default_pages(DEFAULT_PAGES)
        for page in pages:
            result.append(f"ПД {archive_num} л. {page}")

    return result


def parse_cipher(text):
    result = []
    text_clean = re.sub(r'\([^)]*\)', '', text)

    pattern = r'(?:в\s+тетр\.\s+)?ПД\s+(\d+)(.*?)(?=(?:\bПД\s+\d+|;|$))'
    matches = re.finditer(pattern, text_clean, re.IGNORECASE | re.DOTALL)

    for match in matches:
        archive_num = match.group(1)
        pages_context = match.group(2)
        archive_results = parse_single_archive(archive_num, pages_context)
        result.extend(archive_results)

    pattern_range = r'ПД\s+(\d+)\s*[—–\-]\s*ПД\s+(\d+)'
    matches_range = re.finditer(pattern_range, text_clean, re.IGNORECASE)

    for match in matches_range:
        start_num = int(match.group(1))
        end_num = int(match.group(2))

        for num in range(start_num, end_num + 1):
            pages = expand_default_pages(DEFAULT_PAGES)
            for page in pages:
                result.append(f"ПД {num} л. {page}")

    return result


def main():
    start_time = time.time()
    input_file = "variant_4.csv"
    output_file = "result.csv"

    df = pd.read_csv(input_file)
    results = []

    for idx, row in df.iterrows():
        text_index = row['index']
        text_content = row['autographs']

        ciphers = parse_cipher(text_content)
        ciphers_str = '; '.join(ciphers) + ';' if ciphers else ''

        results.append({
            'index': text_index,
            'ciphers': ciphers_str
        })

    result_df = pd.DataFrame(results)
    result_df.to_csv(output_file, index=False, encoding='utf-8')
    end_time = time.time()
    print(f"execution time: {(end_time - start_time):.4f} seconds")


if __name__ == "__main__":
    main()
