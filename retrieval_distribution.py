# evaluation of retrieval result
# image retrieval 결과가 어떠한 경향을 띄는지 보기 위함

from retrieved_image import RetrievedImage

class RetrievalDistribution:
    def __init__(self, retrieved_instance: RetrievedImage, use_num = 1) -> None:
        self.query = retrieved_instance.get_query()
        self.retrieved_list = retrieved_instance.get_retrieved_image_list()
        self.query_gps = self.query.get_latitude(), self.query.get_longitude()
        self.retrieved_gps_list = []
        for retrieved in self.retrieved_list:
            self.retrieved_gps_list.append(retrieved.get_latitude(), retrieved.get_longitude())

        self.topological_error_list = []
        self.topological_latitude_error_list = []
        self.topological_longitude_error_list = []

        for i in range(use_num):
            latitude = self.query_gps[0] - self.retrieved_gps_list[i][0]
            longitude = self.query_gps[1] - self.retrieved_gps_list[i][1]
            self.topological_error_list.append((latitude, longitude))
            self.topological_latitude_error_list.append(latitude)
            self.topological_longitude_error_list.append(longitude)

    def get_topological_error_list(self):
        return self.topological_error_list
    
    def get_topological_latitude_list(self):
        return self.topological_latitude_error_list
    
    def get_topological_longitude_list(self):
        return self.topological_longitude_error_list

def main():
    pass

if __name__ == '__main__': main()