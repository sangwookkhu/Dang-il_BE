from app.deps import get_user_space_coll
from app.utils.db_handlers.mongodb_handler import MongoDBHandler

class YouTubeService:
    @staticmethod
    async def save_video_id(user_id: str, video_id: str,
                            user_space_coll:MongoDBHandler = get_user_space_coll()) -> bool:
        update_result = await user_space_coll.update({"_id": user_id}, {"$set": {"music_url.0": video_id}})
        return update_result is not False

    @staticmethod
    async def delete_video_id(user_id: str, video_id: str, 
                              user_space_coll:MongoDBHandler = get_user_space_coll()) -> bool:
        update_result = await user_space_coll.update({"_id": user_id}, {"$pull": {"music_url": video_id}})
        return update_result is not False

    @staticmethod
    async def update_video_id(user_id: str, old_video_id: str, new_video_id: str,
                              user_space_coll:MongoDBHandler = get_user_space_coll()) -> bool:
        update_result = await user_space_coll.update(
            filter={"_id": user_id},
            update={"$set": {"music_url.0": new_video_id}}
        )
        return update_result is not False

def get_youtube_service() -> YouTubeService:
    return YouTubeService()
