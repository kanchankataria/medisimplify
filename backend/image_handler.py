import base64
from PIL import Image
import io

# Maximum image size Claude accepts (5MB)
MAX_SIZE_BYTES = 5 * 1024 * 1024


def get_media_type(filename: str) -> str:
    """Detect media type from filename"""
    filename = filename.lower()
    if filename.endswith(".jpg") or filename.endswith(".jpeg"):
        return "image/jpeg"
    elif filename.endswith(".png"):
        return "image/png"
    elif filename.endswith(".gif"):
        return "image/gif"
    elif filename.endswith(".webp"):
        return "image/webp"
    else:
        return "image/png"  # default


def resize_image_if_needed(image_bytes: bytes) -> bytes:
    """
    Resize image if it exceeds Claude's size limit.
    Why: Claude API rejects images larger than 5MB.
    """
    if len(image_bytes) <= MAX_SIZE_BYTES:
        return image_bytes

    # Open image and reduce quality
    img = Image.open(io.BytesIO(image_bytes))

    # Convert to RGB if needed (handles RGBA PNG files)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Resize to 70% until under size limit
    quality = 85
    while True:
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        result = buffer.getvalue()
        if len(result) <= MAX_SIZE_BYTES or quality < 30:
            return result
        quality -= 10


def prepare_image_for_claude(image_bytes: bytes, filename: str) -> tuple:
    """
    Prepare image for Claude Vision API.
    Returns: (base64_string, media_type)
    """
    # Resize if needed
    processed_bytes = resize_image_if_needed(image_bytes)

    # Get media type
    media_type = get_media_type(filename)

    # Convert to base64
    base64_string = base64.standard_b64encode(processed_bytes).decode("utf-8")

    return base64_string, media_type


def validate_image(filename: str) -> bool:
    """
    Check if uploaded file is a supported image type.
    Why: We don't want users uploading random files.
    """
    supported = [".jpg", ".jpeg", ".png", ".webp", ".gif"]
    filename_lower = filename.lower()
    return any(filename_lower.endswith(ext) for ext in supported)
