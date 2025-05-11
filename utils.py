import random
from styles import STYLISH_CHARS, NAME_STYLES

def get_random_style():
    """Get a random style from the predefined styles."""
    return random.choice(NAME_STYLES)

def transform_text(text, style=None):
    """Transform text using the given style or a random one."""
    if style is None:
        style = get_random_style()
    
    # Try to format with the style
    try:
        styled_text = style.format(name=text)
        
        # Check if styling actually changed the text
        if styled_text == text:
            # If no change, add some decorative elements
            prefix = random.choice(["✨ ", "🌟 ", "💫 ", "✦ ", "⭐ "])
            suffix = random.choice([" ✨", " 🌟", " 💫", " ✦", " ⭐"])
            styled_text = f"{prefix}{text}{suffix}"
        
        return styled_text
    except Exception as e:
        # If formatting fails, add decorations to original text
        prefix = random.choice(["✨ ", "🌟 ", "💫 ", "✦ ", "⭐ "])
        suffix = random.choice([" ✨", " 🌟", " 💫", " ✦", " ⭐"])
        return f"{prefix}{text}{suffix}"

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

def get_all_styles():
    """Get all available styles."""
    return NAME_STYLES

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