import requests
import json
import os
from requests.auth import HTTPBasicAuth

# Replace these with your Reddit app credentials
CLIENT_ID = 'csCl_EagxlHvPnzn_cpWsA'
CLIENT_SECRET = 'jB5BYcW04pizUCz-U69xhMEnnYXG3Q'
USER_AGENT = 'py:myapp:v1.0 (by u/mohamed805)'

# Reddit OAuth2 URL
AUTH_URL = 'https://www.reddit.com/api/v1/access_token'

# Step 1: Function to authenticate with Reddit and get an access token
def get_access_token():
    auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    data = {'grant_type': 'password', 'username': 'mohamed805', 'password': ''}
    headers = {'User-Agent': USER_AGENT}
    
    response = requests.post(AUTH_URL, auth=auth, data=data, headers=headers)
    if response.status_code == 200:
        token_info = response.json()
        return token_info['access_token']
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return None

# Fetch a list of subreddits
# def get_list_of_subreddits(access_token, limit=100):
#     url = "https://oauth.reddit.com/subreddits/popular"
#     headers = {
#         'Authorization': f'bearer {access_token}',
#         'User-Agent': USER_AGENT
#     }
#     params = {'limit': limit}
#     response = requests.get(url, headers=headers, params=params)
    
#     if response.status_code == 200:
#         data = response.json().get('data', {}).get('children', [])
#         subreddits = [subreddit['data']['display_name'] for subreddit in data]
#         return subreddits
#     else:
#         print(f"Error fetching subreddits: {response.status_code}")
#         return []
    


def get_list_of_subreddits(access_token, limit=100):
    subreddits_list = []
    topics = ["politics", 'technology', 'computers', 'gaming', 'game', 'games', 'pcgaming', 'science', 'space', 'astronomy', 'sports', 'football', 'basketball', 'soccer']
    for topic in topics:
        url = f"https://oauth.reddit.com/subreddits/search.json?q={topic}"
        headers = {
            'Authorization': f'bearer {access_token}',
            'User-Agent': USER_AGENT
        }
        params = {'limit': limit}
        
        # Make the request to Reddit API
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json().get('data', {}).get('children', [])
            subreddits = [subreddit['data']['display_name'] for subreddit in data]
            subreddits_list.extend(subreddits)
        else:
            print(f"Error fetching subreddits for topic {topic}: {response.status_code}")
    
    # Return a combined list of subreddits
    return subreddits_list

# Function to check if the token is still valid
def is_token_valid(access_token):
    url = "https://oauth.reddit.com/api/v1/me"
    headers = {
        'Authorization': f'bearer {access_token}',
        'User-Agent': USER_AGENT
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return True
    elif response.status_code == 401:
        print("Token expired or invalid.")
        return False
    else:
        print(f"Error checking token validity: {response.status_code}")
        return False
        
# Fetch posts from a subreddit or user with pagination
def fetch_paginated_posts(url, limit, access_token):
    headers = {
        'Authorization': f'bearer {access_token}',
        'User-Agent': USER_AGENT
    }
    all_posts = []
    after = None

    while len(all_posts) < limit:
        params = {'limit': 100, 'after': after}
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.json())
            break

        data = response.json()
        posts = data.get('data', {}).get('children', [])
        all_posts.extend(posts)

        # Check if there are more pages
        after = data.get('data', {}).get('after')
        if not after:
            break

        print(f"Fetched {len(all_posts)} posts so far...")

    # Filter only text posts and required fields
    filtered_posts = [
        {
            'subreddit': post['data'].get('subreddit', ''),
            'title': post['data'].get('title', ''),
            'content': post['data'].get('selftext', ''),
            'author': post['data'].get('author', ''),
            'id': post['data'].get('id', ''),
            'created_utc': post['data'].get('created_utc', 0)
        }
        for post in all_posts
    ]

    return filtered_posts

# Fetch subreddit posts
def get_subreddit_posts(subreddit, limit, access_token):
    url = f'https://oauth.reddit.com/r/{subreddit}/new'
    return fetch_paginated_posts(url, limit, access_token)

