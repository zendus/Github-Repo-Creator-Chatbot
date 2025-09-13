# Github-Repo-Creator-Chatbot 🤖

This project is a simple chatbot powered by OpenAI and Composio that allows you to create a new GitHub repository via conversation.

---

## 🚀 Features

- Authenticate with GitHub using **Composio** OAuth2.
- Chat with an LLM and request repository creation.
- Creates **private** or **public** repositories with ease.

---

## 🛠️ Installation

1. Clone this repository:

```bash
git clone https://github.com/zendus/github-repo-creator-chatbot.git
cd github-repo-creator-chatbot
```

2. Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate   # On Mac/Linux
venv\Scripts\activate      # On Windows

pip install -r requirements.txt
```

## Configuration

Create a .env file in the project root with the following variables:

```bash
OPENAI_API_KEY=your_openai_api_key_here
COMPOSIO_API_KEY=your_composio_api_key_here
COMPOSIO_GITHUB_AUTH_CONFIG_ID=your_github_auth_config_id
COMPOSIO_USER_ID=your_unique_user_id   # e.g., UUID or email
```
