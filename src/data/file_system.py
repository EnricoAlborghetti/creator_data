import os
import re
import base64
from typing import List, Optional, Tuple
from PIL import Image
import io

# Try importing pdf2image, but handle if it fails due to missing poppler
try:
    from pdf2image import convert_from_path
    PDF_SUPPORT = True
except (ImportError, Exception):
    PDF_SUPPORT = False

class FileSystem:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    def list_files(self) -> List[str]:
        """Recursively list all files in the root directory."""
        file_list = []
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                # Store relative paths to keep state clean
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.root_dir)
                file_list.append(rel_path)
        return sorted(file_list)  # Sort for consistent processing order

    def extract_fiscal_code_from_path(self, file_path: str) -> Optional[str]:
        """
        Attempts to find a Fiscal Code in the directory structure.
        Regex matches standard Italian CF format: 6 letters, 2 digits, 1 letter, 2 digits, 1 letter, 3 digits, 1 letter.
        """
        # Standard Italian Fiscal Code Regex
        cf_pattern = re.compile(r'[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]', re.IGNORECASE)

        parts = file_path.split(os.sep)
        for part in parts:
            match = cf_pattern.search(part)
            if match:
                return match.group(0).upper()
        return None

    def convert_to_base64_images(self, rel_path: str) -> List[str]:
        """
        Converts a file to a list of base64 encoded images.
        - Images: Returns single item list.
        - PDF: Returns list of images (one per page).
        """
        full_path = os.path.join(self.root_dir, rel_path)
        ext = os.path.splitext(full_path)[1].lower()

        images_b64 = []

        try:
            if ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.webp']:
                with Image.open(full_path) as img:
                    # Convert to RGB to ensure compatibility
                    if img.mode != 'RGB':
                        img = img.convert('RGB')

                    # Resize if too large to save tokens/bandwidth (optional optimization)
                    # img.thumbnail((1024, 1024))

                    buffered = io.BytesIO()
                    img.save(buffered, format="JPEG")
                    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                    images_b64.append(img_str)

            elif ext == '.pdf':
                if not PDF_SUPPORT:
                    print(f"Warning: Poppler not found. Skipping PDF rendering for {rel_path}. Processing as path/metadata only.")
                    return []

                try:
                    # distinct poppler path if needed, but assuming default path or fail
                    images = convert_from_path(full_path)
                    for img in images:
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        buffered = io.BytesIO()
                        img.save(buffered, format="JPEG")
                        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                        images_b64.append(img_str)
                except Exception as e:
                    print(f"Error converting PDF {rel_path}: {e}")

            return images_b64

        except Exception as e:
            print(f"Error processing file {rel_path}: {e}")
            return []
