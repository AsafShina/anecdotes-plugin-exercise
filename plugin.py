from abc import abstractmethod

class Plugin:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.token = None
        self.base_url = None

    @abstractmethod
    def connectivity_test(self):
        raise NotImplementedError()

    @abstractmethod
    def collect_user_details(self):
        raise NotImplementedError()

    @abstractmethod
    def collect_posts(self):
        raise NotImplementedError()

    @abstractmethod
    def collect_posts_with_comments(self):
        raise NotImplementedError()

    @abstractmethod
    def output(self, data):
        raise NotImplementedError()

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