# Fetch comments for a specific post
def fetch_comments(post_id, access_token):
    url = f"https://oauth.reddit.com/comments/{post_id}"
    headers = {
        'Authorization': f'bearer {access_token}',
        'User-Agent': USER_AGENT
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        comments = response.json()[1].get('data', {}).get('children', [])
        filtered_comments = [
            {
                'author': comment['data'].get('author', ''),
                'content': comment['data'].get('body', ''),
                'created_utc': comment['data'].get('created_utc', 0)
            }
            for comment in comments if comment['kind'] == 't1'  # Only include actual comments (not metadata)
        ]
        return filtered_comments
    else:
        print(f"Failed to fetch comments for post {post_id}: {response.status_code}")
        return []

# Fetch comments for posts in subreddits
def fetch_comments_for_subreddits(subreddits, post_limit, access_token):
    for subreddit in subreddits:
        filename = f'{subreddit}_filtered_comments.json'
        print(f"Fetching posts for subreddit: {subreddit}")
        if os.path.exists(filename):
                print(f"File {filename} already exists. Skipping subreddit: {subreddit}")
                continue
        posts = get_subreddit_posts(subreddit, post_limit, access_token)
        all_comments = []
        
        for post in posts:
            post_id = post.get('id')
            if not post_id:
                continue
            print(f"Fetching comments for post ID: {post_id}")
            comments = fetch_comments(post_id, access_token)
            all_comments.extend(comments)
            filename = f'{subreddit}_filtered_comments.json'
            save_data_to_json(all_comments, filename)
        
        # Save comments to a file named after the subreddit
        filename = f'{subreddit}_filtered_comments.json'
        save_data_to_json(all_comments, filename)
        print(f"Saved {len(all_comments)} comments for subreddit '{subreddit}'.")

# Save data to a JSON file
def save_data_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# Main function
def main():
    access_token = get_access_token()
    if not access_token:
        print("Failed to authenticate with Reddit.")
        return

    print("Enter the type of data you want to scrape:")
    choice = input("1. Posts from multiple subreddits\n2. Posts from multiple users\n3. Comments from subreddit posts\nChoose 1, 2, or 3: ")

    if choice == '1':
        # Fetch a list of popular subreddits
        limit_subreddits = int(input("How many subreddits to fetch? (default 10): ") or 10)
        limit_posts = int(input("How many posts per subreddit? (default 100): ") or 100)
        subreddits = get_list_of_subreddits(access_token, limit=limit_subreddits)

        print(f"Fetching posts from {len(subreddits)} subreddits...")
        for subreddit in subreddits:
            filename = f'{subreddit}_posts.json'
            if os.path.exists(filename):
                print(f"File {filename} already exists. Skipping subreddit: {subreddit}")
                continue
            print(f"Fetching posts from subreddit: {subreddit}")
            posts = get_subreddit_posts(subreddit, limit_posts, access_token)
            save_data_to_json(posts, filename)
            print(f"Saved {len(posts)} posts for subreddit '{subreddit}'.")

    elif choice == '2':
        # Manually specify a list of users
        users = input("Enter usernames separated by commas: ").split(",")
        limit_posts = int(input("How many posts per user? (default 100): ") or 100)

        print(f"Fetching posts from {len(users)} users...")
        for user in users:
            user = user.strip()
            filename = f'{user}_posts.json'
            if os.path.exists(filename):
                print(f"File {filename} already exists. Skipping user: {user}")
                continue
            print(f"Fetching posts from user: {user}")
            posts = fetch_paginated_posts(f'https://oauth.reddit.com/user/{user}/submitted', limit_posts, access_token)
            save_data_to_json(posts, filename)
            print(f"Saved {len(posts)} posts for user '{user}'.")

    elif choice == '3':
        # Fetch comments for posts in multiple subreddits
        limit_subreddits = int(input("How many subreddits to fetch? (default 10): ") or 10)
        limit_posts = int(input("How many posts per subreddit? (default 10): ") or 10)
        subreddits = get_list_of_subreddits(access_token, limit=limit_subreddits)

        print(f"Fetching comments from {len(subreddits)} subreddits...")
        fetch_comments_for_subreddits(subreddits, limit_posts, access_token)

    else:
        print("Invalid choice, please run the script again.")

if __name__ == "__main__":
    main()
