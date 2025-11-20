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
        # Для обратного порядка (редкий случай)
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
        # Для нормального порядка - ИСПРАВЛЕННАЯ ЛОГИКА
        current = start_num

        while current <= end_num:
            # Первая страница диапазона
            if current == start_num:
                if start_has_ob:
                    result.append(f"{current} об.")
                else:
                    result.append(str(current))
                    # Если это не последняя страница, добавляем оборот
                    if current < end_num:
                        result.append(f"{current} об.")

            # Последняя страница диапазона
            elif current == end_num:
                if end_has_ob:
                    result.append(str(current))
                    result.append(f"{current} об.")
                else:
                    result.append(str(current))

            # Промежуточные страницы
            else:
                result.append(str(current))
                result.append(f"{current} об.")

            current += 1

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

    # Удаляем комментарии в скобках
    pages_text_clean = re.sub(r'\([^)]*\)', '', pages_text)

    # Разбиваем по запятым
    parts = [p.strip() for p in pages_text_clean.split(',')]

    for part in parts:
        if not part:
            continue

        # Ищем "л. число/диапазон"
        if 'л.' in part.lower():
            pattern = r'л\.\s*([\d]+(?:\s*об\.)?(?:\s*[—–\-]\s*[\d]+(?:\s*об\.)?)?)'
            matches = re.finditer(pattern, part, re.IGNORECASE)

            for match in matches:
                page_spec = match.group(1).strip()
                page_spec = page_spec.replace('—', '-').replace('–', '-')

                if '-' in page_spec:
                    splits = re.split(r'\s*-\s*', page_spec)
                    if len(splits) == 2:
                        start = splits[0].strip()
                        end = splits[1].strip()

                        start_num = int(re.search(r'\d+', start).group())
                        end_num = int(re.search(r'\d+', end).group())

                        reverse = start_num > end_num
                        expanded = expand_page_range(start, end, reverse)

                        for page in expanded:
                            result.append(f"ПД {archive_num} л. {page}")
                else:
                    result.append(f"ПД {archive_num} л. {page_spec}")
        else:
            # Просто число без "л." (например ", 50" или ", 26")
            match_num = re.search(r'^\s*(\d+)\s*(об\.)?', part)
            if match_num:
                num = match_num.group(1)
                has_ob = match_num.group(2) is not None
                if has_ob:
                    result.append(f"ПД {archive_num} л. {num} об.")
                else:
                    result.append(f"ПД {archive_num} л. {num}")

    if not result:
        pages = expand_default_pages(DEFAULT_PAGES)
        for page in pages:
            result.append(f"ПД {archive_num} л. {page}")

    return result


def parse_cipher(text: str) -> List[str]:
    if pd.isna(text):
        return []

    result = []

    # комментарии в скобках
    text_clean = re.sub(r'\([^)]*\)', '', text)

    # ПД [число] и всё до следующего ПД или точки с запятой или конца
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
    input_file = "test.csv"
    output_file = "test_result.csv"

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

# todo ПД 391 — ПД 412
# todo 4 текст 842 неправильный промежуток
# todo ПД 845, л. 3 об. — 4, 50
