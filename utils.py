import random
import itertools
import re
from styles import STYLISH_CHARS, NAME_STYLES

# Add common Indian/Hindi names and their stylish versions
COMMON_NAMES = {
    "heer": [
        "ʜᴇᴇʀ", "нєєя", "ℍ𝔼𝔼ℝ", "ʜᴇᴇʀ", "ђєєг", "𝓗𝓮𝓮𝓻", "Hɘɘɿ",
        "🅷🅴🅴🆁", "ℌℯℯℛ", "нєєя♡", "нєєя❤", "ʜᴇᴇʀ✨", "ʜᴇᴇʀ🌟",
        "★彡[ʜᴇᴇʀ]彡★", "༺ʜᴇᴇʀ༻", "꧁༺ʜᴇᴇʀ༻꧂", "ʜᴇᴇʀ⁣⁣", 
        "ⓗⓔⓔⓡ", "н̥e̥e̥я̥", "ﾍ乇乇尺"
    ],
    "rahul": [
        "ʀᴀʜᴜʟ", "яαнυℓ", "ℝ𝔸ℍ𝕌𝕃", "ʀᴀʜᴜʟ", "яάнцl", "𝓡𝓪𝓱𝓾𝓵", "Rαɦυʅ", 
        "🆁🅰🅷🆄🅻", "ℜαℌυℓ", "яαнυℓ♡", "яαнυℓ❤", "ʀᴀʜᴜʟ✨", "ʀᴀʜᴜʟ🌟",
        "★彡[ʀᴀʜᴜʟ]彡★", "༺ʀᴀʜᴜʟ༻", "꧁༺ʀᴀʜᴜʟ༻꧂", "ʀᴀʜᴜʟ⁣⁣", 
        "ⓡⓐⓗⓤⓛ", "я̥α̥н̥υ̥ℓ̥", "尺卂卄ㄩㄥ"
    ],
    "priya": [
        "ᴘʀɪʏᴀ", "ρяιуα", "ℙℝ𝕀𝕐𝔸", "ᴘʀɪʏᴀ", "ρяïýά", "𝓟𝓻𝓲𝔂𝓪", "Pɾιყα",
        "🅿🆁🅸🆈🅰", "ℙℛℐyα", "ρяιуα♡", "ρяιуα❤", "ᴘʀɪʏᴀ✨", "ᴘʀɪʏᴀ🌟",
        "★彡[ᴘʀɪʏᴀ]彡★", "༺ᴘʀɪʏᴀ༻", "꧁༺ᴘʀɪʏᴀ༻꧂", "ᴘʀɪʏᴀ⁣⁣", 
        "ⓟⓡⓘⓨⓐ", "ρ̥я̥ι̥у̥α̥", "卩尺丨ㄚ卂"
    ],
    "anjali": [
        "ᴀɴᴊᴀʟɪ", "αηנαℓι", "𝔸ℕ𝕁𝔸𝕃𝕀", "ᴀɴᴊᴀʟɪ", "άηjάlï", "𝓐𝓷𝓳𝓪𝓵𝓲", "Aɳʝαʅι",
        "🅰🅽🅹🅰🅻🅸", "α𝓃נαʅι", "αηנαℓι♡", "αηנαℓι❤", "ᴀɴᴊᴀʟɪ✨", "ᴀɴᴊᴀʟɪ🌟",
        "★彡[ᴀɴᴊᴀʟɪ]彡★", "༺ᴀɴᴊᴀʟɪ༻", "꧁༺ᴀɴᴊᴀʟɪ༻꧂", "ᴀɴᴊᴀʟɪ⁣⁣",
        "ⓐⓝⓙⓐⓛⓘ", "α̥η̥נ̥α̥ℓ̥ι̥", "卂几ﾌ卂ㄥ丨"
    ],
    "vikram": [
        "ᴠɪᴋʀᴀᴍ", "νιкяαм", "𝕍𝕀𝕂ℝ𝔸𝕄", "ᴠɪᴋʀᴀᴍ", "νïkгåÞ", "𝓥𝓲𝓴𝓻𝓪𝓶", "Vιƙɾαɱ",
        "🆅🅸🅺🆁🅰🅼", "√ιкяαм", "νιкяαм♡", "νιкяαм❤", "ᴠɪᴋʀᴀᴍ✨", "ᴠɪᴋʀᴀᴍ🌟",
        "★彡[ᴠɪᴋʀᴀᴍ]彡★", "༺ᴠɪᴋʀᴀᴍ༻", "꧁༺ᴠɪᴋʀᴀᴍ༻꧂", "ᴠɪᴋʀᴀᴍ⁣⁣",
        "ⓥⓘⓚⓡⓐⓜ", "ν̥ι̥к̥я̥α̥м̥", "ᐯ丨Ҝ尺卂爪"
    ],
    "neha": [
        "ɴᴇʜᴀ", "ηєнα", "ℕ𝔼ℍ𝔸", "ɴᴇʜᴀ", "ηëhά", "𝓝𝓮𝓱𝓪", "Nҽԋα",
        "🅽🅴🅷🅰", "𝓃єђα", "ηєнα♡", "ηєнα❤", "ɴᴇʜᴀ✨", "ɴᴇʜᴀ🌟",
        "★彡[ɴᴇʜᴀ]彡★", "༺ɴᴇʜᴀ༻", "꧁༺ɴᴇʜᴀ༻꧂", "ɴᴇʜᴀ⁣⁣", 
        "ⓝⓔⓗⓐ", "η̥є̥н̥α̥", "几乇卄卂"
    ],
    "arjun": [
        "ᴀʀᴊᴜɴ", "αяנυη", "𝔸ℝ𝕁𝕌ℕ", "ᴀʀᴊᴜɴ", "άгρυή", "𝓐𝓻𝓳𝓾𝓷", "Aɾʝυɳ",
        "🅰🆁🅹🆄🅽", "αяנυη", "αяנυη♡", "αяנυη❤", "ᴀʀᴊᴜɴ✨", "ᴀʀᴊᴜɴ🌟",
        "★彡[ᴀʀᴊᴜɴ]彡★", "༺ᴀʀᴊᴜɴ༻", "꧁༺ᴀʀᴊᴜɴ༻꧂", "ᴀʀᴊᴜɴ⁣⁣", 
        "ⓐⓡⓙⓤⓝ", "α̥я̥נ̥υ̥η̥", "卂尺ﾌㄩ几"
    ],
    "pooja": [
        "ᴘᴏᴏᴊᴀ", "ρσσנα", "ℙ𝕆𝕆𝕁𝔸", "ᴘᴏᴏᴊᴀ", "ρøøנά", "𝓟𝓸𝓸𝓳𝓪", "Pσσʝα",
        "🅿🅾🅾🅹🅰", "ρσσנα", "ρσσנα♡", "ρσσנα❤", "ᴘᴏᴏᴊᴀ✨", "ᴘᴏᴏᴊᴀ🌟",
        "★彡[ᴘᴏᴏᴊᴀ]彡★", "༺ᴘᴏᴏᴊᴀ༻", "꧁༺ᴘᴏᴏᴊᴀ༻꧂", "ᴘᴏᴏᴊᴀ⁣⁣", 
        "ⓟⓞⓞⓙⓐ", "ρ̥σ̥σ̥נ̥α̥", "卩ㄖㄖﾌ卂"
    ],
    "aditya": [
        "ᴀᴅɪᴛʏᴀ", "α∂ιтуα", "𝔸𝔻𝕀𝕋𝕐𝔸", "ᴀᴅɪᴛʏᴀ", "άÐïţ¥å", "𝓐𝓭𝓲𝓽𝔂𝓪", "Aԃιƚყα",
        "🅰🅳🅸🆃🆈🅰", "α∂ιтуα", "α∂ιтуα♡", "α∂ιтуα❤", "ᴀᴅɪᴛʏᴀ✨", "ᴀᴅɪᴛʏᴀ🌟",
        "★彡[ᴀᴅɪᴛʏᴀ]彡★", "༺ᴀᴅɪᴛʏᴀ༻", "꧁༺ᴀᴅɪᴛʏᴀ༻꧂", "ᴀᴅɪᴛʏᴀ⁣⁣", 
        "ⓐⓓⓘⓣⓨⓐ", "α̥∂̥ι̥т̥у̥α̥", "卂ᗪ丨ㄒㄚ卂"
    ],
    "sandeep": [
        "sᴀɴᴅᴇᴇᴘ", "ѕαη∂єєρ", "𝕊𝔸ℕ𝔻𝔼𝔼ℙ", "sᴀɴᴅᴇᴇᴘ", "šåήÐêëþ", "𝓢𝓪𝓷𝓭𝓮𝓮𝓹", "Sαɳԃҽҽρ",
        "🆂🅰🅽🅴🅴🅿", "ѕαη∂єєρ", "ѕαη∂єєρ♡", "ѕαη∂єєρ❤", "sᴀɴᴅᴇᴇᴘ✨", "sᴀɴᴅᴇᴇᴘ🌟",
        "★彡[sᴀɴᴅᴇᴇᴘ]彡★", "༺sᴀɴᴅᴇᴇᴘ༻", "꧁༺sᴀɴᴅᴇᴇᴘ༻꧂", "sᴀɴᴅᴇᴇᴘ⁣⁣", 
        "ⓢⓐⓝⓓⓔⓔⓟ", "ѕ̥α̥η̥∂̥є̥є̥ρ̥", "丂卂几ᗪ乇乇卩"
    ],
}

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

