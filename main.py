import os
import argparse
import logging
from dotenv import load_dotenv
from lib.blogger_api import BloggerAPI

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main function to run the Blogspot auto post script."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Post content to Blogspot from a CSV file')
    parser.add_argument('csv_file', help='Path to the CSV file containing blog post content')
    parser.add_argument('--title-column', default='title', help='Column name for post titles')
    parser.add_argument('--content-column', default='content', help='Column name for post content')
    parser.add_argument('--labels-column', default='labels', help='Column name for post labels/tags')
    parser.add_argument('--draft', action='store_true', help='Save posts as drafts instead of publishing')
    args = parser.parse_args()
    
    try:
        # Initialize the BloggerAPI with credentials from environment variables
        blogger = BloggerAPI()
        
        # Authenticate with the Blogger API
        blogger.authenticate()
        
        # Post content from the CSV file
        responses = blogger.batch_post_from_csv(
            csv_file=args.csv_file,
            title_column=args.title_column,
            content_column=args.content_column,
            labels_column=args.labels_column,
            is_draft=args.draft
        )
        
        # Print summary
        logger.info(f"Successfully posted {len(responses)} blog posts")
        for i, response in enumerate(responses, 1):
            logger.info(f"Post {i}: {response.get('title')} - {response.get('url')}")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())