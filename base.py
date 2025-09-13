from composio import Composio 
import os 
from dotenv import load_dotenv 

load_dotenv() 

api_key = os.getenv("COMPOSIO_API_KEY") 

# Initialize Composio client with your API key 
composio = Composio(api_key=api_key) 

# Authenticate GitHub via OAuth2
github_auth_config_id = os.getenv("COMPOSIO_GITHUB_AUTH_CONFIG_ID") 
user_id = os.getenv("COMPOSIO_USER_ID")
connection_request = composio.connected_accounts.initiate( user_id=user_id, auth_config_id=github_auth_config_id, config={"auth_scheme": "OAUTH2"} ) 
print(f"Visit this URL to authenticate GitHub: {connection_request.redirect_url}") 

connected_account = connection_request.wait_for_connection(timeout=120) 
print(f"Connected account: {connected_account.id}") 

tool_slug = "GITHUB_CREATE_A_REPOSITORY_FOR_THE_AUTHENTICATED_USER" 

arguments = { "name": "test-repo", # Required: repository name 
             "private": True,
            } 

result = composio.tools.execute( tool_slug, user_id=user_id, arguments=arguments ) 
print("Repository creation result:", result)