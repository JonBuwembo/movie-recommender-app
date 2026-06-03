from abc import ABC, abstractmethod

# Contract class
# Every recommmender must implement this class
class Recommender(ABC):

    @abstractmethod
    def train(self):
        pass

    @abstractmethod
    def recommend(self, user_id, n=20):
        pass

    @abstractmethod
    def save(self, path):
        pass

    @abstractmethod
    def load(self, path):
        pass