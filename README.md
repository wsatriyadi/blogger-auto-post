# Blogger Auto Post

A Python utility for automatically posting content to Blogspot blogs using the Blogger API v3. This tool allows you to batch upload blog posts from a CSV file, making it easy to schedule and publish multiple posts at once.

## Features

- Authenticate with the Blogger API using OAuth2
- Read blog post content from CSV files
- Batch post multiple entries to your Blogspot blog
- Support for post labels/tags
- Option to save posts as drafts or publish immediately
- Customizable column mapping for CSV files

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/blogger-auto-post.git
   cd blogger-auto-post
   ```

2. Create and activate a virtual environment (recommended):
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

### Google API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Blogger API for your project
4. Create OAuth 2.0 credentials (Desktop application type)
5. Download the credentials JSON file

### Environment Variables

Create a `.env` file in the project root with the following variables:

```
BLOGGER_CREDENTIALS_FILE=/path/to/your/credentials.json
BLOGGER_TOKEN_FILE=/path/to/save/token.pickle
BLOGGER_BLOG_ID=your-blog-id
```

To find your blog ID:
1. Go to your Blogspot dashboard
2. The blog ID is in the URL when you're editing your blog: `https://www.blogger.com/blog/posts/YOUR_BLOG_ID`

## Usage

### Basic Usage

```
python main.py your_posts.csv
```

### Command Line Arguments

```
python main.py your_posts.csv --title-column "post_title" --content-column "post_content" --labels-column "tags" --draft
```

- `csv_file`: Path to the CSV file containing blog post content (required)
- `--title-column`: Column name for post titles (default: "title")
- `--content-column`: Column name for post content (default: "content")
- `--labels-column`: Column name for post labels/tags (default: "labels")
- `--draft`: Save posts as drafts instead of publishing immediately

### CSV File Format

Your CSV file should contain at minimum columns for the title and content of each post. Labels are optional.

Example CSV format:

```csv
title,content,labels
"My First Post","<p>This is the content of my first post.</p>","tag1,tag2"
"My Second Post","<p>This is the content of my second post.</p>","tag2,tag3"
```

Notes:
- The content column can contain HTML markup
- Labels should be comma-separated within the cell

## Authentication Flow

On first run, the application will:
1. Open a browser window asking you to log in to your Google account
2. Request permission to manage your Blogger blogs
3. Save the authentication token locally for future use

Subsequent runs will use the saved token without requiring re-authentication unless the token expires or is revoked.

## Troubleshooting

### Common Issues

- **"Credentials file not found"**: Ensure the path to your credentials file is correct in the .env file
- **"Not authenticated"**: Run the authenticate() method before attempting to create posts
- **"CSV must contain 'title' and 'content' columns"**: Check your CSV file format and column names
- **"Error creating post"**: Check your internet connection and API quotas

### Logging

The application uses Python's logging module to provide information about its operation. By default, logs are output to the console with INFO level.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.