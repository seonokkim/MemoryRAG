from app.core.errors import not_found
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserProfileResponse
from sqlalchemy.orm import Session


class UserService:
    def __init__(self, db: Session) -> None:
        self.repo = UserRepository(db)

    def get_profile(self, user_id: int) -> UserProfileResponse:
        user = self.repo.get_user_with_profile(user_id)
        if not user:
            raise not_found("User", user_id)
        profile = user.profile
        memories = self.repo.list_active_memories(user_id, limit=5)
        return UserProfileResponse(
            user_id=user.id,
            name=user.name,
            email=user.email,
            level=user.level,
            dominant_hand=user.dominant_hand,
            goal=profile.goal if profile else None,
            golfer_type=profile.golfer_type if profile else None,
            current_main_issue=profile.current_main_issue if profile else None,
            preferred_feedback_style=profile.preferred_feedback_style if profile else None,
            profile_summary=profile.profile_summary if profile else None,
            memory_summary=[m.content for m in memories],
        )
