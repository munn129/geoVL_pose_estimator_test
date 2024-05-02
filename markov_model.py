# 일단은... 과거 retrieved 결과를 받아야 함. 어능정도까지?
# 그냥 직전 스텝만 받아서, 마르코프 체인이라 하자

# 이게 이 클래스에서 직전 단계만 받아서 처리하면 좋겠지만,
# 필터링한 결과를 계속 업데이트하려면, 메인 파일에서 바꿔야할 것 같으니
# 일단... 여기서 전부 처리하는 걸로

from retrieved_image import RetrievedImage

class MarkovModel:
    def __init__(self, result_list: list) -> None:
        self.result.list = result_list[:]
        