import pandas as pd
import re
import time
from typing import List
from datetime import datetime

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
        if start_has_ob:
            result.append(f"{start_num} об.")
            start_num += 1

        for page in range(start_num, end_num):
            result.append(str(page))
            result.append(f"{page} об.")

        if start_num <= end_num:
            result.append(str(end_num))
            if end_has_ob:
                result.append(f"{end_num} об.")

    return result


def expand_default_pages(num_pages=DEFAULT_PAGES):
    result = []
    for page in range(1, num_pages + 1):
        result.append(str(page))
        result.append(f"{page} об.")
    return result


def parse_single_archive(archive_num, pages_text):
    result = []

    # нет листов – ПД 123
    if not pages_text or pages_text.strip() == '':
        pages = expand_default_pages(DEFAULT_PAGES)
        for page in pages:
            result.append(f"ПД {archive_num} л. {page}")
        return result

    # Находим все упоминания л. [что-то]
    # Убираем комментарии в скобках
    pages_text = re.sub(r'\([^)]*\)', '', pages_text)

    # Ищем все вхождения "л. [число/диапазон]"
    # Паттерн: л. и дальше цифры, "об.", тире, запятые до следующего "л." или конца
    pattern = r'л\.\s*([\d]+(?:\s*об\.)?(?:\s*[—–\-]\s*[\d]+(?:\s*об\.)?)?)'

    matches = re.finditer(pattern, pages_text, re.IGNORECASE)

    for match in matches:
        page_spec = match.group(1).strip()
        page_spec = page_spec.replace('—', '-').replace('–', '-')

        # Проверяем диапазон
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
            # Одиночный лист
            result.append(f"ПД {archive_num} л. {page_spec}")

    # Если ничего не нашли, значит нет листов
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

    # сложные форматы: ПД, ф. 244, оп. 1, Прилож. № 7
    # pattern_complex = r'ПД,\s*ф\.\s*(\d+),\s*оп\.\s*(\d+),\s*Прилож\.\s*№\s*(\d+)'
    # matches_complex = re.finditer(pattern_complex, text_clean, re.IGNORECASE)
    #
    # for match in matches_complex:
    #     f_num = match.group(1)
    #     op_num = match.group(2)
    #     pril_num = match.group(3)
    #     result.append(f"ПД ф. {f_num} оп. {op_num} Прилож. № {pril_num}")

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
