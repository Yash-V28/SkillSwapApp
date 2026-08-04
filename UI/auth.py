from typing import Any

from database import supabase


def register_user(
    email: str,
    password: str,
) -> dict[str, Any]:
    response = supabase.auth.sign_up(
        {
            "email": email.strip(),
            "password": password,
        }
    )

    return {
        "user": response.user,
        "session": response.session,
    }


def login_user(
    email: str,
    password: str,
) -> dict[str, Any]:
    response = supabase.auth.sign_in_with_password(
        {
            "email": email.strip(),
            "password": password,
        }
    )

    return {
        "user": response.user,
        "session": response.session,
    }


def logout_user() -> None:
    supabase.auth.sign_out()