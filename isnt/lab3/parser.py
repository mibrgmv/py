import re
import pandas as pd
import os


def parse(texts):
    all_results = []

    pattern = r'([А-ЯЁA-Z]+ \d+)[,\s]+л\.\s*([^);]+(?:\([^)]+\)[^);]*)*)'

    for text_num, text in enumerate(texts, 1):
        text_results = []
        matches = re.finditer(pattern, text)

        for match in matches:
            doc_code = match.group(1)
            pages_info = match.group(2)

            pages_info_clean = re.sub(r'\([^)]*\)', '', pages_info)

            page_sequences = parse_page_sequences(pages_info_clean)

            for sequence in page_sequences:
                pages = expand_page_sequence(sequence)
                for page in pages:
                    full_code = f"{doc_code} л. {page}"
                    text_results.append(full_code)

        seen = set()
        unique_results = []
        for item in text_results:
            if item not in seen:
                seen.add(item)
                unique_results.append(item)

        all_results.append({
            'text_number': text_num,
            'codes': '; '.join(unique_results)
        })

    return pd.DataFrame(all_results)


def parse_page_sequences(pages_text):
    """
    Разбивает текст с информацией о страницах на отдельные последовательности
    Пример: "20 об. — 23, 40 об. — 41" -> [('20', 'об.', '23', ''), ('40', 'об.', '41', '')]
    """
    sequences = []

    parts = re.split(r'[;,]', pages_text)

    for part in parts:
        part = part.strip()
        if not part:
            continue

        range_match = re.search(r'(\d+)(?:\s*([а-яё]+))?(?:\s*[—\-]\s*(\d+)(?:\s*([а-яё]+))?)?', part)

        if range_match:
            start_num = range_match.group(1)
            start_side = range_match.group(2) or ''
            end_num = range_match.group(3)
            end_side = range_match.group(4) or ''

            sequences.append((start_num, start_side, end_num, end_side))

    return sequences


def expand_page_sequence(sequence):
    """
    Преобразует последовательность страниц в полный список
    Пример: ('20', 'об.', '23', '') -> ['20 об.', '21', '21 об.', '22', '22 об.', '23']
    """
    start_num, start_side, end_num, end_side = sequence

    # Если нет конечной страницы - возвращаем только начальную
    if not end_num:
        return [f"{start_num} {start_side}".strip()]

    start_num = int(start_num)
    end_num = int(end_num)

    pages = []
    current_num = start_num

    while current_num <= end_num:
        if current_num == start_num and start_side:
            pages.append(f"{current_num} {start_side}")
            if start_side == 'об.' and current_num < end_num:
                pages.append(str(current_num + 1))

        elif current_num == end_num and end_side:
            pages.append(f"{current_num} {end_side}")

        else:
            pages.append(str(current_num))
            if current_num < end_num:
                pages.append(f"{current_num} об.")

        current_num += 1

    return pages


def load_texts_from_directory(directory_path):
    texts = []
    for filename in sorted(os.listdir(directory_path)):
        if filename.endswith('.txt'):
            with open(os.path.join(directory_path, filename), 'r', encoding='utf-8') as f:
                texts.append(f.read())
    return texts


def main():
    input_dir = "articles"
    texts = load_texts_from_directory(input_dir)

    print("Обрабатываю тексты...")
    df = parse(texts)

    output_file = "result.csv"
    df.to_csv(output_file, sep=';', index=False, encoding='utf-8')
    print(f"Результаты сохранены в {output_file}")
    print(f"Обработано текстов: {len(df)}")

    print("\nПервые 5 строк результата:")
    for i, row in df.head().iterrows():
        print(f"Текст {row['text_number']}: {row['codes'][:100]}...")


if __name__ == "__main__":
    main()
