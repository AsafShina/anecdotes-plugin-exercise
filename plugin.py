from abc import abstractmethod


class Plugin:

    def __init__(self, username, password):
        self.username = username
        self.password = password

    @abstractmethod
    def connectivity_test(self):
        raise NotImplementedError()

    @abstractmethod
    def collect_user_details(self):
        raise NotImplementedError()

    @abstractmethod
    def collect(self):
        raise NotImplementedError()

    def run(self):
        if self.connectivity_test():
            self.collect()