def format_styled_name(text, style_template):
    """Format text using a style template with {name} placeholder."""
    try:
        # Replace {name} in the template with the actual text
        return style_template.replace("{name}", text)
    except Exception as e:
        # If formatting fails, return the original text
        return text

def generate_name_combinations(text, max_combos=25):
    """Generate combinations for names using only stylized characters."""
    # Normalize and clean the text
    text_clean = text.lower().strip()
    
    combinations = []
    matched_name = None
    
    # Helper function to ensure every character is stylized
    def stylize_text(input_text):
        styled = ""
        for char in input_text:
            if char.lower() in STYLISH_CHARS and len(STYLISH_CHARS[char.lower()]) > 0:
                # Always replace with a random stylized character
                styled += random.choice(STYLISH_CHARS[char.lower()])
            else:
                # For characters not in STYLISH_CHARS, keep as is
                styled += char
        return styled
    
    # Generate fully stylized combinations
    for _ in range(15):
        styled = stylize_text(text)
        if styled not in combinations:
            combinations.append(styled)
    
    # Check if the text is a common name with predefined styles
    for name, styles in COMMON_NAMES.items():
        # Check if input is this name or contains this name
        if name == text_clean or name in text_clean:
            matched_name = name
            # Add the predefined styles for this name
            for style in styles[:min(5, max_combos)]:
                if style not in combinations:
                    combinations.append(style)
    
    # Add name template styles with stylized text
    for i in range(min(5, len(NAME_STYLES))):
        try:
            # Generate a stylized version of the text first
            styled_text = stylize_text(text)
            # Then apply the template
            styled = format_styled_name(styled_text, NAME_STYLES[i])
            if styled not in combinations:
                combinations.append(styled)
        except Exception:
            pass
    
    # Add decorated stylized versions
    decorations = [
        "✨ {} ✨", "🌟 {} 🌟", "💫 {} 💫", "⭐ {} ⭐", 
        "🔥 {} 🔥", "💖 {} 💖", "🌈 {} 🌈", "🦋 {} 🦋",
        "{}✨", "{}🌟", "{}💫", "{}⭐", "{}🔥",
        "★彡 {} 彡★", "꧁༺ {} ༻꧂", "•°♪ {} ♪°•", "♡ {} ♡"
    ]
    
    # Fill remaining slots with decorated stylized text
    remaining_slots = max_combos - len(combinations)
    if remaining_slots > 0:
        for i in range(min(remaining_slots, len(decorations))):
            # Always create a new stylized version
            styled_text = stylize_text(text)
            decorated = decorations[i].format(styled_text)
            if decorated not in combinations:
                combinations.append(decorated)
    
    # If we still don't have enough combinations, create more random ones
    seen = set(combinations)
    while len(combinations) < max_combos:
        styled = stylize_text(text)
        if styled not in seen:
            seen.add(styled)
            combinations.append(styled)
    
    return combinations[:max_combos]

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
                # Use all variants for more diversity
                char_options.append(variants)  
            else:
                # For lowercase, use lowercase variants
                variants = STYLISH_CHARS[char]
                # Add the original char at the beginning
                variants.insert(0, char)
                # Use all variants for more diversity
                char_options.append(variants)
        else:
            # For non-alphabet characters, only one option - the character itself
            char_options.append([char])
    
    # First add the original text
    styled_variations.append(text)
    
    # Create a systematic 5x5 grid (25 combinations)
    # Use different approaches to create variety
    
    # Approach 1: Generate combinations where each character is styled
    for i in range(min(10, max_combos - len(styled_variations))):
        styled_chars = []
        for char_idx, variants in enumerate(char_options):
            if len(variants) > 1:  # If there are style options
                # Choose a random variant different from the original if possible
                non_original = [v for v in variants if v != text[char_idx]]
                if non_original:
                    styled_chars.append(random.choice(non_original))
                else:
                    styled_chars.append(text[char_idx])
            else:
                styled_chars.append(text[char_idx])
        
        styled_text = ''.join(styled_chars)
        # Only add if this is a new variation
        if styled_text not in styled_variations:
            styled_variations.append(styled_text)
    
    # Approach 2: Style one character at a time
    for char_idx, char in enumerate(text):
        if char.lower() in STYLISH_CHARS and len(STYLISH_CHARS[char.lower()]) > 0:
            # Use multiple different styles for this character
            max_styles = min(5, len(STYLISH_CHARS[char.lower()]))
            style_indices = random.sample(range(len(STYLISH_CHARS[char.lower()])), min(max_styles, len(STYLISH_CHARS[char.lower()])))
            
            for style_idx in style_indices:
                new_text = list(text)
                new_text[char_idx] = STYLISH_CHARS[char.lower()][style_idx]
                styled_text = ''.join(new_text)
                
                # Only add if this is a new variation
                if styled_text not in styled_variations:
                    styled_variations.append(styled_text)
                    
                # If we have enough variations, stop
                if len(styled_variations) >= max_combos:
                    return styled_variations[:max_combos]
    
    # Approach 3: Style pairs of characters simultaneously
    if len(text) >= 2:
        for i in range(0, len(text) - 1):
            for j in range(i + 1, len(text)):
                if (text[i].lower() in STYLISH_CHARS and len(STYLISH_CHARS[text[i].lower()]) > 0 and
                    text[j].lower() in STYLISH_CHARS and len(STYLISH_CHARS[text[j].lower()]) > 0):
                    
                    # Choose random styles for both characters
                    style_i = random.choice(STYLISH_CHARS[text[i].lower()])
                    style_j = random.choice(STYLISH_CHARS[text[j].lower()])
                    
                    new_text = list(text)
                    new_text[i] = style_i
                    new_text[j] = style_j
                    styled_text = ''.join(new_text)
                    
                    # Only add if this is a new variation
                    if styled_text not in styled_variations:
                        styled_variations.append(styled_text)
                        
                    # If we have enough variations, stop
                    if len(styled_variations) >= max_combos:
                        return styled_variations[:max_combos]
    
    # Approach 4: Create fully randomized combinations until we reach max_combos
    while len(styled_variations) < max_combos:
        styled_chars = []
        for i, variants in enumerate(char_options):
            # Randomly choose a variant for each character
            styled_chars.append(random.choice(variants))
            
        styled_text = ''.join(styled_chars)
        if styled_text not in styled_variations:
            styled_variations.append(styled_text)
    
    # Make sure we return exactly max_combos combinations or all available if fewer
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