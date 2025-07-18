import os

SENSITIVE_WORDS_FILE = 'config/sensitive_words.txt'
DOCS_DIR = 'docs/'
TARGET_SUFFIX = '.md'


def load_sensitive_words():
    if not os.path.exists(SENSITIVE_WORDS_FILE):
        raise FileNotFoundError(f'Not found sensitive words {SENSITIVE_WORDS_FILE}')
    with open(SENSITIVE_WORDS_FILE, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]


def check_file(file_path, sensitive_words):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f'⚠️ Unable to decode {file_path}')
        return False

    for word in sensitive_words:
        if word in content:
            print(f'❌ Found sensitive words「{word}」 in{file_path}')
            return False
    return True


def main():
    sensitive_words = load_sensitive_words()
    if not sensitive_words:
        print('⚠️ Skip check due to empty sensitive words')
        return

    has_error = False
    for root, _, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith(TARGET_SUFFIX):
                file_path = os.path.join(root, file)
                if not check_file(file_path, sensitive_words):
                    has_error = True

    if has_error:
        print('❌ Failed to check sensitive words')
        exit(1)
    else:
        print('✅ Check sensitive words passed')


if __name__ == '__main__':
    main()
