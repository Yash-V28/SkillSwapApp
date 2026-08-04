import re

import flet as ft


def main(page: ft.Page) -> None:
    """Build the SkillSwap login page."""

    page.title = "SkillSwap"
    page.padding = 0
    page.bgcolor = "#F5F7FB"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Restrict the desktop window to a sensible minimum size.
    page.window.min_width = 360
    page.window.min_height = 650

    title = ft.Text(
        "SkillSwap",
        size=34,
        weight=ft.FontWeight.BOLD,
        color="#152238",
    )

    subtitle = ft.Text(
        "Share your time. Teach what you know.\nLearn something new.",
        size=15,
        color="#667085",
        text_align=ft.TextAlign.CENTER,
    )

    email_input = ft.TextField(
        label="Email address",
        hint_text="name@example.com",
        keyboard_type=ft.KeyboardType.EMAIL,
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        border_radius=12,
        autofocus=True,
    )

    password_input = ft.TextField(
        label="Password",
        hint_text="Enter your password",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        border_radius=12,
        on_submit=lambda event: log_in(event),
    )

    remember_me = ft.Checkbox(
        label="Remember me",
        value=False,
    )

    message = ft.Text(
        "",
        size=14,
        text_align=ft.TextAlign.CENTER,
    )

    def valid_email(email: str) -> bool:
        """Return True when the email has a basic valid structure."""
        pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        return bool(re.match(pattern, email))

    def show_message(text: str, colour: str) -> None:
        message.value = text
        message.color = colour
        page.update()

    def log_in(event: ft.ControlEvent) -> None:
        """Validate the form and process the temporary demo login."""

        email = (email_input.value or "").strip()
        password = password_input.value or ""

        email_input.error_text = None
        password_input.error_text = None
        message.value = ""

        has_error = False

        if not email:
            email_input.error_text = "Enter your email address."
            has_error = True
        elif not valid_email(email):
            email_input.error_text = "Enter a valid email address."
            has_error = True

        if not password:
            password_input.error_text = "Enter your password."
            has_error = True
        elif len(password) < 8:
            password_input.error_text = (
                "Your password must contain at least 8 characters."
            )
            has_error = True

        if has_error:
            page.update()
            return

        # This is temporary until a real database and authentication
        # system are connected.
        show_message(
            "Login details accepted. Authentication will be added next.",
            "#087443",
        )

    def forgot_password(event: ft.ControlEvent) -> None:
        show_message(
            "Password recovery has not been connected yet.",
            "#475467",
        )

    def create_account(event: ft.ControlEvent) -> None:
        show_message(
            "The account creation page will be added next.",
            "#475467",
        )

    login_button = ft.ElevatedButton(
        content=ft.Text(
            "Log in",
            size=16,
            weight=ft.FontWeight.BOLD,
        ),
        width=400,
        height=52,
        bgcolor="#635BFF",
        color="#FFFFFF",
        on_click=log_in,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
    )

    login_card = ft.Container(
        width=440,
        padding=ft.Padding.all(28),
        bgcolor="#FFFFFF",
        border_radius=20,
        shadow=ft.BoxShadow(
            blur_radius=24,
            color="#1A000000",
            offset=ft.Offset(0, 8),
        ),
        content=ft.Column(
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=62,
                            height=62,
                            bgcolor="#635BFF",
                            border_radius=18,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(
                                ft.Icons.SWAP_HORIZ_ROUNDED,
                                color="#FFFFFF",
                                size=36,
                            ),
                        )
                    ],
                ),
                title,
                subtitle,
                ft.Container(height=8),
                email_input,
                password_input,
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        remember_me,
                        ft.TextButton(
                            content=ft.Text("Forgot password?"),
                            on_click=forgot_password,
                        ),
                    ],
                ),
                login_button,
                message,
                ft.Divider(height=24),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "Don't have an account?",
                            color="#667085",
                        ),
                        ft.TextButton(
                            content=ft.Text("Create account"),
                            on_click=create_account,
                        ),
                    ],
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=14,
        ),
    )

    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Container(
                expand=True,
                padding=20,
                alignment=ft.Alignment.CENTER,
                content=login_card,
            ),
        )
    )


if __name__ == "__main__":
    ft.run(main)