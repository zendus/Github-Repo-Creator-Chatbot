#!/usr/bin/env python3
import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI
from composio import Composio

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY")
GITHUB_AUTH_CONFIG_ID = os.getenv("COMPOSIO_GITHUB_AUTH_CONFIG_ID")
USER_ID = os.getenv("COMPOSIO_USER_ID")

# Tool slug used by composio to create a GitHub repository
TOOL_SLUG = "GITHUB_CREATE_A_REPOSITORY_FOR_THE_AUTHENTICATED_USER"

if not (OPENAI_API_KEY and COMPOSIO_API_KEY and GITHUB_AUTH_CONFIG_ID and USER_ID):
    raise SystemExit(
        "Missing env vars. Make sure OPENAI_API_KEY, COMPOSIO_API_KEY, COMPOSIO_GITHUB_AUTH_CONFIG_ID and COMPOSIO_USER_ID are set."
    )

client = OpenAI(api_key=OPENAI_API_KEY)
composio = Composio(api_key=COMPOSIO_API_KEY)

# Authenticate GitHub (first time)
print("Starting GitHub OAuth (if not already connected)...")
connection_request = composio.connected_accounts.initiate(
    user_id=USER_ID,
    auth_config_id=GITHUB_AUTH_CONFIG_ID,
    config={"auth_scheme": "OAUTH2"},
)
print("Visit this URL to authenticate GitHub:")
print(connection_request.redirect_url)
print("Waiting for you to complete authentication in the browser...")

# wait_for_connection may return immediately if already connected
try:
    connected_account = connection_request.wait_for_connection(timeout=300)
    print("Connected account:", getattr(connected_account, "id", repr(connected_account)))
except Exception as e:
    print("Warning: waiting for connection raised:", e)
    print("If you already connected previously, you can continue. Otherwise re-run after completing OAuth.")


# Helper: ask OpenAI to extract parameters
def parse_with_openai(text: str) -> dict:
    system = (
        "You are a strict parser. Given a user's instruction to create a GitHub repository, "
        "return JSON only with keys: name (string|null), private (true/false|null), "
        "description (string|null), auto_init (true/false|null). "
        "If a field is not specified, return null. No explanation."
    )
    user = f"Instruction: {text}"

    resp = client.chat.completions.create(
        model="gpt-4o-mini",  # use gpt-4o if available
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0,
        max_tokens=200,
    )

    content = resp.choices[0].message.content.strip()
    m = re.search(r"\{.*\}", content, re.S)
    if not m:
        raise ValueError("OpenAI did not return JSON")
    return json.loads(m.group(0))


# Fallback simple parser
def fallback_parse(text: str) -> dict:
    # name: look for quotes or keywords
    name = None
    m = re.search(r'(?:called|named)\s*["\']([^"\']+)["\']', text, re.I)
    if not m:
        m = re.search(r'(?:repo|repository)\s+["\']([^"\']+)["\']', text, re.I)
    if not m:
        m = re.search(r'(?:create|make)\s+(?:a\s+)?(?:repo|repository)\s+(?:called|named)?\s*([A-Za-z0-9_\-\.]+)', text, re.I)
    if m:
        name = m.group(1)

    private = None
    if re.search(r'\b(private|privately|make it private)\b', text, re.I):
        private = True
    elif re.search(r'\b(public|publicly|make it public)\b', text, re.I):
        private = False

    desc = None
    mdesc = re.search(r'description\s*[:\-]\s*(?:"([^"]+)"|\'([^\']+)\'|(.+))', text, re.I)
    if mdesc:
        desc = next((g for g in mdesc.groups() if g), None)
        if desc:
            desc = desc.strip()

    auto_init = None
    if re.search(r'\b(init|initialize|with readme|auto[- ]?init|initialize with a readme)\b', text, re.I):
        auto_init = True

    return {"name": name or None, "private": private, "description": desc or None, "auto_init": auto_init}


# Main loop
print("\n🤖 GitHub Repo Creator (type 'exit' to quit)")
while True:
    user_text = input("You: ").strip()
    if user_text.lower() in ("exit", "quit"):
        print("Bye 👋")
        break

    # Try OpenAI parser first, fallback to regex parser
    parsed = None
    try:
        parsed = parse_with_openai(user_text)
    except Exception as e:
        # safe fallback
        print("Warning: OpenAI parsing failed:", e)
        parsed = fallback_parse(user_text)

    # Validate name
    repo_name = parsed.get("name")
    if not repo_name:
        print("❌ Could not determine repository name. Try: create a repo called \"my-repo\"")
        continue

    # Build arguments for composio.tools.execute
    args = {"name": repo_name}
    if parsed.get("private") is not None:
        args["private"] = bool(parsed["private"])
    if parsed.get("description"):
        args["description"] = parsed["description"]
    if parsed.get("auto_init") is not None:
        args["auto_init"] = bool(parsed["auto_init"])

    print("Creating repo with:", args)

    try:
        result = composio.tools.execute(TOOL_SLUG, user_id=USER_ID, arguments=args)
        print("✅ Created repository (response):")
        print(result)
    except Exception as e:
        print("❌ Repository creation failed. Error:")
        print(type(e).__name__, e)
