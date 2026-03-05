import algosdk.mnemonic as m
words = m.wordlist.word_list_raw().split(",")
print(f"Number of words: {len(words)}")
print(f"First 5 words: {words[:5]}")
