Publish the UAE Banking Apps Review Pulse dashboard update. Do exactly this and nothing else:
1. Run the Artifact tool with action "publish", url https://claude.ai/artifact/TSWbsxwLrftdCKMk5TEYBj, file_path /Users/hemal/Documents/Github/ENBDXFeedback/web/index.html. If the publish is refused because the live version was not viewed, read the live version with action "read" on that url, then publish the same file again (the repo file is the source of truth; do not merge live content into it).
2. Send `files` as a map {"<published path>": "<absolute source path>"} built from /Users/hemal/Documents/Github/ENBDXFeedback/data/_publish_files.json (a JSON object already in exactly that shape). Include "app.html" -> /Users/hemal/Documents/Github/ENBDXFeedback/web/app.html.
3. Do not pass capabilities (the stored declaration carries forward). Use label "Daily refresh".
4. Reply with the version id only.
