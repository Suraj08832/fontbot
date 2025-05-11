import random
import itertools
from styles import STYLISH_CHARS, NAME_STYLES

def get_random_style():
    """Get a random style from the predefined styles."""
    return random.choice(NAME_STYLES)

def get_all_styles():
    """Get all available styles."""
    return NAME_STYLES

def transform_text(text, style_map):
    """Transform text according to a style map."""
    result = ""
    for char in text:
        result += style_map.get(char.lower(), char)
    return result

def create_custom_style(text, style_map):
    """Create a custom style for the given text."""
    return transform_text(text, style_map)

def get_stylish_char_by_index(char, style_index):
    """Get a stylish character by style index."""
    if char.lower() in STYLISH_CHARS and style_index < len(STYLISH_CHARS[char.lower()]):
        return STYLISH_CHARS[char.lower()][style_index]
    return char

def generate_style_permutations(text, max_combos=25):
    """Generate combinations of styled characters for a given text."""
    styled_variations = []
    
    # For each character in the text, get all possible styled variants
    char_options = []
    for char in text:
        if char.lower().isalpha() and char.lower() in STYLISH_CHARS:
            # Get styles for this character
            if char.isupper():
                # For uppercase, get lowercase variants and convert to uppercase
                variants = [v.upper() if v.isalpha() else v for v in STYLISH_CHARS[char.lower()]]
                # Add the original uppercase char at the beginning
                variants.insert(0, char)
                char_options.append(variants[:3])  # Limit to 3 variants to manage combinations
            else:
                # For lowercase, use lowercase variants
                variants = STYLISH_CHARS[char]
                # Add the original char at the beginning
                variants.insert(0, char)
                char_options.append(variants[:3])  # Limit to 3 variants to manage combinations
        else:
            # For non-alphabet characters, only one option - the character itself
            char_options.append([char])
    
    # Generate systematic combinations for short texts
    if len(char_options) <= 4:  # For short words, try more combinations
        for combo in itertools.product(*char_options):
            styled_text = ''.join(combo)
            styled_variations.append(styled_text)
            if len(styled_variations) >= max_combos:
                break
    else:
        # For longer texts, use randomized approach to avoid too many combinations
        # First add the original text
        styled_variations.append(text)
        
        # Then add some varied styles where each character might be styled
        attempt_count = 0
        max_attempts = max_combos * 3  # Limit attempts to avoid infinite loops
        
        while len(styled_variations) < max_combos and attempt_count < max_attempts:
            attempt_count += 1
            
            # Create a random styled variation
            styled_chars = []
            for i, variants in enumerate(char_options):
                # Randomly decide whether to style this character
                if random.random() > 0.5 or len(variants) <= 1:
                    # Keep original character
                    styled_chars.append(text[i])
                else:
                    # Choose a random variant different from the original
                    non_original = [v for v in variants if v != text[i]]
                    if non_original:
                        styled_chars.append(random.choice(non_original))
                    else:
                        styled_chars.append(text[i])
            
            styled_text = ''.join(styled_chars)
            
            # Only add if this is a new variation and differs from original
            if styled_text != text and styled_text not in styled_variations:
                styled_variations.append(styled_text)
    
    # If we still don't have enough variations, add some fully random ones
    while len(styled_variations) < max_combos and len(styled_variations) < 2**len(text):
        styled_chars = []
        for i, variants in enumerate(char_options):
            styled_chars.append(random.choice(variants))
            
        styled_text = ''.join(styled_chars)
        if styled_text not in styled_variations:
            styled_variations.append(styled_text)
    
    return styled_variations[:max_combos]

def get_stylish_char(char):
    """Get a random stylish character for the given character."""
    char = char.lower()
    if char in STYLISH_CHARS:
        return random.choice(STYLISH_CHARS[char])
    return char

def create_custom_style(text):
    """Create a custom style by replacing each character with a stylish version."""
    styled_text = ''.join(get_stylish_char(c) for c in text)
    
    # Check if styling actually changed the text
    if styled_text == text:
        # If no change, add some decorative elements
        prefix = random.choice(["✨ ", "🌟 ", "💫 ", "✦ ", "⭐ "])
        suffix = random.choice([" ✨", " 🌟", " 💫", " ✦", " ⭐"])
        styled_text = f"{prefix}{text}{suffix}"
    
    return styled_text

def get_stylish_char_by_index(char, index=0):
    """Get a specific stylish character by index."""
    char = char.lower()
    if char in STYLISH_CHARS:
        if 0 <= index < len(STYLISH_CHARS[char]):
            return STYLISH_CHARS[char][index]
        else:
            # Return first style if index out of range
            return STYLISH_CHARS[char][0]
    return char 