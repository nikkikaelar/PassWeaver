import itertools
import random
import string
import re
from typing import List
from termcolor import colored
import time
import sys
import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer

# Enhanced character substitution map for leetspeak variations
leet_substitutions = {
    'a': ['@', '4', '^'],
    'b': ['8', '6'],
    'c': ['(', '{', '[', '<'],
    'e': ['3', '&'],
    'g': ['6', '9', 'q'],
    'i': ['1', '!', '|', 'l'],
    'o': ['0', 'Q', '*'],
    's': ['$', '5', 'z'],
    't': ['7', '+', '†'],
    'z': ['2', 's']
}

ascii_art = """
╔───────────────────────────────────────────────────────────────────────────────────╗
│ ██▓███   ▄▄▄        ██████   ██████     █     █░▓█████ ▄▄▄    ██▒   █▓▓█████  ██▀███  │
│▓██░  ██▒▒████▄    ▒██    ▒ ▒██    ▒    ▓█░ █ ░█░▓█   ▀▒████▄ ▓██░   █▒▓█   ▀ ▓██ ▒ ██▒│
│▓██░ ██▓▒▒██  ▀█▄  ░ ▓██▄   ░ ▓██▄      ▒█░ █ ░█ ▒███  ▒██  ▀█▄▓██  █▒░▒███   ▓██ ░▄█ ▒│
│▒██▄█▓▒ ▒░██▄▄▄▄██   ▒   ██▒  ▒   ██▒   ░█░ █ ░█ ▒▓█  ▄░██▄▄▄▄██▒██ █░░▒▓█  ▄ ▒██▀▀█▄  │
│▒██▒ ░  ░ ▓█   ▓██▒▒██████▒▒▒██████▒▒   ░░██▒██▓ ░▒████▒▓█   ▓██▒▒▀█░  ░▒████▒░██▓ ▒██▒│
│▒▓▒░ ░  ░ ▒▒   ▓▒█░▒ ▒▓▒ ▒ ░▒ ▒▓▒ ▒ ░   ░ ▓░▒ ▒  ░░ ▒░ ░▒▒   ▓▒█░░ ▐░  ░░ ▒░ ░░ ▒▓ ░▒▓░│
│░▒ ░       ▒   ▒▒ ░░ ░▒  ░ ░░ ░▒  ░ ░     ▒ ░ ░   ░ ░  ░ ▒   ▒▒ ░░ ░░   ░ ░  ░  ░▒ ░ ▒░│
│░░         ░   ▒   ░  ░  ░  ░  ░  ░       ░   ░     ░    ░   ▒     ░░     ░     ░░   ░ │
│               ░  ░      ░        ░         ░       ░  ░     ░  ░   ░     ░  ░   ░     │
│                                                                   ░                   │
╚───────────────────────────────────────────────────────────────────────────────────╝"""

