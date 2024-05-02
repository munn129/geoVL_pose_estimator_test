import matplotlib.pyplot as plt

class ErrorPlot:
    def __init__(self, topological_error: list) -> None:
        self.x = []
        self.y = []

        for i in topological_error:
            self.x.append(i.get_topological_latitude_list())
            self.y.append(i.get_topological_longitude_list())

    def plot(self):
        plt.scatter(self.x, self.y)
        plt.title('topological error')
        plt.xlabel('latitude')
        plt.ylabel('longitude')
        
        plt.show()