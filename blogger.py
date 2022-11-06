import os
import pickle
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/blogger']

load_dotenv()
BLOG_ID = os.environ['BLOG_ID']


def auth():
    # we check if the file to store the credentials exists
    if not os.path.exists('credentials.dat'):
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json', SCOPES)
        credentials = flow.run_local_server()
        with open('credentials.dat', 'wb') as credentials_dat:
            pickle.dump(credentials, credentials_dat)
    else:
        with open('credentials.dat', 'rb') as credentials_dat:
            credentials = pickle.load(credentials_dat)
    if credentials.expired:
        credentials.refresh(Request())
    blogger_service = build('blogger', 'v3', credentials=credentials)
    return blogger_service


def create_paste(title, content, labels):
    # https://developers.google.com/blogger/docs/3.0/reference/posts/insert
    posts = auth().posts()
    post_body = {
        "title": title,
        "content": content,
        "labels": labels,
    }
    post = posts.insert(blogId=BLOG_ID, body=post_body,
                        isDraft=False).execute()
    return post['id'], post['url']


def update_paste(postId, title, content, labels):
    # https://developers.google.com/blogger/docs/3.0/reference/posts/update
    posts = auth().posts()
    post_body = {
        "title": title,
        "content": content,
        "labels": labels,
    }
    post = posts.update(blogId=BLOG_ID, postId=postId,
                        body=post_body).execute()
    return post["url"]


def delete_paste(postId):
    # https://developers.google.com/blogger/docs/3.0/reference/posts/delete
    posts = auth().posts()
    post = posts.delete(blogId=BLOG_ID, postId=postId).execute()