cyber_intro = """
Ultimate Password List Generator for Brute Force Attacks
"""
cyber_description = ""This tool generates multiple password variations for brute-force attacks, combining leetspeak, patterns, and machine learning techniques.\n"""

# Generate leetspeak variations for a given word with alternating complexity
def generate_leetspeak_variations(word: str) -> List[str]:
    variations = set([word])
    word = word.lower()
    indices = [i for i, char in enumerate(word) if char in leet_substitutions]

    for length in range(1, len(indices) + 1):
        for subset in itertools.combinations(indices, length):
            for replacements in itertools.product(*[leet_substitutions[word[i]] for i in subset]):
                word_list = list(word)
                for idx, replacement in zip(subset, replacements):
                    for i, char in enumerate(replacements):
                        if i % 2 == 0:
                            word_list[subset[i]] = char
                variations.add(''.join(word_list))

    return list(variations)

# Generate common passwords based on user input
def generate_common_passwords(keyword: str) -> List[str]:
    common_patterns = ['123', '2023', 'password', 'admin', 'user', 'secure', 'qwerty', 'letmein', 'welcome', 'trustno1', 'master']
    variations = [keyword, keyword.lower(), keyword.upper(), keyword.capitalize()]
    common_passwords = set()
    for variation in variations:
        for pattern in common_patterns:
            common_passwords.update([
                f"{variation}{pattern}", f"{pattern}{variation}",
                f"{variation}_{pattern}", f"{pattern}_{variation}"
            ])
    return list(common_passwords)

# Add advanced patterns with machine-learned importance
def add_common_patterns(base_words: List[str]) -> List[str]:
    patterns = ['123', '!', '@', '#', 'secure', '2023', 'admin']
    pattern_weights = {'123': 0.8, 'secure': 0.9, '@': 0.7, 'admin': 0.95}
    result = []
    for word in base_words:
        for pattern in patterns:
            result.append(f'{word}{pattern}')
            result.append(f'{pattern}{word}')
            result.append(f'{word}_{pattern}')
            if pattern_weights.get(pattern, 0) > 0.8:
                result.append(f'{word}#{pattern}')
    return base_words + result

# Machine learning model for additional variations using a more sophisticated corpus
def ml_generate_more_variations(base_words: List[str]) -> List[str]:
    external_passwords = joblib.load('common_passwords.pkl') if joblib.os.path.exists('common_passwords.pkl') else [
        'password', 'admin', 'welcome', '123456', 'letmein', 'qwerty'
    ]
    corpus = base_words + external_passwords
    vectorizer = TfidfVectorizer(ngram_range=(2, 3), min_df=1)
    X = vectorizer.fit_transform(corpus)
    model = LogisticRegression(max_iter=1000, class_weight='balanced')
    y = [1] * len(base_words) + [0] * len(external_passwords)
    model.fit(X, y)

    new_variations = []
    for word in base_words:
        features = vectorizer.transform([word])
        if model.predict(features)[0] == 1:
            new_variations.append(word + random.choice(['2023', '!', 'secure']))
    return list(set(base_words + new_variations))

# Stylish progress bar with colors and improved visuals
def display_progress_bar(completed: int, total: int, bar_length: int = 40):
    percent = completed / total
    bar_chars = ['█', '░']  # Block and light block characters
    filled_length = int(bar_length * percent)
    bar = colored(bar_chars[0] * filled_length, 'red') + colored(bar_chars[1] * (bar_length - filled_length), 'yellow')
    sys.stdout.write(f"\rGenerating passwords: [{bar}] {percent * 100:.2f}% Completed")
    sys.stdout.flush()

# Main password generation function
def generate_passwords(keyword: str) -> List[str]:
    common_passwords = generate_common_passwords(keyword)
    keyword_variations = generate_leetspeak_variations(keyword)
    variations_with_patterns = add_common_patterns(common_passwords + keyword_variations)
    final_passwords = ml_generate_more_variations(variations_with_patterns)
    return list(set(final_passwords))

# Stylish terminal UI for hacker-like design
def hacker_style_print(text: str, color: str = 'green', delay: float = 0.02):
    for char in text:
        sys.stdout.write(colored(char, color))
        sys.stdout.flush()
        time.sleep(delay)
    print()

def show_ascii_art():
    print(colored(ascii_art, 'green'))

def save_passwords_to_file(passwords: List[str], filename: str = 'generated_passwords.txt'):
    with open(filename, 'w') as file:
        for password in passwords:
            file.write(password + '\n')
    hacker_style_print(f"\nTotal passwords generated: {len(passwords)}", 'yellow')

def main():
    print(colored(cyber_intro, 'red'))
    hacker_style_print(cyber_description, 'magenta')
    show_ascii_art()
    hacker_style_print("Enter a keyword to generate passwords: ", 'cyan')
    keyword = input("Write the Keyword Here=> ").strip()

    if not re.match(r'^[a-zA-Z0-9]+$', keyword):
        hacker_style_print("\nInvalid input. Please enter a keyword with letters and numbers only.", 'red')
        return

    total_steps = 100  # Simulated progress steps
    passwords = []

    for step in range(total_steps):
        time.sleep(0.05)  # Simulate processing time
        display_progress_bar(step + 1, total_steps)

    passwords = generate_passwords(keyword)
    hacker_style_print("\nGenerated Passwords:", 'cyan')
    for password in passwords[:10]:  # Show top 10 for brevity
        hacker_style_print(password, 'green')

    save_passwords_to_file(passwords)
    hacker_style_print("\nPasswords have been saved to 'generated_passwords.txt'", 'yellow')

if __name__ == "__main__":
    main()
