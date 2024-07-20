from plugin import Plugin
import requests


class DummyApiPlugin(Plugin):
    def __init__(self, username, password):
        super().__init__(username, password)
        self.id = None
        self.base_url = "https://dummyjson.com"

    def connectivity_test(self):
        try:
            response = requests.post(f"{self.base_url}/auth/login",
                                     json={"username": self.username,
                                           "password": self.password})
            response.raise_for_status()
            self.token = response.json().get("token")
            self.id = response.json().get("id")
            print("Connection successful!")
            return True
        except requests.exceptions.HTTPError as err:
            print(f"Connection failed: {err}")
            return False

    def collect_user_details(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/users/{self.id}", headers=headers)
        response.raise_for_status()
        return response.json()

    def collect_posts(self, user_id=None):
        if user_id:
            response = requests.get(f"{self.base_url}/users/{user_id}/posts")
        else:
            response = requests.get(f"{self.base_url}/posts")
        response.raise_for_status()
        return response.json().get("posts", [])

    def collect_posts_with_comments(self, posts):
        posts_with_comments = []
        for post in posts:
            post_id = post["id"]
            response = requests.get(f"{self.base_url}/posts/{post_id}/comments")
            response.raise_for_status()
            post["comments"] = response.json()
            posts_with_comments.append(post)
        return posts_with_comments

    def output(self, data):
        if data:
            print("User Details:", data["user_details"])
            print("Posts:", data["posts"])
            print("Number of Posts:", len(data["posts"]))
            print("Posts with Comments:", data["posts_with_comments"])
            print("Number of Posts with Comments:", len(data["posts_with_comments"]))

    def all_users_with_posts(self):
        response = requests.get(f"{self.base_url}/users")
        response.raise_for_status()
        users = response.json().get("users", [])

        eligible_users = []
        for user in users:
            user_id = user["id"]
            if user_id != self.id:
                eligible_users.append(user_id)
        return eligible_users

    def collect(self):
        try:
            user_details = self.collect_user_details()
            posts = self.collect_posts()
            posts_with_comments = self.collect_posts_with_comments(posts)

            if len(posts) < 60:
                users_with_posts = self.all_users_with_posts()
                users_posts = []
                users_posts_with_comments = []

                while len(posts) < 60 and users_with_posts:
                    for user_id in users_with_posts:
                        if len(posts) >= 60:
                            break
                        new_posts = self.collect_posts(user_id)
                        posts.extend(new_posts)
                        new_posts_with_comments = self.collect_posts_with_comments(new_posts)
                        posts_with_comments.extend(new_posts_with_comments)

                    # Ensure we don't run indefinitely
                    users_with_posts = [user_id for user_id in users_with_posts if len(posts) < 60]

                # Trim lists to ensure exactly 60 items
                posts = posts[:60]
                posts_with_comments = [post for post in posts_with_comments if post in posts]

            return {
                "user_details": user_details,
                "posts": posts,
                "posts_with_comments": posts_with_comments
            }
        except Exception as err:
            print(f"Data collection failed: {err}")
            return None