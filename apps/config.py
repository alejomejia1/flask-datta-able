# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os, random, string

class Config(object):
    
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    CLIENT_ID = os.getenv("CLIENT_ID") # Application (client) ID of app registration
    CLIENT_SECRET = os.getenv("CLIENT_SECRET") # Placeholder - for use ONLY during testing.

    AUTHORITY = os.getenv("AUTHORITY")
    REDIRECT_PATH = "/api/auth/callback"  # Used for forming an absolute URL to your redirect URI.
                                # The absolute URL must match the redirect URI you set
                                # in the app's registration in the Azure portal.
    
    # You can find more Microsoft Graph API endpoints from Graph Explorer
    # https://developer.microsoft.com/en-us/graph/graph-explorer
    # ENDPOINT = 'https://graph.microsoft.com/v1.0/users'  # This resource requires no admin consent
    ENDPOINT = 'https://graph.microsoft.com/beta/users'
    # https://graph.microsoft.com/beta/users?$select=userPrincipalName,onPremisesSamAccountName
    # You can find the proper permission names from this document
    # https://docs.microsoft.com/en-us/graph/permissions-reference
    SCOPE = ["User.ReadBasic.All"]

    SESSION_TYPE = "filesystem"  # Specifies the token cache should be stored in server-side session

    basedir = os.path.abspath(os.path.dirname(__file__))

    # Assets Management
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')  
    PDF_FOLDER = os.getenv('PDF_FOLDER', '/static/pdfs')
    # Set up the App SECRET_KEY
    SECRET_KEY  = os.getenv('SECRET_KEY', None)
    if not SECRET_KEY:
        SECRET_KEY = ''.join(random.choice( string.ascii_lowercase  ) for i in range( 32 ))

    # Social AUTH context
    SOCIAL_AUTH_GITHUB  = False

    GITHUB_ID      = os.getenv('GITHUB_ID'    , None)
    GITHUB_SECRET  = os.getenv('GITHUB_SECRET', None)

    # Enable/Disable Github Social Login    
    if GITHUB_ID and GITHUB_SECRET:
         SOCIAL_AUTH_GITHUB  = True        

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Get environment variables
    DBSERVER = os.getenv('DBSERVER')
    DBNAME = os.getenv('DBNAME')
    DBUSER = os.getenv('DBUSER')
    DBTYPE = os.getenv('DBTYPE')
    DBPORT = os.getenv('DBPORT')
    DBPASSWORD = os.getenv("DBPASSWORD")
    CONNECT_URL = os.getenv('CONNECT_URL')
   
    SQLALCHEMY_DATABASE_URI=CONNECT_URL
    SQLALCHEMY_TRACK_MODIFICATIONS=False
 
    # Calendar Settings
    WEEK_START_DAY_MONDAY = 0
    WEEK_START_DAY_SUNDAY = 6

    MIN_YEAR = 2022
    MAX_YEAR = 2200
    WEEK_STARTING_DAY = WEEK_START_DAY_MONDAY

    HIDE_PAST_TASKS = False
 
    DB_ENGINE   = os.getenv('DB_ENGINE'   , None)
    # DB_USERNAME = os.getenv('DB_USERNAME' , None)
    # DB_PASS     = os.getenv('DB_PASS'     , None)
    # DB_HOST     = os.getenv('DB_HOST'     , None)
    # DB_PORT     = os.getenv('DB_PORT'     , None)
    # DB_NAME     = os.getenv('DB_NAME'     , None)

    USE_SQLITE  = True 
    
    # Application (client) ID of app registration
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET") # Placeholder - for use ONLY during testing.
    # In a production app, we recommend you use a more secure method of storing your secret,
    # like Azure Key Vault. Or, use an environment variable as described in Flask's documentation:
    # https://flask.palletsprojects.com/en/1.1.x/config/#configuring-from-environment-variables
    # CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    # if not CLIENT_SECRET:
    #     raise ValueError("Need to define CLIENT_SECRET environment variable")

    # AUTHORITY = "https://login.microsoftonline.com/common"  # For multi-tenant app
    AUTHORITY = os.getenv("AUTHORITY")

    REDIRECT_PATH = "/getAToken"  # Used for forming an absolute URL to your redirect URI.
                                # The absolute URL must match the redirect URI you set
                                # in the app's registration in the Azure portal.

    # You can find more Microsoft Graph API endpoints from Graph Explorer
    # https://developer.microsoft.com/en-us/graph/graph-explorer
    ENDPOINT = 'https://graph.microsoft.com/v1.0/users'  # This resource requires no admin consent

    # You can find the proper permission names from this document
    # https://docs.microsoft.com/en-us/graph/permissions-reference
    SCOPE = ["User.ReadBasic.All"]
    SESSION_TYPE = "filesystem"  # Specifies the token cache should be stored in server-side session
    
    CONSULTAR_LENEL = os.getenv("CONSULTAR_LENEL")

    
class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600


class DevelopmentConfig(Config):
	DEBUG = True
    
    
class DebugConfig(Config):
    DEBUG = True

# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug'     : DebugConfig
}
