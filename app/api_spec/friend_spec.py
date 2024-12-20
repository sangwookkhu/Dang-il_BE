from app.schemas.request_dto.friend_request import FriendApplyRequest

class FriendSpec:
    @staticmethod
    def friend_apply():
        spec = {
            "summary": "친구 요청 보내는 엔드포인트",
            "description": """
                다른 유저에게 친구신청 보내면 sse 연결을 통해 메시지가 감  <br><br>  
                이후 해당 유저가 친구 신청을 수락 또는 거절 가능 <br><br>  
                친구 신청 대기 중 또는 거절 이후 3일이 지나야 다시 신청 가능 <br><br> 
                쿠키에 session_id 필수
            """,
            "operation_id": "friend_apply",  # 고유한 Operation ID 제공
            "responses": {
                200: {
                    "description": "성공적인 요청 응답",
                    "content": {
                        "application/json": {
                            "examples": {
                                "친구 신청 예시": {
                                    "summary": "친구 신청 예시",
                                    "value": {
                                        "message": "Request has been successfully sent",
                                        "data": {
                                            "sender_id": "친구 신청 보낸 사람(본인) id",
                                            "receiver_id": "친구 신청 받은 사람 id"
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                204: {
                    "description": "이미 친구이거나 친구 신청을 한지 3일이 지나지 않은 경우",
                    "content": {
                        "application/json": {
                            "examples": {
                                "이미 친구인 경우 예시": {
                                    "summary": "이미 친구인 경우 예시",
                                    "value": {
                                        "message": "This friend is already added."
                                    }
                                },
                                "친구 신청 보낸지 3일 이내 예시": {
                                    "summary": "친구 신청 보낸지 3일 이내 예시",
                                    "value": {
                                        "message": "The request was sent within 3 days"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        return spec
    
    @staticmethod
    def friend_apply_response():
        spec = {
            "summary": "친구 요청 수락 또는 거절하는 엔드포인트",
            "description": """
                친구 신청이 오면 이를 수락 또는 거절 <br><br>  
                수락 시 친구 신청을 보낸 유저에게 sse 메시지가 감<br><br> 
                쿠키에 session_id 필수  

                친구 승낙 시 sse 메시지
                {
                    "source": /friend/apply/response,
                    "data": {
                        "consent_status": True or False,
                        "sender_id": 요청 보낸 사람 id,
                        "receiver_id": 요청 받은 사람 id
                    }
                }
            """,
            "operation_id": "friend_apply_response",  # 고유한 Operation ID 제공
            "responses": {
                200: {
                    "description": "친구 수락 또는 거절 시 응답",
                    "content": {
                        "application/json": {
                            "examples": {
                                "친구 수락 예시": {
                                    "summary": "친구 수락 예시",
                                    "value": {
                                        "message": "Friend request accepted successfully",
                                        "data": {
                                            "sender_id": "test1",
                                            "receiver_id": "test2"
                                        }
                                    }
                                },
                                "친구 거절 예시": {
                                    "summary": "친구 거절 예시",
                                    "value":  {
                                        "message": "Friend request denied successfully",
                                        "data": {
                                            "sender_id": "test1",
                                            "receiver_id": "test2"
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                400:{
                    "description": "처리 대기 중인 요청이 없는 경우",
                    "content": {
                        "application/json": {
                            "examples": {
                                "응답 예시": {
                                    "summary": "응답 예시",
                                    "value": {
                                        "detail": "Requested data does not exist"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        return spec

    @staticmethod
    def friend_search():
        spec = {
            "summary": "친구(유저) 검색하는 엔드포인트",
            "description": """
                요청 본문에 검색어 포함해 보낼 시 일치하는 유저 반환 <br><br>  
                검색어로는 이름(name), 태그(tag) 사용 가능 
            """,
            "operation_id": "friend_search",  # 고유한 Operation ID 제공
            "responses": {
                200: {
                    "description": "검색어와 일치하는 사용자가 있을 때 응답",
                    "content": {
                        "application/json": {
                            "examples": {
                                "일치하는 데이터 존재 예시": {
                                    "summary": "일치하는 데이터 존재 예시",
                                    "value":  {
                                        "message":"search data successfully transported",
                                        "user_data_list": ["유저 정보들"]
                                    }
                                }
                            }
                        }
                    }
                },
                204:{
                    "description": "검색어와 일치하는 사용자가 없을 때 응답",
                    "content": {
                        "application/json": {
                            "examples": {
                                "데이터 없을 때 예시": {
                                    "summary": "데이터 없을 때 예시",
                                    "value": {
                                        "message": "The search data does not exist"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        return spec
