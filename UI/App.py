import re

import flet as ft


def main(page: ft.Page) -> None:
    page.title = "SkillSwap"
    page.padding = 0
    page.bgcolor = "#F5F7FB"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    current_user_email = ""

    # ---------------------------------------------------------
    # Shared helper functions
    # ---------------------------------------------------------

    def valid_email(email: str) -> bool:
        pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        return bool(re.match(pattern, email))

    def page_header(title: str, subtitle: str) -> ft.Container:
        return ft.Container(
            padding=ft.Padding.only(left=22, right=22, top=28, bottom=15),
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Text(
                        title,
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color="#152238",
                    ),
                    ft.Text(
                        subtitle,
                        size=14,
                        color="#667085",
                    ),
                ],
            ),
        )

    def feature_card(
        icon: str,
        title: str,
        description: str,
    ) -> ft.Container:
        return ft.Container(
            bgcolor="#FFFFFF",
            border_radius=16,
            padding=18,
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=48,
                        height=48,
                        bgcolor="#EEECFF",
                        border_radius=14,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(
                            icon,
                            color="#635BFF",
                            size=26,
                        ),
                    ),
                    ft.Column(
                        expand=True,
                        spacing=4,
                        controls=[
                            ft.Text(
                                title,
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color="#152238",
                            ),
                            ft.Text(
                                description,
                                size=13,
                                color="#667085",
                            ),
                        ],
                    ),
                    ft.Icon(
                        ft.Icons.CHEVRON_RIGHT,
                        color="#98A2B3",
                    ),
                ],
            ),
        )

    # ---------------------------------------------------------
    # Main app pages
    # ---------------------------------------------------------

    def home_page() -> ft.Control:
        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                page_header(
                    "Welcome to SkillSwap",
                    "Learn something new by sharing what you know.",
                ),
                ft.Container(
                    margin=ft.Margin.only(left=20, right=20),
                    padding=22,
                    border_radius=20,
                    bgcolor="#635BFF",
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Text(
                                "Your time balance",
                                color="#EAE8FF",
                                size=14,
                            ),
                            ft.Text(
                                "2 hours",
                                color="#FFFFFF",
                                size=32,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "Teach a skill to earn more time.",
                                color="#EAE8FF",
                                size=13,
                            ),
                        ],
                    ),
                ),
                ft.Container(height=10),
                ft.Container(
                    padding=ft.Padding.only(left=20, right=20),
                    content=ft.Text(
                        "Quick actions",
                        size=19,
                        weight=ft.FontWeight.BOLD,
                        color="#152238",
                    ),
                ),
                ft.Container(
                    padding=ft.Padding.only(left=20, right=20),
                    content=ft.Column(
                        spacing=12,
                        controls=[
                            feature_card(
                                ft.Icons.SEARCH,
                                "Find a skill",
                                "Discover people who can teach you.",
                            ),
                            feature_card(
                                ft.Icons.ADD_CIRCLE_OUTLINE,
                                "Offer a skill",
                                "Share your knowledge and earn time.",
                            ),
                            feature_card(
                                ft.Icons.CALENDAR_MONTH_OUTLINED,
                                "Upcoming session",
                                "You do not have a session booked yet.",
                            ),
                        ],
                    ),
                ),
                ft.Container(height=25),
            ],
        )

    def discover_page() -> ft.Control:
        search_box = ft.TextField(
            hint_text="Search for a skill",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=14,
        )

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                page_header(
                    "Discover",
                    "Find skills and people in the community.",
                ),
                ft.Container(
                    padding=ft.Padding.only(left=20, right=20),
                    content=search_box,
                ),
                ft.Container(height=10),
                ft.Container(
                    padding=ft.Padding.only(left=20, right=20),
                    content=ft.Text(
                        "Popular skills",
                        size=19,
                        weight=ft.FontWeight.BOLD,
                    ),
                ),
                ft.Container(
                    padding=ft.Padding.only(left=20, right=20),
                    content=ft.Column(
                        spacing=12,
                        controls=[
                            feature_card(
                                ft.Icons.LANGUAGE,
                                "Learn Spanish",
                                "Practise with community members.",
                            ),
                            feature_card(
                                ft.Icons.PHOTO_CAMERA_OUTLINED,
                                "Photography",
                                "Learn to take better photographs.",
                            ),
                            feature_card(
                                ft.Icons.CODE,
                                "Programming",
                                "Learn Python, websites, or app development.",
                            ),
                            feature_card(
                                ft.Icons.MUSIC_NOTE,
                                "Guitar",
                                "Book a beginner-friendly guitar session.",
                            ),
                        ],
                    ),
                ),
                ft.Container(height=25),
            ],
        )

    def friends_page() -> ft.Control:
        return ft.Column(
            expand=True,
            controls=[
                page_header(
                    "Friends",
                    "Connect with people you learn and teach with.",
                ),
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    padding=30,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(
                                ft.Icons.GROUP_OUTLINED,
                                size=72,
                                color="#98A2B3",
                            ),
                            ft.Text(
                                "No friends yet",
                                size=21,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "Discover people and send your first "
                                "connection request.",
                                text_align=ft.TextAlign.CENTER,
                                color="#667085",
                            ),
                            ft.FilledButton(
                                "Discover people",
                                icon=ft.Icons.SEARCH,
                                on_click=lambda event: select_page(1),
                            ),
                        ],
                    ),
                ),
            ],
        )

    def sessions_page() -> ft.Control:
        return ft.Column(
            expand=True,
            controls=[
                page_header(
                    "Sessions",
                    "Manage your teaching and learning sessions.",
                ),
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    padding=30,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(
                                ft.Icons.CALENDAR_MONTH_OUTLINED,
                                size=72,
                                color="#98A2B3",
                            ),
                            ft.Text(
                                "No upcoming sessions",
                                size=21,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "When you book or accept a session, "
                                "it will appear here.",
                                text_align=ft.TextAlign.CENTER,
                                color="#667085",
                            ),
                            ft.FilledButton(
                                "Find a skill",
                                icon=ft.Icons.SEARCH,
                                on_click=lambda event: select_page(1),
                            ),
                        ],
                    ),
                ),
            ],
        )

    def profile_page() -> ft.Control:
        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                page_header(
                    "Profile",
                    "Manage your account and skills.",
                ),
                ft.Container(
                    padding=20,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.CircleAvatar(
                                radius=42,
                                bgcolor="#635BFF",
                                content=ft.Icon(
                                    ft.Icons.PERSON,
                                    color="#FFFFFF",
                                    size=45,
                                ),
                            ),
                            ft.Text(
                                "SkillSwap User",
                                size=22,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                current_user_email,
                                color="#667085",
                            ),
                        ],
                    ),
                ),
                ft.Container(
                    padding=ft.Padding.only(left=20, right=20),
                    content=ft.Column(
                        spacing=12,
                        controls=[
                            feature_card(
                                ft.Icons.SCHOOL_OUTLINED,
                                "Skills I teach",
                                "Add or edit the skills you can offer.",
                            ),
                            feature_card(
                                ft.Icons.LIGHTBULB_OUTLINE,
                                "Skills I want to learn",
                                "Manage your learning interests.",
                            ),
                            feature_card(
                                ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
                                "Time wallet",
                                "View your time credits and activity.",
                            ),
                            feature_card(
                                ft.Icons.SETTINGS_OUTLINED,
                                "Settings",
                                "Change your account preferences.",
                            ),
                        ],
                    ),
                ),
                ft.Container(
                    padding=20,
                    content=ft.OutlinedButton(
                        "Sign out",
                        icon=ft.Icons.LOGOUT,
                        on_click=lambda event: show_login(),
                    ),
                ),
            ],
        )

    main_content = ft.Container(
        expand=True,
        bgcolor="#F5F7FB",
    )

    navigation = ft.NavigationBar(
        selected_index=0,
        bgcolor="#FFFFFF",
        indicator_color="#E8E5FF",
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME,
                label="Home",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.EXPLORE_OUTLINED,
                selected_icon=ft.Icons.EXPLORE,
                label="Discover",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.GROUP_OUTLINED,
                selected_icon=ft.Icons.GROUP,
                label="Friends",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.PERSON_OUTLINE,
                selected_icon=ft.Icons.PERSON,
                label="Profile",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
                selected_icon=ft.Icons.CALENDAR_MONTH,
                label="Sessions",
            ),
        ],
    )

    app_pages = [
        home_page,
        discover_page,
        friends_page,
        profile_page,
        sessions_page,
    ]

    def select_page(index: int) -> None:
        navigation.selected_index = index
        main_content.content = app_pages[index]()
        page.update()

    def navigation_changed(event: ft.ControlEvent) -> None:
        select_page(event.control.selected_index)

    navigation.on_change = navigation_changed

    def show_main_app() -> None:
        page.clean()
        page.navigation_bar = navigation
        navigation.selected_index = 0
        main_content.content = home_page()
        page.add(main_content)
        page.update()

    # ---------------------------------------------------------
    # Login page
    # ---------------------------------------------------------

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
    )

    login_message = ft.Text(
        "",
        size=13,
        color="#B42318",
        text_align=ft.TextAlign.CENTER,
    )

    def sign_in(event: ft.ControlEvent) -> None:
        nonlocal current_user_email

        email = (email_input.value or "").strip()
        password = password_input.value or ""

        email_input.error_text = None
        password_input.error_text = None
        login_message.value = ""

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
                "Password must contain at least 8 characters."
            )
            has_error = True

        if has_error:
            page.update()
            return

        current_user_email = email
        show_main_app()

    password_input.on_submit = sign_in

    def show_login() -> None:
        page.clean()
        page.navigation_bar = None

        email_input.value = ""
        password_input.value = ""
        email_input.error_text = None
        password_input.error_text = None
        login_message.value = ""

        login_card = ft.Container(
            width=430,
            bgcolor="#FFFFFF",
            padding=28,
            border_radius=20,
            content=ft.Column(
                spacing=14,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=65,
                        height=65,
                        bgcolor="#635BFF",
                        border_radius=18,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(
                            ft.Icons.SWAP_HORIZ_ROUNDED,
                            color="#FFFFFF",
                            size=38,
                        ),
                    ),
                    ft.Text(
                        "SkillSwap",
                        size=34,
                        weight=ft.FontWeight.BOLD,
                        color="#152238",
                    ),
                    ft.Text(
                        "Share your time. Learn something new.",
                        color="#667085",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=5),
                    ft.Text(
                        "Welcome back",
                        size=25,
                        weight=ft.FontWeight.BOLD,
                    ),
                    email_input,
                    password_input,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Checkbox(
                                label="Remember me",
                                value=False,
                            ),
                            ft.TextButton(
                                "Forgot password?",
                                on_click=lambda event: setattr(
                                    login_message,
                                    "value",
                                    "Password recovery will be added later.",
                                ),
                            ),
                        ],
                    ),
                    ft.Container(
                        width=400,
                        content=ft.FilledButton(
                            "Sign in",
                            icon=ft.Icons.LOGIN,
                            height=52,
                            on_click=sign_in,
                        ),
                    ),
                    login_message,
                    ft.Row(
                        controls=[
                            ft.Divider(expand=True),
                            ft.Text("OR", color="#98A2B3"),
                            ft.Divider(expand=True),
                        ],
                    ),
                    ft.Container(
                        width=400,
                        content=ft.OutlinedButton(
                            "Continue with Google",
                            icon=ft.Icons.ACCOUNT_CIRCLE_OUTLINED,
                            height=52,
                            on_click=lambda event: setattr(
                                login_message,
                                "value",
                                "Google authentication still needs "
                                "to be configured.",
                            ),
                        ),
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                "Don't have an account?",
                                color="#667085",
                            ),
                            ft.TextButton(
                                "Sign up",
                                on_click=lambda event: setattr(
                                    login_message,
                                    "value",
                                    "The sign-up form will be connected next.",
                                ),
                            ),
                        ],
                    ),
                ],
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

        page.update()

    show_login()


if __name__ == "__main__":
    ft.run(
        main,
        port=8550,
        view=ft.AppView.WEB_BROWSER,
    )