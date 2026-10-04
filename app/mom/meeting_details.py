from app.schemas.mom import MeetingDetails

def create_default_details(title: str = "Project Review") -> MeetingDetails:
    return MeetingDetails(
        title=title,
        date="Not specified",
        time="Not specified",
        location="Not specified",
        meeting_type="Internal Review"
    )