import os, sys, dotenv
dotenv.load_dotenv(encoding="utf-8")
sys.path.append(os.getenv("BACKEND_PATH"))

from unittest import IsolatedAsyncioTestCase, main
# 테스트 대상
from app.services.auth_service import AuthService
from app.schemas.service_dto.auth_dto import (
    AuthGoogleLoginInput,
    AuthGoogleLoginOutput,
    AuthGoogleRegisterInput,
    AuthGoogleRegisterOutput,
)

class AuthServiceTest(IsolatedAsyncioTestCase):
    async def testSetup(self):
        self.target = AuthService.get_instance()
    
    async def test_google_register1(self):
        input1 = AuthGoogleRegisterInput(
            id="test1",
            name="test1",
            email="test1"
        )
        self.assertEqual(
            self.target.google_register(input1),
            AuthGoogleRegisterOutput(
                id= "test1",
                name="test1",
                email="test1",
                
            )
        )





if(__name__ == "__main__"):
    main()




