import re

def clean_indonesian_for_xtts(text):
    """
    Indonesian Text Normalization for XTTS.
    Fixes abbreviations, numbers, and symbols to follow KBBI rules.
    """
    if not text:
        return ""
    
    # 1. Lowercase for consistency
    text = text.lower()
    
    # 2. Expand common abbreviations (Slang/Chat)
    abbreviations = {
        r'\byg\b': 'yang',
        r'\bdngn\b': 'dengan',
        r'\bkm\b': 'kamu',
        r'\bsdh\b': 'sudah',
        r'\btlh\b': 'telah',
        r'\bbwt\b': 'buat',
        r'\badlh\b': 'adalah',
        r'\bdp\b': 'di',
        r'\bjkt\b': 'jakarta',
        r'\butk\b': 'untuk',
        r'\bgk\b': 'tidak',
        r'\bgak\b': 'tidak',
        r'\bgda\b': 'tidak ada',
        r'\bmsh\b': 'masih',
        r'\bkrn\b': 'karena',
        r'\btp\b': 'tapi',
        r'\btetapi\b': 'tetapi',
        r'\bsy\b': 'saya',
        r'\bak\b': 'aku',
        r'\bjgn\b': 'jangan',
        r'\blg\b': 'lagi',
        r'\bsaja\b': 'saja',
        r'\bsj\b': 'saja',
        r'\baja\b': 'saja',
        r'\bdr\b': 'dari',
        r'\btdk\b': 'tidak',
    }
    
    for pattern, replacement in abbreviations.items():
        text = re.sub(pattern, replacement, text)
    
    # 3. Currency expansion (Rp 10.000 -> 10000 rupiah)
    text = re.sub(r'rp\s?([\d.]+)', lambda x: x.group(1).replace('.', '') + ' rupiah', text)
    
    # 4. Number expansion (very basic for now, XTTS usually handles digits ok but needs clarity)
    # XTTS sometimes struggles with Indonesian numbers, but let's keep them as is unless problematic
    
    # 5. Fix repetitive vowels/consonants often used in chat (e.g. "halooo" -> "halo")
    text = re.sub(r'(.)\1{2,}', r'\1', text)
    
    # 6. Normalize punctuation (remove weird characters, keep basic ones)
    text = re.sub(r'[^a-z0-9\s,.!?]', ' ', text)
    
    # 7. Strategic pauses
    if len(text.split()) > 15 and ',' not in text:
        words = text.split()
        mid = len(words) // 2
        words[mid] = words[mid] + ','
        text = ' '.join(words)
        
    # 8. Phonetic Tweaks for English Bridge (Optional but helps)
    # Some Indonesian sounds are better interpreted by the EN engine with slight spelling changes
    # But we have to be CAREFUL not to overdo it.
    phonetic_fixes = {
        r'\bakreditasi\b': 'akreditasi', # Example: ensure correct vowel focus
        # r'e': 'eh', # Dangerous, but can be used for specific problematic words
    }
    
    for pattern, replacement in phonetic_fixes.items():
        text = re.sub(pattern, replacement, text)

    return text.strip()

if __name__ == "__main__":
    # Test
    test_text = "Sdh jm 10, sy blm mkn. Rp 50.000 buat beli baksooo di JKT."
    print(f"Original: {test_text}")
    print(f"Cleaned:  {clean_indonesian_for_xtts(test_text)}")
