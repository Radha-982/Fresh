
from oauth2client.service_account import ServiceAccountCredentials

def get_credentials(scopes: list)-> ServiceAccountCredentials:
    credentialss = ServiceAccountCredentials.from_json_keyfile_name('Keys.json', scopes)
    return credentialss