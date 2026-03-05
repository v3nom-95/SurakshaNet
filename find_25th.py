from algosdk import mnemonic, account
import hashlib

def find_25th_word(m24_str):
    m24_list = m24_str.split()
    if len(m24_list) != 24:
        return f"Error: Expected 24 words, got {len(m24_list)}"
    
    words = mnemonic.wordlist.word_list_raw().split()
    
    # Try all words as the 25th word
    found = []
    for word in words:
        trial_mnemonic = m24_str + " " + word
        try:
            # This function internaly validates the checksum
            pk = mnemonic.to_private_key(trial_mnemonic)
            addr = account.address_from_private_key(pk)
            found.append((word, addr))
        except Exception:
            continue
    return found

m24 = "ticket identify slice mirror science clean airport network cannon vote kidney coconut else toilet infant else equip only leader sniff tackle verb need yellow"
results = find_25th_word(m24)

if results:
    print(f"Found {len(results)} valid 25th words:")
    for w, a in results:
        print(f"WORD: {w} | ADDRESS: {a}")
else:
    print("NO VALID CHECKSUM WORD FOUND FOR THIS 24-WORD SEQUENCE.")

# Double check wordlist
u_words = m24.split()
all_words = mnemonic.wordlist.word_list_raw().split()
for i, uw in enumerate(u_words):
    if uw not in all_words:
        print(f"Word {i+1} '{uw}' NOT in wordlist")
