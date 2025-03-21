import json
import os
import sys
import argparse
from collections import defaultdict

har_file_path = os.path.join(os.getcwd(), "har-output", "log.har") 

# Stores a list of error details per status.
errors = defaultdict(list)

# Parse arguments
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--isPrValidation", type=str, required=False, default="False")
    parser.add_argument("--ignoreErrors", type=str, required=False, default="False")
    return parser.parse_args()

# Convert arguments to bool from string
def convert_to_bool(*args):
    return tuple(arg.lower() == "true" for arg in args)

# Iterate through the HAR file, pull out (final) HTTP requests/responses that resulted in a status code other than 2xx.
# 'errors' is populated with the response status code, request url, and response content type.
def process_har_file(har_file):
    with open(har_file, 'r') as har_f:
        data = json.load(har_f)


    # dictionary to store each requested URL and the status, content type, and timestamp from the final response in the HAR file
    failed_requests = {}

    # Iterate through the HAR file, and retrieve status (http code), url (requested), timestamp (of request), 
    # and the content type (js, css, html, etc.)
    for entry in data["log"]["entries"]:
        status = entry["response"]["status"]
        url = entry["request"]["url"]
        timestamp = entry["startedDateTime"]
        content_type = next((header["value"] for header in entry["response"]["headers"] if header["name"].lower() == "content-type"), "unknown")

        # Store as tuple using url as key so as to group requests by url.
        # Compare duplicate URLs timestamps to get most recent request - this is to handle retries
        if url not in failed_requests or timestamp > failed_requests[url]["timestamp"]:
            failed_requests[url] = {"status": status, "content_type": content_type, "timestamp": timestamp}

    # Iterate through the remaining non duplicate URLs/requests, add only non-2xx responses to errors
    # and group by status to provide a summary of counts by status
    for url, data in failed_requests.items():
        if data["status"] < 200 or data["status"] >= 300:
            errors[data["status"]].append({
                "url": url,
                "content_type": data["content_type"]
            })

# Iterate through 'errors' and print a count of each status code.
# Also print a list of URLs and content types under each status code.
def print_error_summary(is_pr_validation, ignore_errors):
    # bool to error out the pipeline if set to True
    stop_pipeline = False

    if not errors:
        print("No HTTP errors (non 2xx) found.")
        return

    # print a summary with counts of each status code
    print("\nHTTP Error Code Counts:\n")
    for status, details in sorted(errors.items()):
        print(f"{status}: {len(details)} occurrence(s)")
        
        # if a 5xx status is seen, set stopPipeline to True so that the script exits and fails the build once the errors have finished reporting
        if status >= 500:
            stop_pipeline = True

    # print a detailed section containing urls and content type grouped by status code
    print("-" * 50 + "\n\nDetailed Error List:")
    for status, details in sorted(errors.items()):
        if status != -1:
            print(f"\nStatus: {status}\n")
            for error in sorted(details, key=lambda e: e["content_type"]):  # Sort by content type
                print(f"  [{error['content_type']}] {error['url']}")
            print("-" * 50)

    # stop the pipeline if stop_pipeline has been set to true by the above logic AND
    # ignore_errors hasn't been set to true and this isn't a PR validation run
    if not(is_pr_validation or ignore_errors) and stop_pipeline:
        print("Non-safe error (5xx) detected. Stopping pipeline.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    args = get_args()
    is_pr_validation, ignore_errors = convert_to_bool(args.isPrValidation, args.ignoreErrors)
    if os.path.exists(har_file_path):
        process_har_file(har_file_path)
        print_error_summary(is_pr_validation, ignore_errors)
    else:
        print(f"HAR file not found: {har_file_path}")