# Playwright Python image bundles browser binaries (Chromium, Firefox, WebKit)
# so the audit skill can drive headless browsers out of the box.
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Copy skill content
COPY skill/ ./skill/
COPY prompt/ ./prompt/
COPY api/ ./api/
COPY docs/ ./docs/
COPY examples/ ./examples/
COPY README.md LICENSE ./

# Install the OpenAI SDK
RUN pip install --no-cache-dir openai

# Default: run the audit CLI against stdin.
# Override with your own command when using as a base image.
CMD ["python", "api/openai_compatible.py"]
