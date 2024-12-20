class MainpageSpec:
    @staticmethod
    def mainpage():
        spec = {
            "summary": "메인페이지 초기 로딩에 필요한 정보 응답",
            "description": 
                """
                    로그인 한 상태로 요청 시 메인페이지 초기 로딩에 필요한 정보 응답 <br><br> 
                    본인+친구+모르는 사람 포함해서 18명 응답 <br><br> 
                    모르는 사람은 18-(본인+친구) 형태로 반환 <br><br> 
                    공간 정보, 집중 시간 정보도 응답<br> <br> 
                    쿠키에 session_id 필수
                """,
            "operation_id": "mainpage",
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
                                                    "my_data": {
                                                            "_id": "test1",
                                                            "name": "‍test1",
                                                            "email": "test1",
                                                            "tag": "test1",
                                                            "accessibility": 'false',
                                                            "friend_list": [
                                                                "0",
                                                                "1",
                                                                "2",
                                                                "3",
                                                                "4",
                                                                "5",
                                                                "6",
                                                                "7"
                                                            ]
                                                        },
                                                    "friend_data": ["친구들 정보"],
                                                    "unknown_user_data": ["모르는 유저들 정보"],
                                                },
                                                "user_space_data": {
                                                    "my_space_data": {
                                                        "_id": "test1",
                                                        "interior_data": [
                                                            {
                                                                "decor_id": "desk1",
                                                                "location": [
                                                                    1.0,
                                                                    2.0,
                                                                    3.0
                                                                ]
                                                            }
                                                        ]
                                                    },
                                                    "friend_space_data": ["친구 공간 정보"],
                                                    "unknown_space_data": ["모르는 유저 공간 정보"]
                                                },
                                                "user_tasking_time_data": {
                                                    "my_tasking_time_data": {
                                                        "_id": "test1",
                                                        "today_tasking_time": {
                                                            "total_time": 3600,
                                                            "task_specific_time": {
                                                                "math": 1900,
                                                                "coding": 1700
                                                            }
                                                        },
                                                        "previous_tasking_time": {
                                                            "day1": {
                                                                "total_time": 10800,
                                                                "task_specific_time": {
                                                                    "math": 5400,
                                                                    "coding": 5400
                                                                }
                                                            }
                                                        }
                                                    },
                                                    "friend_tasking_time":["친구 공간 정보"],
                                                    "unknown_tasking_time_data": ["모르는 사람 공간 정보"]
                                                }
                                            }
                                        }
                                    },
                                }
                            }
                        }
                    },
                }
            }
        return spec