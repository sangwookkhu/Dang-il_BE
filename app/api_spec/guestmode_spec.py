class GuestmodeSpec:
    @staticmethod
    def guestmode_mainpage():
        spec = {
            "summary": "게스트모드 메인페이지 초기 로딩에 필요한 정보 응답",
            "description": 
                """
                    로그인 하지 않은 상태로 요청 시 메인페이지 초기 로딩에 필요한 정보 응답 <br><br> 
                    모르는 사람 17명(본인 제외) 응답 <br><br> 
                    공간 정보, 집중 시간 정보도 응답
                """,
            "operation_id": "guestmode_mainpage",
            "responses": {
                200: {
                    "description": "메시지, 각 유저의 사용자 정보, 공간 정보, 집중 시간 정보 포함된 응답, 없으면 false거나 없음",
                    "content": {
                            "application/json": {
                                "examples": {
                                    "예시": {
                                        "summary": "응답 예시",
                                        "value": {
                                        "message": "The response was successfully transmitted",
                                        "data": {
                                            "user_data": {
                                            "unknown_user_data": [
                                                {
                                                "_id": "112028052296384135975",
                                                "name": "조익준",
                                                "email": "choikjun9659@gmail.com",
                                                "tag": "10000",
                                                "accessibility": 'false'
                                                },
                                                {
                                                "_id": "18",
                                                "name": "18",
                                                "email": "test",
                                                "tag": "test",
                                                "accessibility": 'false'
                                                },
                                                {
                                                "_id": "34",
                                                "name": "34",
                                                "email": "test",
                                                "tag": "test",
                                                "accessibility": 'false'
                                                },
                                                {
                                                "_id": "13",
                                                "name": "13",
                                                "email": "test",
                                                "tag": "test",
                                                "accessibility": 'false'
                                                },
                                                {
                                                "_id": "26",
                                                "name": "26",
                                                "email": "test",
                                                "tag": "test",
                                                "accessibility": 'false'
                                                },
                                                {
                                                "_id": "10",
                                                "name": "10",
                                                "email": "test",
                                                "tag": "test",
                                                "accessibility": 'false'
                                                },
                                                {
                                                "_id": "7",
                                                "name": "7",
                                                "email": "test",
                                                "tag": "test",
                                                "accessibility": 'false'
                                                },
                                                {
                                                "_id": "3666956208",
                                                "name": "채지성",
                                                "email": "jschae02@kakao.com",
                                                "tag": "00000",
                                                "accessibility": 'false'
                                                },
                                                {
                                                "_id": "test2",
                                                "name": "‍test2",
                                                "email": "test2",
                                                "tag": "test2",
                                                "accessibility": 'false'
                                                },
                                                {
                                                "_id": "11",
                                                "name": "11",
                                                "email": "test",
                                                "tag": "test",
                                                "accessibility": 'false'
                                                },
                                                {
                                                "_id": "38",
                                                "name": "38",
                                                "email": "test",
                                                "tag": "test",
                                                "accessibility": 'false'
                                                },
                                                {
                                                "_id": "39",
                                                "name": "39",
                                                "email": "test",
                                                "tag": "test",
                                                "accessibility": 'false'
                                                },
                                                {
                                                "_id": "28",
                                                "name": "28",
                                                "email": "test",
                                                "tag": "test",
                                                "accessibility": 'false'
                                                },
                                                {
                                                "_id": "0",
                                                "name": "0",
                                                "email": "test",
                                                "tag": "test",
                                                "accessibility": 'false'
                                                },
                                                {
                                                "_id": "30",
                                                "name": "30",
                                                "email": "test",
                                                "tag": "test",
                                                "accessibility": 'false'
                                                },
                                                {
                                                "_id": "21",
                                                "name": "21",
                                                "email": "test",
                                                "tag": "test",
                                                "accessibility": 'false'
                                                },
                                                {
                                                "_id": "23",
                                                "name": "23",
                                                "email": "test",
                                                "tag": "test",
                                                "accessibility": 'false'
                                                }
                                            ]
                                            },
                                            "user_space_data": {
                                            "unknown_space_data": ['false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false']
                                            },
                                            "user_tasking_time_data": {
                                            "unknown_tasking_time_data": ['false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false']
                                            }
                                        },
                                    },
                                }
                            }
                        }
                    },
                }
            }
        }
        return spec