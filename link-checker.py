import os
import re
import requests
import time

IGNORE_LIST = [
    'https://machinelearningmastery.com/start-here',
    ]

def extract_urls(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    url_pattern = r'(https?://[^\s)]+)'
    urls = re.findall(url_pattern, content)
    return urls


def find_all_urls(repo_path):
    all_urls = set()
    file_path = os.path.join(repo_path, 'README.md')
    if os.path.exists(file_path):
        urls = extract_urls(file_path)
        all_urls.update(urls)
    else:
        print('README.md file does not exist in the repository root.')
    return all_urls


def is_broken(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/86.0.4240.75 Safari/537.36'
    }
    retries = 3
    backoff_factor = 0.3
    for i in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            if response.status_code >= 400:
                print(f'{url} returned status code {response.status_code}')
                return True
            else:
                return False
        except requests.exceptions.RequestException as e:
            if i < retries - 1:
                sleep_time = backoff_factor * (2 ** i)
                print(f'Error accessing {url}, retrying in {sleep_time:.1f} seconds...')
                time.sleep(sleep_time)
                continue
            else:
                print(f'Failed to access {url} after {retries} attempts: {e}')
                return True


def check_urls(urls):
    broken_urls = []
    for url in urls:
        if url in IGNORE_LIST:
            print(f'Skipping {url}')
            continue
        if is_broken(url):
            broken_urls.append(url)
        time.sleep(1)
    return broken_urls


def main():
    repo_path = os.getcwd()  # Assumes the script is run from the repository root
    all_urls = find_all_urls(repo_path)
    print(f'Found {len(all_urls)} URLs in README.md.')

    if all_urls:
        broken_urls = check_urls(all_urls)
        print(f'Found {len(broken_urls)} broken URLs.')

        if broken_urls:
            print('Broken URLs:')
            for url in broken_urls:
                print(url)
        else:
            print('No broken URLs found.')
    else:
        print('No URLs found in README.md.')

if __name__ == "__main__":
    main()
