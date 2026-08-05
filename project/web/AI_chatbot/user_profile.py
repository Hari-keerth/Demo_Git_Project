from web.models import ATSResult


def get_user_profile(user):
    """
    Return the latest parsed resume JSON for the user.
    """

    latest_result = (
        ATSResult.objects
        .filter(user=user)
        .order_by("-created_at")
        .first()
    )

    if latest_result:

        return latest_result.resume_json

    return {}