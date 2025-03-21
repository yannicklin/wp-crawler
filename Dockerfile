FROM python:3.11

# Install dependencies
COPY ./requirements.txt ./
RUN pip3 install -r requirements.txt \
    && playwright install-deps

# Configure filesystem
WORKDIR /usr/src/app

# Add the user
RUN useradd runner
RUN mkdir -p /usr/src/app/output \
    && mkdir -p /home/runner \
    && mkdir -p /usr/src/app/wordpress/har-output \
    && mkdir -p /usr/src/app/wordpress/traces \
    && chown -R runner /usr/src/app \
    && chown -R runner /home/runner

# Copy files
COPY --chown=runner:runner ./webserver ./webserver
COPY --chown=runner:runner ./wordpress ./wordpress
COPY --chown=runner:runner ./settings.py ./
COPY --chown=runner:runner ./bin ./bin

# Expose chromium to the scraping script in userspace
USER runner
RUN playwright install chromium
CMD ["bash", "./bin/run_scrape.sh"]
