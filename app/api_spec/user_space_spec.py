class UserSpaceSpec:
    @staticmethod
    def space():
        spec = {
            "summary": "경로 파라미터에 들어있는 id의 유저 공간 불러오는 엔드포인트(테스트X)",
            "description": 
                """
                    path_user_id에 값을 넣어 해당 id의 유저 공간+작업 시간을 불러오는 엔드포인트 <br><br>  
                    본인, 친구, 접근을 허용해둔(accessbility가 true) 모르는 사람의 공간정보+작업시간 정보 불러옴 <br><br> 
                    본인, 친구 검증을 위해 쿠키에 session_id 필수
                """,
            "operation_id": "space",
            "responses": {
                200: {
                    "description": "메시지, data(안에 공간 정보, 작업 시간 정보)",
                    "content": {
                            "application/json": {
                                "examples": {
                                    "응답 예시": {
                                        "summary": "응답 예시",
                                        "value": {
                                            "message": "data successfully transferred",
                                            "data": {
                                                "accessibility": True,
                                                "user_space_data": {
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
                                                "user_tasking_time_data": {
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
    
    @staticmethod
    def space_save():
        spec = {
            "summary": "유저 공간 데이터 저장하는 엔드포인트",
            "description": 
                """
                    유저가 공간을 꾸민 후 그 정보를 저장하는 엔드포인트 <br><br> 
                    유저 공간 데이터 중 인테리어 데이터만을 보내면 됨 <br><br> 
                    본인 검증을 위해 쿠키에 session_id 필수
                """,
            "operation_id": "space_save",
            "responses": {
                200: {
                    "description": "유저의 인테리어 데이터 리스트를 요청 본문으로 받고 업데이트된 공간 데이터 전체를 응답",
                    "content": {
                            "application/json": {
                                "examples": {
                                    "응답 예시": {
                                        "summary": "응답 예시",
                                        "value": {
                                            "message": "space data successfully updated",
                                            "data": {
                                                "accessibility": True,
                                                "user_space_data": {
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

    @staticmethod
    def space_delete():
        spec = {
            "summary": "유저 공간 데이터 초기화하는 엔드포인트",
            "description": 
                """
                    유저 공간 데이터 초기화하는 엔드포인트 <br><br>
                    본인 검증을 위해 쿠키에 session_id 필수
                """,
            "operation_id": "space_delete",
            "responses": {
                200: {
                    "description": "유저 공간 데이터를 초기화하는 엔드포인트",
                    "content": {
                            "application/json": {
                                "examples": {
                                    "응답 예시": {
                                        "summary": "응답 예시",
                                        "value": {
                                            "message": "space data successfully deleted",
                                        }
                                    },
                                }
                            }
                        }
                    },
                }
            }
        return spec
    
    @staticmethod
    def space_get_todo():
        spec = {
            "summary": "본인 할일(Todo) 불러오는 엔드포인트",
            "description": 
                """
                    본인 Todo list 불러오는 엔드포인트 <br><br> 
                    본인 검증을 위해 쿠키에 session_id 필수
                """,
            "operation_id": "space_get_todo",
            "responses": {
                200: {
                    "description": "유저 본인이 기존에 설정한 TodoList 불러오기",
                    "content": {
                            "application/json": {
                                "examples": {
                                    "응답 예시": {
                                        "summary": "응답 예시",
                                        "value": {
                                            "message": "todo data successfully transmitted",
                                            "todo": ['국어', '수학']
                                        }
                                    },
                                }
                            }
                        }
                    },
                }
            }
        return spec
    
    @staticmethod
    def space_post_todo():
        spec = {
            "summary": "본인 할일(Todo) 저장하는 엔드포인트",
            "description": 
                """
                    본인 Todo list 저장하는 엔드포인트 <br><br> 
                    본인 검증을 위해 쿠키에 session_id 필수
                """,
            "operation_id": "space_post_todo",
            "responses": {
                200: {
                    "description": "유저 본인이 변경한 TodoList 데이터 불러오기",
                    "content": {
                            "application/json": {
                                "examples": {
                                    "응답 예시": {
                                        "summary": "응답 예시",
                                        "value": {
                                            "message": "todo data successfully saved",
                                            "todo": ['국어', '수학']
                                        }
                                    },
                                }
                            }
                        }
                    },
                }
            }
        return spec
    
    @staticmethod
    def space_delete_todo():
        spec = {
            "summary": "본인 할일(Todo) 전체 삭제하는 엔드포인트",
            "description": 
                """
                    본인 Todo list 저장하는 엔드포인트 <br><br> 
                    본인 검증을 위해 쿠키에 session_id 필수
                """,
            "operation_id": "space_delete_todo",
            "responses": {
                200: {
                    "description": "유저가 기존에 설정한 할일(Todo) 전체 삭제 후 메시지만 응답",
                    "content": {
                            "application/json": {
                                "examples": {
                                    "응답 예시": {
                                        "summary": "응답 예시",
                                        "value": {
                                            "message": "todo data successfully deleted"
                                        }
                                    },
                                }
                            }
                        }
                    },
                }
            }
        return spec
    
    @staticmethod
    def space_board():
        spec = {
            "summary": "개인 공간의 게시판의 글들을 모두 가져오는 엔드포인트",
            "description": 
                """
                    개인 공간의 게시판 글들을 모두 가져오는 엔드포인트 <br><br> 
                    경로 파라미터 path_user_id에 글을 작성하는 개인 공간의 주인 user_id를 넣어서 사용 <br><br>
                    세션 id 필요하지 않음 <br><br>
                    모든 사람들이 사용 가능
                """,
            "operation_id": "space_board",
            "responses": {
                200: {
                    "description": "해당 유저의 개인 페이지에 작성되어 있는 게시판의 메모들 불러오기",
                    "content": {
                            "application/json": {
                                "examples": {
                                    "응답 예시": {
                                        "summary": "응답 예시",
                                        "value": {
                                            "board_data": [{
                                                "sender_id":"test1", 
                                                "sender_name": "test1",
                                                "content": "메모에요"
                                                }]
                                        }
                                    },
                                }
                            }
                        }
                    },
                }
            }
        return spec
    
    @staticmethod
    def space_board_write():
        spec = {
            "summary": "타인의 개인 공간에서 작성한 메모를 첨부하는 엔드포인트",
            "description": 
                """
                    개인 공간의 게시판 글들을 모두 가져오는 엔드포인트 <br><br> 
                    경로  파라미터 path_user_id에 글을 작성하는 개인 공간의 주인 user_id를 넣어서 사용 <br><br>
                    무분별한 사용을 막기 위한 session_id 필요 
                """,
            "operation_id": "space_board_write",
            # "parameters": [
            #     {
            #         "name": "path_user_id",
            #         "in": "path",
            #         "required": True,
            #         "description": "글을 작성하는 개인 공간 주인의 id",
            #         "schema": {
            #             "type": "string"
            #         }
            #     }
            # ],
            "requestBody": {
                "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "memo": "dict",
                                    "description": "작성하려는 메모 데이터"
                                },
                                "required": ["sender_id", "sender_name", "content"]
                            },
                            "examples": {
                                "요청 예시": {
                                    "summary": "요청 예시",
                                    "value": {
                                        "sender_id": "test1",
                                        "sender_name": "test1",
                                        "content": "게시판에 메모로 작성할 글입니다."
                                    }
                                }
                            }
                        }
                    }
                },
            "responses": {
                200: {
                    "description": "해당 유저의 개인 페이지에 작성되어 있는 게시판의 메모들 불러오기(방금 추가한 내용까지)",
                    "content": {
                            "application/json": {
                                "examples": {
                                    "응답 예시": {
                                        "summary": "응답 예시",
                                        "value": {
                                            "board_data": [{
                                                "sender_id":"test1", 
                                                "sender_name": "test1",
                                                "content": "게시판에 메모로 작성할 글입니다."
                                            }]
                                        }
                                    },
                                }
                            }
                        }
                    },
                }
            }
        return spec
    
    @staticmethod
    def space_board_delete():
        spec = {
            "summary": "본인 공간 게시판에 붙어있는 메모 전부 제거하는 엔드포인트",
            "description": 
                """
                    본인 공간 게시판에 붙어있는 메모를 모두 제거하는 엔드포인트 <br><br> 
                    본인 확인을 위한 session_id 필요 
                """,
            "operation_id": "space_board_delete",
            "responses": {
                200: {
                    "description": "메모들이 삭제되었음을 나타내는 메시지 반환",
                    "content": {
                            "application/json": {
                                "examples": {
                                    "응답 예시": {
                                        "summary": "응답 예시",
                                        "value": {
                                            "message": "board has been cleared"
                                        }
                                    },
                                }
                            }
                        }
                    },
                }
            }
        return spec
    
