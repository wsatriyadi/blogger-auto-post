"""Blogger API v3 Library for auto-posting content to Blogspot.

This module provides a class to interact with the Blogger API v3 for automatically
posting content from CSV files to a Blogspot blog.
"""

import os
import csv
import pandas as pd
from typing import Dict, List, Optional, Any, Union
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
import pickle
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BloggerAPI:
    """A class to interact with the Blogger API v3.
    
    This class provides methods to authenticate with the Blogger API,
    read content from CSV files, and post that content to a Blogspot blog.
    """
    
    # The scope required for Blogger API
    SCOPES = ['https://www.googleapis.com/auth/blogger']
    
    def __init__(self, credentials_file: str = None, token_file: str = None, 
                 blog_id: str = None):
        """Initialize the BloggerAPI class.
        
        Args:
            credentials_file: Path to the client secrets JSON file.
            token_file: Path to save/load the user's access and refresh tokens.
            blog_id: The ID of the blog to post to.
        """
        self.credentials_file = credentials_file or os.getenv('BLOGGER_CREDENTIALS_FILE')
        self.token_file = token_file or os.getenv('BLOGGER_TOKEN_FILE')
        self.blog_id = blog_id or os.getenv('BLOGGER_BLOG_ID')
        self.service = None
        
        if not self.credentials_file or not self.blog_id:
            logger.error("Missing required configuration. Please set BLOGGER_CREDENTIALS_FILE and BLOGGER_BLOG_ID")
            raise ValueError("Missing required configuration")
    
    def authenticate(self) -> None:
        """Authenticate with the Blogger API.
        
        This method handles the OAuth2 authentication flow, including:
        - Loading saved credentials if available
        - Refreshing expired credentials
        - Starting a new authentication flow if needed
        
        Raises:
            FileNotFoundError: If the credentials file doesn't exist.
            Exception: For other authentication errors.
        """
        creds = None
        
        # Load token from file if it exists
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                try:
                    creds = pickle.load(token)
                except Exception as e:
                    logger.warning(f"Error loading credentials: {e}")
        
        # If no valid credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except RefreshError as e:
                    logger.warning(f"Failed to refresh token: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(f"Credentials file not found: {self.credentials_file}")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        # Build the service
        try:
            self.service = build('blogger', 'v3', credentials=creds)
            logger.info("Successfully authenticated with Blogger API")
        except Exception as e:
            logger.error(f"Failed to build Blogger service: {e}")
            raise
    
    def read_csv(self, csv_file: str) -> List[Dict[str, str]]:
        """Read blog post content from a CSV file.
        
        Args:
            csv_file: Path to the CSV file containing blog post content.
            
        Returns:
            A list of dictionaries, each representing a blog post.
            
        Raises:
            FileNotFoundError: If the CSV file doesn't exist.
            Exception: For other CSV reading errors.
        """
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"CSV file not found: {csv_file}")
        
        try:
            # Using pandas for more robust CSV handling
            df = pd.read_csv(csv_file)
            posts = df.to_dict('records')
            logger.info(f"Successfully read {len(posts)} posts from {csv_file}")
            return posts
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            raise
    
    def create_post(self, title: str, content: str, labels: Optional[List[str]] = None, 
                    is_draft: bool = False) -> Dict[str, Any]:
        """Create a new blog post.
        
        Args:
            title: The title of the blog post.
            content: The HTML content of the blog post.
            labels: Optional list of labels/tags for the post.
            is_draft: Whether to save as draft (True) or publish immediately (False).
            
        Returns:
            The response from the Blogger API containing the post details.
            
        Raises:
            ValueError: If the service is not authenticated.
            Exception: For API errors.
        """
        if not self.service:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        if not title or not content:
            raise ValueError("Title and content are required")
        
        post_body = {
            'kind': 'blogger#post',
            'title': title,
            'content': content,
        }
        
        if labels:
            post_body['labels'] = labels
        
        try:
            request = self.service.posts().insert(
                blogId=self.blog_id,
                body=post_body,
                isDraft=is_draft
            )
            response = request.execute()
            logger.info(f"Successfully created post: {title}")
            return response
        except Exception as e:
            logger.error(f"Error creating post: {e}")
            raise
    
    def batch_post_from_csv(self, csv_file: str, title_column: str = 'title', 
                           content_column: str = 'content', labels_column: Optional[str] = 'labels', 
                           is_draft: bool = False) -> List[Dict[str, Any]]:
        """Read posts from a CSV file and publish them to the blog.
        
        Args:
            csv_file: Path to the CSV file containing blog post content.
            title_column: The name of the column containing post titles.
            content_column: The name of the column containing post content.
            labels_column: Optional name of the column containing comma-separated labels.
            is_draft: Whether to save as drafts (True) or publish immediately (False).
            
        Returns:
            A list of responses from the Blogger API for each post.
            
        Raises:
            ValueError: If required columns are missing.
            Exception: For other errors.
        """
        posts = self.read_csv(csv_file)
        responses = []
        
        # Validate required columns
        if not posts or title_column not in posts[0] or content_column not in posts[0]:
            raise ValueError(f"CSV must contain '{title_column}' and '{content_column}' columns")
        
        for post in posts:
            title = post[title_column]
            content = post[content_column]
            
            # Process labels if available
            labels = None
            if labels_column and labels_column in post and post[labels_column]:
                if isinstance(post[labels_column], str):
                    labels = [label.strip() for label in post[labels_column].split(',')]
            
            try:
                response = self.create_post(title, content, labels, is_draft)
                responses.append(response)
            except Exception as e:
                logger.error(f"Failed to post '{title}': {e}")
                # Continue with next post even if one fails
                continue
        
        logger.info(f"Completed batch posting. Successfully posted {len(responses)} out of {len(posts)} posts")
        return responses