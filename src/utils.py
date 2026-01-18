import io
from PIL import Image
from .config import config


def validate_image(image_data, max_size_mb=None):
    max_size = max_size_mb or config.MAX_IMAGE_SIZE_MB
    size_mb = len(image_data) / (1024 * 1024)
    
    if size_mb > max_size:
        return False, f"Image too large ({size_mb:.1f}MB). Max: {max_size}MB"
    
    try:
        img = Image.open(io.BytesIO(image_data))
        img.verify()
    except Exception as e:
        return False, f"Invalid image: {str(e)}"
    
    return True, None


def resize_image_if_needed(image_data, max_dim=2048):
    image = Image.open(io.BytesIO(image_data))
    
    if max(image.size) <= max_dim:
        return image_data
    
    ratio = max_dim / max(image.size)
    new_size = tuple(int(d * ratio) for d in image.size)
    resized = image.resize(new_size, Image.Resampling.LANCZOS)
    
    output = io.BytesIO()
    resized.save(output, format=image.format or 'JPEG', quality=90)
    return output.getvalue()


def get_image_mime_type(image_data):
    try:
        image = Image.open(io.BytesIO(image_data))
        types = {'JPEG': 'image/jpeg', 'PNG': 'image/png', 'GIF': 'image/gif', 'WEBP': 'image/webp'}
        return types.get(image.format, 'image/jpeg')
    except:
        return 'image/jpeg'


def format_number(n):
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    elif n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return f"{n:.0f}"


def get_relatable_comparison(total_liters):
    showers = total_liters / 95
    drinking_days = total_liters / config.DAILY_DRINKING_WATER_LITERS
    pools = total_liters / 90_000
    
    if pools >= 1:
        return f"{pools:.1f} swimming pools" if pools < 10 else f"{pools:.0f} swimming pools"
    elif drinking_days >= 365:
        years = drinking_days / 365
        return f"{years:.1f} years of drinking water" if years < 10 else f"{years:.0f} years of drinking water"
    elif drinking_days >= 30:
        return f"{drinking_days:.0f} days of drinking water"
    elif showers >= 1:
        return f"{showers:.0f} ten-minute showers"
    return f"{total_liters:.0f} glasses of water"


def get_disclaimer():
    return "**📋 Note:** Estimates based on Water Footprint Network global averages. For educational purposes."


def get_category_icon(category):
    icons = {
        'textiles': '👕', 'food': '🍽️', 'electronics': '📱', 'agriculture': '🌾',
        'paper': '📄', 'transport': '🚗', 'beverages': '☕', 'other': '📦'
    }
    return icons.get(category.lower(), '📦')


def get_impact_level(total_liters):
    if total_liters < 100:
        return "Very Low", "#4CAF50", "Minimal water impact 👍"
    elif total_liters < 1000:
        return "Low", "#8BC34A", "Pretty good water footprint"
    elif total_liters < 5000:
        return "Moderate", "#FFC107", "Consider some alternatives"
    elif total_liters < 15000:
        return "High", "#FF9800", "That's a lot of water!"
    return "Very High", "#F44336", "Major water footprint 😬"
