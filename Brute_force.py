import itertools
import string
import time
from typing import Optional

# Check a wordlist file to see if the target password appears there.
# - word: the password to check
# - path: path to a wordlist file (one entry per line)
# Returns a descriptive string if found, otherwise None.
def common_guess(word: str, path: str = 'brute_force.txt') -> Optional[str]:
    try:
        # Open the wordlist file in a safe context manager and read lines.
        # Using encoding='utf-8' to reduce encoding-related issues across systems.
        with open(path, 'r', encoding='utf-8') as f:
            # splitlines preserves memory structure: one list element per line without newline chars
            word_list = f.read().splitlines()
    except FileNotFoundError:
        # If the file is missing, return None and continue — don't crash the program.
        return None
    # Iterate with an index for reporting which line matched (1-based index).
    for i, w in enumerate(word_list, start=1):
        # Exact (case-sensitive) match. Change to .lower() if you want case-insensitive checking.
        if w == word:
            return f'common match: {w} (#{i})'
    # No match found in the wordlist
    return None

# Brute-force the target by generating all combinations of characters of a given length.
# - word: the target password
# - length: length of combinations to try (e.g., 4 means try all combos of length 4)
# - digits: if True, include digits 0-9 in the character set
# - symbol: if True, include punctuation characters in the character set
# - print_every: if > 0, print progress every N attempts (avoids printing every guess)
# - max_attempts: optional cap to stop after a certain number of attempts
# Returns a descriptive string if cracked, otherwise None.

def brute_force(word: str, length: int, digits: bool = False, symbol: bool = False,
                print_every: int = 0, max_attempts: int | None = None) -> Optional[str]:
    # Start with lowercase letters by default
    chars = string.ascii_lowercase # 'abcdefghijklmnopqrstuvwxyz'
    # Optionally add digits
    if digits:
        chars += string.digits  #  # '0123456789'
    # Optionally add punctuation symbols
    if symbol:
        chars += string.punctuation  # e.g. '!@#$%^&*()...'

    # attempts counter to measure how many guesses we've made
    attempts = 0
    try:
        # itertools.product yields tuples of characters (lazy generator).
        # e.g., product('ab', repeat=3) -> ('a','a','a'), ('a','a','b'), ...
        for combo in itertools.product(chars, repeat=length):
            attempts += 1
            # Join tuple of characters into a single string guess
            guess_str = ''.join(combo)

            # If user requested periodic progress, print every `print_every` attempts
            if guess_str == word:
                # Print a concise progress line: total attempts and last tried string
                return f'"{word}" was cracked in {attempts} guesses.'

            # If a maximum attempts limit is set, stop when reached
            if print_every and attempts % print_every == 0:
                print(f'attempts: {attempts} (last: {guess_str})')

            if max_attempts is not None and attempts >= max_attempts:
                # Reached the enforced attempt cap; return None (not found within cap)
                return None
    except KeyboardInterrupt:
        # Allow the user to stop the brute-force with Ctrl+C cleanly.
        print('Interrupted by user.')
        return None
    # Exhausted the entire search space of this length without finding the password
    return None


def main():
    print('Searching...')

    # Securely obtain password from the user without echoing (getpass).
    # If getpass fails in the current environment (some IDE consoles), fall back to input().
    try:
        password = getpass.getpass('Enter the password to test (input hidden): ')
        # If user just pressed Enter and left it blank, optionally fall back or warn.
        if password == '':
            print('Warning: empty password entered.')
    except Exception:
        # Fallback for environments where getpass can't control the terminal.
        password = input('Enter the password to test (input visible): ')

    start_time = time.perf_counter()

    # First check the wordlist to quickly find very common passwords.
    if common := common_guess(password):
        print(common)
    else:
        # Auto-detect whether digits or symbols are present in the target password
        # so we can include the proper character sets in brute-force.
        need_digits = any(ch.isdigit() for ch in password)
        need_symbols = any(not ch.isalnum() for ch in password)

        found = False
        pw_len = len(password)

        # Example: try only the exact length of the target password.
        # You can expand this range if you want to try shorter/longer lengths.
        for i in range(pw_len, pw_len + 1):
            result = brute_force(
                password,
                length=i,
                digits=need_digits,
                symbol=need_symbols,
                print_every=100000,    # progress printed every 100k attempts
                max_attempts=5_000_000 # safety cap on attempts
            )
            if result:
                print(result)
                found = True
                break

        if not found:
            print("There was no match...")

    end_time = time.perf_counter()
    print(round(end_time - start_time, 2), 'seconds')

if __name__ == '__main__':
    main()