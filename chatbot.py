import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI
from composio import Composio


class GitHubRepoCreator:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY")
        self.GITHUB_AUTH_CONFIG_ID = os.getenv("COMPOSIO_GITHUB_AUTH_CONFIG_ID")
        self.USER_ID = os.getenv("COMPOSIO_USER_ID")

        if not all([self.OPENAI_API_KEY, self.COMPOSIO_API_KEY,
                    self.GITHUB_AUTH_CONFIG_ID, self.USER_ID]):
            raise SystemExit(
                "Missing env vars. Ensure OPENAI_API_KEY, COMPOSIO_API_KEY, "
                "COMPOSIO_GITHUB_AUTH_CONFIG_ID, and COMPOSIO_USER_ID are set."
            )

        self.client = OpenAI(api_key=self.OPENAI_API_KEY)
        self.composio = Composio(api_key=self.COMPOSIO_API_KEY)
        self.TOOL_SLUG = "GITHUB_CREATE_A_REPOSITORY_FOR_THE_AUTHENTICATED_USER"
        self.is_github_authenticated = False

    # ---------------------------
    # Helpers to clean responses
    # ---------------------------
    def handle_connection_response(self, response):
        for item in response.items:
            if item.status == "ACTIVE":
                account_id = item.id
                print(f"✅ GitHub Connected | Account ID: {account_id}")
                return account_id
        print("⚠️ No active GitHub account found.")
        return None

    def handle_repo_creation(self, response):
        if response.get("successful") and response.get("data"):
            repo_url = response["data"].get("html_url")
            print(f"✅ Repository created: {repo_url}")
            return repo_url
        else:
            print("❌ Failed to create repository")
            return None

    # ---------------------------
    # GitHub Authentication
    # ---------------------------
    def authenticate_github(self, timeout: int = 300):
        print("🔑 Starting GitHub OAuth (if not already connected)...")

        try:
            connected_accounts = self.composio.connected_accounts.list()
            if connected_accounts and connected_accounts.items:
                self.handle_connection_response(connected_accounts)
                self.is_github_authenticated = True
                return connected_accounts

            connection_request = self.composio.connected_accounts.initiate(
                user_id=self.USER_ID,
                auth_config_id=self.GITHUB_AUTH_CONFIG_ID,
                config={"auth_scheme": "OAUTH2"},
            )

            print("🌐 Visit this URL to authenticate GitHub:")
            print(connection_request.redirect_url)
            print("⏳ Waiting for authentication to complete in browser...")

            connected_account = connection_request.wait_for_connection(timeout=timeout)
            self.handle_connection_response(connected_account)
            self.is_github_authenticated = True
            return connected_account

        except Exception as e:
            print(f"⚠️ Authentication warning: {e}")
            print("If you already connected previously, you can continue. "
                  "Otherwise, re-run after completing OAuth.")
            return None

    # ---------------------------
    # Parsing helpers
    # ---------------------------
    def parse_with_openai(self, text: str) -> dict:
        system = (
            "You are a strict parser. Given a user's instruction to create a GitHub repository, "
            "return JSON only with keys: name (string|null), private (true/false|null), "
            "description (string|null), auto_init (true/false|null). "
            "If a field is not specified, return null. No explanation."
        )
        user = f"Instruction: {text}"

        resp = self.client.chat.completions.create(
            model="gpt-4o-mini",
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

    def fallback_parse(self, text: str) -> dict:
        name, private, desc, auto_init = None, None, None, None

        m = re.search(r'(?:called|named)\s*["\']([^"\']+)["\']', text, re.I) \
            or re.search(r'(?:repo|repository)\s+["\']([^"\']+)["\']', text, re.I) \
            or re.search(r'(?:create|make)\s+(?:a\s+)?(?:repo|repository)\s+(?:called|named)?\s*([A-Za-z0-9_\-\.]+)', text, re.I)
        if m:
            name = m.group(1)

        if re.search(r'\b(private|privately|make it private)\b', text, re.I):
            private = True
        elif re.search(r'\b(public|publicly|make it public)\b', text, re.I):
            private = False

        mdesc = re.search(r'description\s*[:\-]\s*(?:"([^"]+)"|\'([^\']+)\'|(.+))', text, re.I)
        if mdesc:
            desc = next((g for g in mdesc.groups() if g), None)
            if desc:
                desc = desc.strip()

        if re.search(r'\b(init|initialize|with readme|auto[- ]?init|initialize with a readme)\b', text, re.I):
            auto_init = True

        return {"name": name, "private": private, "description": desc, "auto_init": auto_init}

    # ---------------------------
    # Repo Creation
    # ---------------------------
    def create_repository(self, args: dict):
        try:
            response = self.composio.tools.execute(
                self.TOOL_SLUG,
                user_id=self.USER_ID,
                arguments=args
            )
            self.handle_repo_creation(response)
        except Exception as e:
            print("❌ Repository creation failed. Error:")
            print(type(e).__name__, e)

    # ---------------------------
    # Main loop
    # ---------------------------
    def run(self):
        print("\n🤖 GitHub Repo Creator (type 'exit' to quit)")

        while True:
            if not self.is_github_authenticated:
                self.authenticate_github()
                if not self.is_github_authenticated:
                    print("⚠️ GitHub authentication is required to create repositories.")
                    break

            user_text = input("You: ").strip()
            if user_text.lower() in ("exit", "quit"):
                print("Bye 👋")
                break

            try:
                parsed = self.parse_with_openai(user_text)
            except Exception as e:
                print("⚠️ OpenAI parsing failed, using fallback:", e)
                parsed = self.fallback_parse(user_text)

            repo_name = parsed.get("name")
            if not repo_name:
                print("❌ Could not determine repository name. Try: create a repo called \"my-repo\"")
                continue

            args = {"name": repo_name}
            if parsed.get("private") is not None:
                args["private"] = bool(parsed["private"])
            if parsed.get("description"):
                args["description"] = parsed["description"]
            if parsed.get("auto_init") is not None:
                args["auto_init"] = bool(parsed["auto_init"])

            print("🚀 Creating repo with:", args)
            self.create_repository(args)


if __name__ == "__main__":
    app = GitHubRepoCreator()
    app.run()
