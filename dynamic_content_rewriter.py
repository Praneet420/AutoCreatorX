# dynamic_content_rewriter.py

import logging
from transformers import pipeline

class DynamicContentRewriter:
    def __init__(self):
        self.logger = logging.getLogger("DynamicContentRewriter")
        try:
            self.rewriter = pipeline("text2text-generation", model="google/flan-t5-base")
            self.logger.info("Content rewriter model loaded successfully.")
        except Exception as e:
            self.rewriter = None
            self.logger.error(f"Failed to load model: {e}")

    def rewrite(self, text, tone="neutral"):
        if not self.rewriter:
            self.logger.warning("Rewriter model not loaded.")
            return text

        prompt = f"Rewrite the following in a {tone} tone:\n{text}"
        try:
            rewritten = self.rewriter(prompt, max_length=256, do_sample=False)
            return rewritten[0]['generated_text']
        except Exception as e:
            self.logger.error(f"Rewrite failed: {e}")
            return text
