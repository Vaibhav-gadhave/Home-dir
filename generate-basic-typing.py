#!/usr/bin/env python3
import os
import re
import subprocess
import string

TARGET_FILE = os.path.expanduser("~/desktop_typing_practice.txt")

def fetch_wikit_text(topic):
    """Executes the native wikit tool and cleans out all hidden terminal styling layout codes."""
    try:
        result = subprocess.run(f"wikit {topic}", shell=True, capture_output=True, text=True, timeout=5)
        raw_output = result.stdout.strip()
        
        if not raw_output:
            return ""
            
        # Strip hidden ANSI terminal colors and brackets
        ansi_cleaner = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_text = ansi_cleaner.sub('', raw_output)
        
        # Strip trailing system navigation warnings added by the utility binary
        clean_text = re.sub(r'Press .* to view more', '', clean_text, flags=re.IGNORECASE)
        
        return clean_text
    except Exception as e:
        print(f"⚠️ Process Error: {e}")
    return ""

def clean_numbers_and_symbols(text_block):
    """Directly strips numbers, attached digits, and isolated math/currency symbols from the text flow."""
    if not text_block:
        return ""
        
    # Remove citation brackets like, [2]
    text = re.sub(r'\[[^\]]*\]', '', text_block)
    text = text.replace('\n', ' ').replace('\r', ' ')
    
    # 1. Strip standalone digits, percentages, and currencies (e.g., 2005, 14%, $50billion, $31.7billion)
    # This regular expression target identifies any word containing a number and wipes it out completely
    words = text.split()
    clean_words = []
    
    for word in words:
        # If the word contains ANY number (0-9) or stray isolated symbols like $, %, or €, skip it
        if re.search(r'[0-9]', word) or word in ['$', '%', '€', '£', '+', '=', '-', '/', '*', '(', ')']:
            continue
        clean_words.append(word)
        
    processed_text = " ".join(clean_words)
    
    # 2. Clean up punctuation artifacts left behind by the deleted numbers
    # Fixes empty dangling commas or double spaces (e.g., "day. , videos" becomes "day. videos")
    processed_text = re.sub(r'\s+,\s+', ' ', processed_text)
    processed_text = re.sub(r'\s+\.\s+', ' ', processed_text)
    processed_text = re.sub(r'\s+', ' ', processed_text).strip()
    
    return processed_text

def generate_pure_wikit_text():
    accumulated_text = ""
    
    print("==================================================")
    print("  WIKIT DIRECT TEXT EXTRACTOR (WORD-LEVEL FILTER) ")
    print("==================================================")
    
    while True:
        topic = input("📝 Enter a topic for your text layout (e.g., youtube): ").strip()
        if not topic:
            print("⚠️ Topic cannot be empty. Please enter a valid term.")
            continue
            
        print(f"🔍 Fetching raw data from wikit for: '{topic}'...")
        raw_text = fetch_wikit_text(topic)
        
        # Strip individual numbers and symbols directly
        clean_segment = clean_numbers_and_symbols(raw_text)
        
        if not clean_segment or "not found" in clean_segment.lower():
            print("⚠️ No valid text found for that topic. Please enter a different term.")
            print("--------------------------------------------------")
            continue
            
        # Append the new text segment cleanly
        if accumulated_text:
            accumulated_text += " " + clean_segment
        else:
            accumulated_text = clean_segment
            
        words_array = accumulated_text.split()
        current_count = len(words_array)
        
        # Check against your strict training boundaries
        if current_count >= 200:
            break
        else:
            print(f"ℹ️ Current text yields only {current_count} words after filtering numbers/symbols.")
            print("💡 Please enter an additional topic to reach 200-220 words.")
            print("--------------------------------------------------")

    # Final layout constraint trimming
    words_list = accumulated_text.split()
    
    if len(words_list) > 220:
        print("✂️ Trimming text layout down to the strict 220 word ceiling...")
        words_list = words_list[:215]
        
    final_paragraph = " ".join(words_list)
    
    # Force fix the trailing punctuation marker if sliced abruptly
    if not final_paragraph.endswith('.'):
        final_paragraph = final_paragraph.rstrip(string.punctuation) + "."
        
    return final_paragraph, len(final_paragraph.split())

# Execute data extraction pipeline instantly
final_text, final_word_count = generate_pure_wikit_text()

with open(TARGET_FILE, "w") as f_out:
    f_out.write(final_text + "\n")

print("\n==================================================")
print(f"✨ Success! Raw text file written to: {TARGET_FILE}")
print(f"📊 Total Word Count: {final_word_count} words.")
print("==================================================")
