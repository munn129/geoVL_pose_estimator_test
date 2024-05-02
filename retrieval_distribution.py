# evaluation of retrieval result
# image retrieval 결과가 어떠한 경향을 띄는지 보기 위함

from retrieved_image import RetrievedImage

class RetrievalDistribution:
    def __init__(self, retrieved_instance: RetrievedImage) -> None:
        self.query = retrieved_instance.get_query()
        self.retrieved_list = retrieved_instance.get_retrieved_image_list()
        self.query_gps = self.query.get_latitude(), self.query.get_longitude()
        self.retrieved_gps_list = []
        for retrieved in self.retrieved_list:
            self.retrieved_gps_list.append(retrieved.get_latitude(), retrieved.get_longitude())

    def topological_gps_error(self):
        pass

def main():
    pass

if __name__ == '__main__': main()