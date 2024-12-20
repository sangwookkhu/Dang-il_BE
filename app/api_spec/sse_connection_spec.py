class SSEConnectSpec:
    @staticmethod
    def sse_connect():
        spec = {
            "summary": "서버 push를 위한 sse 연결 생성하는 엔드포인트",
            "description": 
                """
                    서버 push 메시지를 위한 sse 연결 생성하는 엔드포인트 <br><br> 
                    해당 sse 연결을 통해 친구 신청, 친구 수락, 공지 사항 같은 것들을 받음 <br><br> 
                    메시지 종류는 메시지의 source 필드를 통해 구분 <br><br> 
                    쿠키에  session_id 필수 <br><br> 

                    메시지 예시
                    친구 요청
                    {
                        "source": /friend/apply,
                        "data": {
                            "sender_id": sender_id,
                            "receiver_id": receiver_id
                        }
                    }
                """,
            "operation_id": "sse_connect",
            "responses": {
                200: {
                    "description": "별도의 응답 존재하지 X, 모두 메시지로 처리",
                    },
                }
            }
        return spec