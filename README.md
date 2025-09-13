# GitHub Repo Creator Chatbot 🤖

A conversational chatbot powered by OpenAI and Composio that streamlines GitHub repository creation through natural language interactions.

## ✨ Features

- **OAuth2 Authentication**: Secure GitHub integration via Composio
- **Conversational Interface**: Natural language repository creation requests
- **Repository Control**: Create both private and public repositories
- **Streamlined Workflow**: No manual GitHub navigation required

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Composio API key
- GitHub account

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/zendus/github-repo-creator-chatbot.git
cd github-repo-creator-chatbot
```

### 2. Set Up Virtual Environment

**macOS/Linux:**

```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

Create a `.env` file in the project root directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
COMPOSIO_API_KEY=your_composio_api_key_here
COMPOSIO_GITHUB_AUTH_CONFIG_ID=your_github_auth_config_id
COMPOSIO_USER_ID=your_unique_user_id
```

### Getting Your API Keys

- **OpenAI API Key**: Get yours at [platform.openai.com](https://platform.openai.com/api-keys)
- **Composio API Key**: Sign up at [composio.dev](https://composio.dev) to obtain your key
- **User ID**: Use a unique identifier like a UUID or your email address

## 🚀 Usage

1. **Start the application:**

   ```bash
   python chatbot.py
   ```

2. **Authenticate with GitHub** when prompted

3. **Chat naturally** with the bot to create repositories:
   - "Create a new public repo called 'my-awesome-project'"
   - "I need a private repository titled diary for my personal notes"

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 🔗 Links

- [Composio Documentation](https://docs.composio.dev)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Report Issues](https://github.com/zendus/github-repo-creator-chatbot/issues)

## ⭐ Support

If you found this project helpful, please give it a star on GitHub!
