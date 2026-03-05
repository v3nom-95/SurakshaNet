import algosdk.mnemonic as m
words_in_list = set(m.wordlist.word_list_raw().split())
user_words = "ticket identify slice mirror science clean airport network cannon vote kidney coconut else toilet infant else equip only leader sniff tackle verb need yellow".split()

missing = []
for w in user_words:
    if w not in words_in_list:
        missing.append(w)

if missing:
    print(f"Missing words: {missing}")
else:
    print("All words are in the wordlist")
