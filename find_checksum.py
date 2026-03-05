from algosdk import mnemonic, account
import os

def find_25th_word(m24_str):
    m24_list = m24_str.split()
    if len(m24_list) != 24:
        return f"Error: Expected 24 words, got {len(m24_list)}"
    
    # Get the official wordlist
    words = mnemonic.wordlist.word_list_raw().split()
    
    for word in words:
        trial_mnemonic = m24_str + " " + word
        try:
            pk = mnemonic.to_private_key(trial_mnemonic)
            addr = account.address_from_private_key(pk)
            # Optional: Check if the derived address matches the user's provided address
            if addr == "KKWXTEIXQ5GFMFF67FXXIHFQQPE4XIUU42CH4HKVKWTS5XRAUV7G664Z5U":
                return word, addr, trial_mnemonic
            # If user didn't provide address or just want the correct checksum
            # For now, let's just return the first one that validates
            # but ideally we match the intended address.
            # In this case, we have the address "KKWXTEIX..."
        except Exception:
            continue
    
    # If no exact match found for address, but we found a valid checksum
    for word in words:
        trial_mnemonic = m24_str + " " + word
        try:
            pk = mnemonic.to_private_key(trial_mnemonic)
            addr = account.address_from_private_key(pk)
            return word, addr, trial_mnemonic
        except Exception:
            continue
            
    return None

m24 = "ticket identify slice mirror science clean airport network cannon vote kidney coconut else toilet infant else equip only leader sniff tackle verb need yellow"
result = find_25th_word(m24)

if result:
    word, addr, full_m = result
    print(f"FOUND_WORD: {word}")
    print(f"DERIVED_ADDRESS: {addr}")
    print(f"FULL_MNEMONIC: {full_m}")
else:
    print("No valid checksum found.")
