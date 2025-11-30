import os
import sys
import logging
from src.core.logger import setup_logger
from src.data.state_manager import StateManager
from src.data.file_system import FileSystem
from src.data.crm import CRMMock
from src.ai.analyzer import AIAnalyzer

# Configuration
BATCH_SIZE = 50
WORKDRIVE_ROOT = "workdrive_mock"

def main():
    logger = setup_logger()
    logger.info("Starting Document Processor...")

    # 1. Initialize Components
    state_manager = StateManager()
    fs = FileSystem(WORKDRIVE_ROOT)
    crm = CRMMock()
    analyzer = AIAnalyzer()

    # 2. Get Files
    all_files = fs.list_files()
    logger.info(f"Found {len(all_files)} total files in {WORKDRIVE_ROOT}")

    # 3. Filter Unprocessed
    files_to_process = state_manager.get_unprocessed_files(all_files, limit=BATCH_SIZE)
    if not files_to_process:
        logger.info("No new files to process. Exiting.")
        return

    logger.info(f"Processing batch of {len(files_to_process)} files.")

    processed_successfully = []

    # 4. Process Loop
    for rel_path in files_to_process:
        logger.info(f"Processing: {rel_path}")

        try:
            # A. Extract Context (Folder CF)
            potential_cf = fs.extract_fiscal_code_from_path(rel_path)

            # B. Convert to Images
            images = fs.convert_to_base64_images(rel_path)

            if not images:
                logger.warning(f"Could not convert {rel_path} to images (or empty). Skipping analysis.")
                # We still mark it as processed to avoid infinite loops on bad files
                processed_successfully.append(rel_path)
                continue

            # C. AI Analysis
            result = analyzer.analyze_document(images, potential_cf=potential_cf)
            logger.info(f"Analyzed {rel_path}: Type={result.document_type}, CF={result.personal_info.fiscal_code}")

            # D. Save to CRM
            crm.save_data(rel_path, result)

            processed_successfully.append(rel_path)

        except Exception as e:
            logger.error(f"Failed to process {rel_path}: {e}")
            # Decision: Do we mark failed files as processed?
            # Usually yes to avoid blocking the queue, but maybe log to a 'failed' list.
            # For this MVP, we mark them processed so the job proceeds.
            processed_successfully.append(rel_path)

    # 5. Update State
    if processed_successfully:
        state_manager.mark_files_as_processed(processed_successfully)
        logger.info(f"Batch complete. Marked {len(processed_successfully)} files as processed.")

if __name__ == "__main__":
    main()
