from plugin import Plugin
import requests


class DummyApiPlugin(Plugin):
    def __init__(self, username, password):
        super().__init__(username, password)
        self.base_url = "https://dummyjson.com"
        self.id = None
        self.user_details = None
        self.token = None
        self.posts = None
        self.posts_with_comments = None

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
        self.user_details = response.json()
        return self.user_details

    def collect_user_posts(self, user_id=None):
        if user_id:
            response = requests.get(f"{self.base_url}/users/{user_id}/posts")
        else:
            response = requests.get(f"{self.base_url}/posts")
        response.raise_for_status()
        return response.json().get("posts", [])

    def collect_user_posts_with_comments(self):
        posts = self.collect_user_posts(self.id)
        posts_with_comments = []
        for post in posts:
            post_id = post["id"]
            response = requests.get(f"{self.base_url}/posts/{post_id}/comments")
            response.raise_for_status()
            post["comments"] = response.json()
            posts_with_comments.append(post)
        return posts_with_comments

    def get_user_tags(self):
        user_posts = self.collect_user_posts()
        user_tags = set()
        for post in user_posts:
            tags = post.get("tags", [])
            user_tags.update(tags)
        return user_tags

    def collect_posts(self):
        user_tags = self.get_user_tags()  # Get tags from the user's posts
        total_posts = []
        matching_posts = []
        limit = 100
        skip = 0

        while len(total_posts) < 60:
            # fetch for a batch of size 'limit' from the data set and store it in the 'posts' list
            response = requests.get(f"{self.base_url}/posts?limit={limit}&skip={skip}")
            response.raise_for_status()
            posts = response.json().get("posts", [])

            # collect all posts that do not belong to the user,
            # but share similar 'tags' to the ones his posts
            for post in posts:
                if post['userId'] != self.id:  # Ensure the post does not belong to the user
                    post_tags = set(post.get("tags", []))
                    if post_tags & user_tags:  # Intersection to check for common tags
                        matching_posts.append(post)
                        if len(matching_posts) == 60:
                            break

            # add the post to a list contain all the posts that where fetch so far
            # Break if no more posts are returned, or enough matching posts are found
            total_posts.extend(posts)
            if not posts or len(matching_posts) == 60:
                break
            # increase the 'skip' to fetch for the next batch of size 'limit'
            skip += limit

        # If not enough matching posts, fill with random posts
        # that not belong to the user, and not in 'matching_posts' already (do not share 'tags')
        if len(matching_posts) < 60:
            extra_needed = 60 - len(matching_posts)
            non_matching_posts = [post for post in total_posts if
                                  post['userId'] != self.id and post not in matching_posts]
            matching_posts.extend(non_matching_posts[:extra_needed])

        # print(f"Collected {len(matching_posts)} posts with matching tags.")
        self.posts = matching_posts
        return self.posts

    def collect_posts_with_comments(self):
        posts = self.collect_posts()
        posts_with_comments = []
        for post in posts:
            post_id = post["id"]
            response = requests.get(f"{self.base_url}/posts/{post_id}/comments")
            response.raise_for_status()
            post["comments"] = response.json()
            posts_with_comments.append(post)
        self.posts_with_comments = posts_with_comments
        return self.posts_with_comments

    def collect(self):
        try:
            user_details = self.collect_user_details()
            posts = self.collect_posts()
            posts_with_comments = self.collect_posts_with_comments()
            return {
                "user_details": user_details,
                "posts": posts,
                "posts_with_comments": posts_with_comments
            }
        except Exception as err:
            print(f"Data collection failed: {err}")
            return None

    def run(self):
        if self.connectivity_test():
            collected_data = self.collect()
            if collected_data:
                self.output(collected_data)

    # for debuting purposes
    @staticmethod
    def output(data):
        if data:
            print("User Details:", data["user_details"])
            print("Posts:", data["posts"])
            print("Posts with Comments:", data["posts_with_comments"])
