import calendar
from datetime import date, time
from typing import Any, Callable, Awaitable

import flet as ft

from database import create_supabase_client
from friends_chat import FriendsChatFeature


# ---------------------------------------------------------
# Colours
# ---------------------------------------------------------

BACKGROUND = "#101010"
PAGE_BACKGROUND = "#242424"
SURFACE = "#202020"
SURFACE_LIGHT = "#2B2B2B"
BORDER = "#343434"

PRIMARY_TEXT = "#F3F3F3"
SECONDARY_TEXT = "#A8A8A8"

SELECTED = "#707070"
ACCENT = "#3F8C85"
ACCENT_DARK = "#244743"
ACCENT_LIGHT = "#A9E8DF"


def main(page: ft.Page) -> None:
    page.title = "SkillSwap"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = PAGE_BACKGROUND
    page.padding = 0

    supabase = create_supabase_client()
    launcher = ft.UrlLauncher()

    state: dict[str, Any] = {
        "user": None,
        "mobile_mode": True,
        "year": 2026,
        "month": 8,
        "selected_day": 18,
        "session_tab": 0,
        "bookings": [],
    }

    app_shell = ft.Container(
        width=390,
        height=820,
        bgcolor=BACKGROUND,
        border_radius=24,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        border=ft.Border.all(2, "#666666"),
    )

    root = ft.Container(
        expand=True,
        alignment=ft.Alignment.TOP_CENTER,
        padding=20,
        content=app_shell,
    )

    # ---------------------------------------------------------
    # General helpers
    # ---------------------------------------------------------

    def close_dialog(event: ft.ControlEvent) -> None:
        page.pop_dialog()

    def show_error(message: str) -> None:
        page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("Something went wrong"),
                content=ft.Text(message),
                actions=[
                    ft.TextButton(
                        "Close",
                        on_click=close_dialog,
                    )
                ],
            )
        )

    def format_booking_date(value: Any) -> str:
        try:
            parsed = date.fromisoformat(str(value))
            return parsed.strftime("%A, %d %B %Y")
        except (TypeError, ValueError):
            return str(value or "")

    def format_booking_time(value: Any) -> str:
        try:
            cleaned = str(value).split("+")[0]
            parsed = time.fromisoformat(cleaned)
            return parsed.strftime("%-I:%M %p")
        except (TypeError, ValueError):
            return str(value or "")

    def normalise_format(
        booking: dict[str, Any],
    ) -> str:
        return (
            str(booking.get("format") or "")
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )

    def is_online(
        booking: dict[str, Any],
    ) -> bool:
        return normalise_format(booking) in {
            "online",
            "online_session",
            "video",
            "video_call",
        }

    friends_feature = FriendsChatFeature(
        page=page,
        supabase=supabase,
        state=state,
        background=BACKGROUND,
        surface=SURFACE,
        surface_light=SURFACE_LIGHT,
        border=BORDER,
        primary_text=PRIMARY_TEXT,
        secondary_text=SECONDARY_TEXT,
        accent=ACCENT,
        accent_dark=ACCENT_DARK,
        accent_light=ACCENT_LIGHT,
    )

    # ---------------------------------------------------------
    # Authentication screen
    # ---------------------------------------------------------

    email_field = ft.TextField(
        label="Email",
        keyboard_type=ft.KeyboardType.EMAIL,
        autofocus=True,
        border_radius=10,
    )

    password_field = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        border_radius=10,
    )

    auth_message = ft.Text(
        color=SECONDARY_TEXT,
        text_align=ft.TextAlign.CENTER,
    )

    login_button = ft.FilledButton(
        content="Log in",
        bgcolor=ACCENT,
        color="#FFFFFF",
        height=48,
    )

    register_button = ft.OutlinedButton(
        content="Create account",
        height=48,
    )

    def validate_auth_fields() -> bool:
        email = (email_field.value or "").strip()
        password = password_field.value or ""

        if not email or not password:
            auth_message.value = (
                "Enter your email and password."
            )
            page.update()
            return False

        if len(password) < 6:
            auth_message.value = (
                "Your password must contain at least "
                "6 characters."
            )
            page.update()
            return False

        return True

    def set_auth_loading(
        loading: bool,
    ) -> None:
        login_button.disabled = loading
        register_button.disabled = loading

        if loading:
            auth_message.value = "Please wait..."

        page.update()

    def handle_login(
        event: ft.ControlEvent,
    ) -> None:
        if not validate_auth_fields():
            return

        set_auth_loading(True)

        try:
            response = (
                supabase.auth.sign_in_with_password(
                    {
                        "email": (
                            email_field.value or ""
                        ).strip(),
                        "password": (
                            password_field.value or ""
                        ),
                    }
                )
            )

            if response.user is None:
                auth_message.value = "Login failed."
                return

            state["user"] = response.user
            friends_feature.on_login(response.user)
            show_sessions_page()

        except Exception as error:
            auth_message.value = (
                f"Login failed: {error}"
            )

        finally:
            set_auth_loading(False)

    def handle_register(
        event: ft.ControlEvent,
    ) -> None:
        if not validate_auth_fields():
            return

        set_auth_loading(True)

        try:
            response = supabase.auth.sign_up(
                {
                    "email": (
                        email_field.value or ""
                    ).strip(),
                    "password": (
                        password_field.value or ""
                    ),
                }
            )

            if response.session is None:
                auth_message.value = (
                    "Account created. Check your email, "
                    "confirm the account, and then log in."
                )
            else:
                state["user"] = response.user
                friends_feature.on_login(response.user)
                show_sessions_page()

        except Exception as error:
            auth_message.value = (
                f"Registration failed: {error}"
            )

        finally:
            set_auth_loading(False)

    login_button.on_click = handle_login
    register_button.on_click = handle_register

    def show_login_page() -> None:
        auth_message.value = ""
        password_field.value = ""

        app_shell.content = ft.Container(
            expand=True,
            bgcolor=BACKGROUND,
            padding=30,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                tight=True,
                horizontal_alignment=(
                    ft.CrossAxisAlignment.CENTER
                ),
                spacing=16,
                controls=[
                    ft.Container(
                        width=90,
                        height=90,
                        border_radius=20,
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        content=ft.Image(
                        src="logo.png",
                        width=90,
                        height=90,
                        fit=ft.BoxFit.CONTAIN,
                    ),
                    ),
                    ft.Text(
                        "SkillSwap",
                        size=30,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        "Log in to view your sessions",
                        color=SECONDARY_TEXT,
                    ),
                    email_field,
                    password_field,
                    ft.Container(
                        width=350,
                        content=login_button,
                    ),
                    ft.Container(
                        width=350,
                        content=register_button,
                    ),
                    auth_message,
                ],
            ),
        )

        page.update()

    # ---------------------------------------------------------
    # Mobile/Desktop mode
    # ---------------------------------------------------------

    mode_button = ft.IconButton(
        icon=ft.Icons.PHONE_IPHONE,
        tooltip="Switch to desktop mode",
    )

    def toggle_device_mode(
        event: ft.ControlEvent,
    ) -> None:
        state["mobile_mode"] = (
            not state["mobile_mode"]
        )

        if state["mobile_mode"]:
            app_shell.width = 390
            app_shell.height = 820
            app_shell.border_radius = 24

            mode_button.icon = (
                ft.Icons.PHONE_IPHONE
            )
            mode_button.tooltip = (
                "Switch to desktop mode"
            )
        else:
            app_shell.width = 900
            app_shell.height = 760
            app_shell.border_radius = 8

            mode_button.icon = (
                ft.Icons.DESKTOP_WINDOWS
            )
            mode_button.tooltip = (
                "Switch to mobile mode"
            )

        page.update()

    mode_button.on_click = toggle_device_mode

    # ---------------------------------------------------------
    # Booking helpers
    # ---------------------------------------------------------

    def booking_date(
        booking: dict[str, Any],
    ) -> date | None:
        try:
            return date.fromisoformat(
                str(booking["session_date"])
            )
        except (
            KeyError,
            TypeError,
            ValueError,
        ):
            return None

    def bookings_for_day(
        day: int,
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []

        for booking in state["bookings"]:
            parsed = booking_date(booking)

            if (
                parsed is not None
                and parsed.year == state["year"]
                and parsed.month == state["month"]
                and parsed.day == day
            ):
                results.append(booking)

        return results

    def day_has_booking(day: int) -> bool:
        return bool(bookings_for_day(day))

    # ---------------------------------------------------------
    # Meeting functionality
    # ---------------------------------------------------------

    async def join_meeting(
        event: ft.ControlEvent,
        booking: dict[str, Any],
    ) -> None:
        room_name = str(
            booking.get("meeting_room") or ""
        ).strip()

        if not room_name:
            show_error(
                "This booking does not have "
                "a meeting room."
            )
            return

        safe_room_name = (
            room_name
            .replace(" ", "-")
            .replace("/", "-")
        )

        meeting_url = (
            f"https://meet.jit.si/"
            f"{safe_room_name}"
        )

        try:
            await launcher.launch_url(
                meeting_url,
                web_only_window_name="_blank",
            )
        except Exception as error:
            show_error(
                f"Could not open the meeting: {error}"
            )

    def make_join_handler(
        booking: dict[str, Any],
    ) -> Callable[
        [ft.ControlEvent],
        Awaitable[None],
    ]:
        async def handle_join(
            event: ft.ControlEvent,
        ) -> None:
            await join_meeting(
                event,
                booking,
            )

        return handle_join

    # ---------------------------------------------------------
    # Location functionality
    # ---------------------------------------------------------

    def show_location(
        event: ft.ControlEvent,
        booking: dict[str, Any],
    ) -> None:
        location = (
            booking.get("location")
            or "No location provided."
        )

        page.show_dialog(
            ft.AlertDialog(
                title=ft.Text(
                    "Session location"
                ),
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    horizontal_alignment=(
                        ft.CrossAxisAlignment.CENTER
                    ),
                    controls=[
                        ft.Icon(
                            ft.Icons.LOCATION_ON,
                            size=44,
                            color=ACCENT,
                        ),
                        ft.Text(
                            str(location),
                            size=16,
                            text_align=(
                                ft.TextAlign.CENTER
                            ),
                        ),
                    ],
                ),
                actions=[
                    ft.TextButton(
                        "Close",
                        on_click=close_dialog,
                    )
                ],
            )
        )

    def make_location_handler(
        booking: dict[str, Any],
    ) -> Callable[
        [ft.ControlEvent],
        None,
    ]:
        def handle_location(
            event: ft.ControlEvent,
        ) -> None:
            show_location(
                event,
                booking,
            )

        return handle_location

    # ---------------------------------------------------------
    # Booking cards
    # ---------------------------------------------------------

    def booking_card(
        booking: dict[str, Any],
        show_date: bool = False,
    ) -> ft.Container:
        online = is_online(booking)

        title = (
            booking.get("title")
            or "Skill session"
        )

        teacher = (
            booking.get("teacher_name")
            or booking.get("teacher")
            or "SkillSwap member"
        )

        details: list[ft.Control] = []

        if show_date:
            details.append(
                ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.CALENDAR_MONTH,
                            size=18,
                            color=SECONDARY_TEXT,
                        ),
                        ft.Text(
                            format_booking_date(
                                booking.get(
                                    "session_date"
                                )
                            ),
                            color=SECONDARY_TEXT,
                        ),
                    ]
                )
            )

        details.extend(
            [
                ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.SCHEDULE,
                            size=18,
                            color=SECONDARY_TEXT,
                        ),
                        ft.Text(
                            format_booking_time(
                                booking.get(
                                    "session_time"
                                )
                            ),
                            color=SECONDARY_TEXT,
                        ),
                    ]
                ),
                ft.Row(
                    controls=[
                        ft.Icon(
                            (
                                ft.Icons
                                .VIDEO_CALL_OUTLINED
                                if online
                                else ft.Icons
                                .PERSON_PIN_CIRCLE_OUTLINED
                            ),
                            size=18,
                            color=SECONDARY_TEXT,
                        ),
                        ft.Text(
                            (
                                "Online meeting"
                                if online
                                else "In-person session"
                            ),
                            color=SECONDARY_TEXT,
                        ),
                    ]
                ),
            ]
        )

        if not online:
            details.append(
                ft.Row(
                    vertical_alignment=(
                        ft.CrossAxisAlignment.START
                    ),
                    controls=[
                        ft.Icon(
                            ft.Icons
                            .LOCATION_ON_OUTLINED,
                            size=18,
                            color=ACCENT,
                        ),
                        ft.Text(
                            str(
                                booking.get(
                                    "location"
                                )
                                or (
                                    "No location "
                                    "provided"
                                )
                            ),
                            expand=True,
                            color=SECONDARY_TEXT,
                        ),
                    ],
                )
            )

        if online:
            action_button = ft.FilledButton(
                content="Join Meeting",
                icon=ft.Icons.VIDEO_CALL,
                bgcolor=ACCENT,
                color="#FFFFFF",
                height=44,
                on_click=make_join_handler(
                    booking
                ),
            )
        else:
            action_button = ft.FilledButton(
                content="View Location",
                icon=ft.Icons.LOCATION_ON,
                bgcolor=ACCENT,
                color="#FFFFFF",
                height=44,
                on_click=make_location_handler(
                    booking
                ),
            )

        return ft.Container(
            bgcolor=SURFACE_LIGHT,
            border=ft.Border.all(1, BORDER),
            border_radius=12,
            padding=15,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                width=44,
                                height=44,
                                border_radius=12,
                                bgcolor=ACCENT,
                                alignment=(
                                    ft.Alignment.CENTER
                                ),
                                content=ft.Icon(
                                    (
                                        ft.Icons
                                        .VIDEO_CALL
                                        if online
                                        else ft.Icons
                                        .SPORTS_SOCCER
                                    ),
                                    color="#FFFFFF",
                                ),
                            ),
                            ft.Column(
                                expand=True,
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        str(title),
                                        size=16,
                                        weight=(
                                            ft.FontWeight
                                            .BOLD
                                        ),
                                    ),
                                    ft.Text(
                                        f"With {teacher}",
                                        color=(
                                            SECONDARY_TEXT
                                        ),
                                    ),
                                ],
                            ),
                            ft.Container(
                                padding=(
                                    ft.Padding.symmetric(
                                        horizontal=9,
                                        vertical=5,
                                    )
                                ),
                                border_radius=12,
                                bgcolor=ACCENT_DARK,
                                content=ft.Text(
                                    "Upcoming",
                                    size=11,
                                    color=ACCENT_LIGHT,
                                ),
                            ),
                        ],
                    ),
                    ft.Divider(
                        height=1,
                        color=BORDER,
                    ),
                    *details,
                    action_button,
                ],
            ),
        )

    # ---------------------------------------------------------
    # Calendar controls
    # ---------------------------------------------------------

    month_title = ft.Text(
        "",
        size=19,
        weight=ft.FontWeight.BOLD,
    )

    calendar_grid = ft.Column(
        spacing=6
    )

    selected_date_area = ft.Container()

    def selected_date_text() -> str:
        selected = date(
            state["year"],
            state["month"],
            state["selected_day"],
        )

        return selected.strftime(
            "%A, %d %B %Y"
        )

    def update_selected_date_area() -> None:
        selected_bookings = bookings_for_day(
            state["selected_day"]
        )

        controls: list[ft.Control] = [
            ft.Text(
                selected_date_text(),
                size=14,
                weight=ft.FontWeight.BOLD,
            )
        ]

        if selected_bookings:
            controls.extend(
                booking_card(booking)
                for booking in selected_bookings
            )
        else:
            controls.append(
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text(
                        (
                            "No sessions scheduled "
                            "for this date."
                        ),
                        color=SECONDARY_TEXT,
                        text_align=(
                            ft.TextAlign.CENTER
                        ),
                    ),
                )
            )

        selected_date_area.content = (
            ft.Column(
                spacing=12,
                controls=controls,
            )
        )

    def select_day(day: int) -> None:
        state["selected_day"] = day

        build_calendar()
        update_selected_date_area()
        page.update()

    def day_cell(
        day: int | None,
    ) -> ft.Control:
        if day is None:
            return ft.Container(height=42)

        selected = (
            day == state["selected_day"]
        )

        has_booking = day_has_booking(day)

        return ft.Container(
            height=42,
            alignment=ft.Alignment.CENTER,
            border_radius=21,
            bgcolor=(
                SELECTED if selected else None
            ),
            ink=True,
            on_click=(
                lambda event, value=day:
                select_day(value)
            ),
            content=ft.Stack(
                width=38,
                height=38,
                controls=[
                    ft.Container(
                        alignment=(
                            ft.Alignment.CENTER
                        ),
                        content=ft.Text(
                            str(day),
                            size=14,
                            color=(
                                PRIMARY_TEXT
                                if selected
                                else SECONDARY_TEXT
                            ),
                            weight=(
                                ft.FontWeight.BOLD
                                if selected
                                else (
                                    ft.FontWeight
                                    .NORMAL
                                )
                            ),
                        ),
                    ),
                    ft.Container(
                        visible=has_booking,
                        alignment=(
                            ft.Alignment
                            .BOTTOM_CENTER
                        ),
                        padding=ft.Padding.only(
                            bottom=2
                        ),
                        content=ft.Container(
                            width=6,
                            height=6,
                            border_radius=3,
                            bgcolor=ACCENT,
                        ),
                    ),
                ],
            ),
        )

    def build_calendar() -> None:
        year = state["year"]
        month = state["month"]

        month_title.value = (
            f"{calendar.month_name[month]} "
            f"{year}"
        )

        month_rows = calendar.Calendar(
            firstweekday=6
        ).monthdayscalendar(
            year,
            month,
        )

        weekday_names = [
            "Sun",
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri",
            "Sat",
        ]

        controls: list[ft.Control] = [
            ft.Row(
                spacing=0,
                controls=[
                    ft.Container(
                        expand=True,
                        alignment=(
                            ft.Alignment.CENTER
                        ),
                        content=ft.Text(
                            weekday,
                            size=12,
                            color=SECONDARY_TEXT,
                        ),
                    )
                    for weekday in weekday_names
                ],
            )
        ]

        for week in month_rows:
            controls.append(
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.Container(
                            expand=True,
                            content=day_cell(
                                day
                                if day
                                else None
                            ),
                        )
                        for day in week
                    ],
                )
            )

        calendar_grid.controls = controls

    def change_month(
        amount: int,
    ) -> None:
        new_month = (
            state["month"] + amount
        )
        new_year = state["year"]

        if new_month < 1:
            new_month = 12
            new_year -= 1
        elif new_month > 12:
            new_month = 1
            new_year += 1

        state["year"] = new_year
        state["month"] = new_month
        state["selected_day"] = 1

        build_calendar()
        update_selected_date_area()
        page.update()

    def calendar_view() -> ft.Control:
        build_calendar()
        update_selected_date_area()

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=16,
            controls=[
                ft.Row(
                    alignment=(
                        ft.MainAxisAlignment
                        .SPACE_BETWEEN
                    ),
                    controls=[
                        ft.IconButton(
                            icon=(
                                ft.Icons
                                .CHEVRON_LEFT
                            ),
                            bgcolor=SURFACE_LIGHT,
                            on_click=lambda event: (
                                change_month(-1)
                            ),
                        ),
                        month_title,
                        ft.IconButton(
                            icon=(
                                ft.Icons
                                .CHEVRON_RIGHT
                            ),
                            bgcolor=SURFACE_LIGHT,
                            on_click=lambda event: (
                                change_month(1)
                            ),
                        ),
                    ],
                ),
                ft.Container(
                    bgcolor=SURFACE,
                    border=ft.Border.all(
                        1,
                        BORDER,
                    ),
                    border_radius=10,
                    padding=10,
                    content=calendar_grid,
                ),
                ft.Container(
                    bgcolor=SURFACE,
                    border_radius=12,
                    padding=14,
                    content=selected_date_area,
                ),
            ],
        )

    # ---------------------------------------------------------
    # Sessions tabs
    # ---------------------------------------------------------

    session_body = ft.Container(
        expand=True
    )

    tab_names = [
        "Calendar",
        "Requests",
        "Upcoming",
        "Teaching",
        "Completed",
    ]

    tab_buttons: list[
        ft.TextButton
    ] = []

    def empty_tab(
        icon: str,
        title: str,
        message: str,
    ) -> ft.Control:
        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            padding=30,
            content=ft.Column(
                tight=True,
                horizontal_alignment=(
                    ft.CrossAxisAlignment.CENTER
                ),
                spacing=12,
                controls=[
                    ft.Icon(
                        icon,
                        size=56,
                        color=SECONDARY_TEXT,
                    ),
                    ft.Text(
                        title,
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        text_align=(
                            ft.TextAlign.CENTER
                        ),
                    ),
                    ft.Text(
                        message,
                        color=SECONDARY_TEXT,
                        text_align=(
                            ft.TextAlign.CENTER
                        ),
                    ),
                ],
            ),
        )

    def upcoming_view() -> ft.Control:
        controls: list[ft.Control] = [
            ft.Text(
                "Upcoming sessions",
                size=18,
                weight=ft.FontWeight.BOLD,
            )
        ]

        if not state["bookings"]:
            controls.append(
                empty_tab(
                    ft.Icons.EVENT_BUSY,
                    "No upcoming sessions",
                    (
                        "Your shared bookings "
                        "will appear here."
                    ),
                )
            )
        else:
            sorted_bookings = sorted(
                state["bookings"],
                key=lambda item: (
                    str(
                        item.get(
                            "session_date"
                        )
                        or ""
                    ),
                    str(
                        item.get(
                            "session_time"
                        )
                        or ""
                    ),
                ),
            )

            controls.extend(
                booking_card(
                    booking,
                    show_date=True,
                )
                for booking
                in sorted_bookings
            )

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=14,
            controls=controls,
        )

    def show_session_tab(
        index: int,
    ) -> None:
        state["session_tab"] = index

        for button_index, button in enumerate(
            tab_buttons
        ):
            button.style = ft.ButtonStyle(
                bgcolor=(
                    SURFACE_LIGHT
                    if button_index == index
                    else None
                ),
                color=(
                    PRIMARY_TEXT
                    if button_index == index
                    else SECONDARY_TEXT
                ),
                shape=(
                    ft.RoundedRectangleBorder(
                        radius=7
                    )
                ),
            )

        if index == 0:
            session_body.content = (
                calendar_view()
            )
        elif index == 1:
            session_body.content = empty_tab(
                ft.Icons.MAIL_OUTLINE,
                "No booking requests",
                (
                    "New booking requests "
                    "will appear here."
                ),
            )
        elif index == 2:
            session_body.content = (
                upcoming_view()
            )
        elif index == 3:
            session_body.content = empty_tab(
                ft.Icons.SCHOOL_OUTLINED,
                "No teaching sessions",
                (
                    "Sessions you teach "
                    "will appear here."
                ),
            )
        else:
            session_body.content = empty_tab(
                ft.Icons
                .CHECK_CIRCLE_OUTLINE,
                "No completed sessions",
                (
                    "Completed sessions "
                    "will appear here."
                ),
            )

        page.update()

    for index, tab_name in enumerate(
        tab_names
    ):
        tab_buttons.append(
            ft.TextButton(
                content=ft.Text(
                    tab_name,
                    size=13,
                ),
                on_click=(
                    lambda event, value=index:
                    show_session_tab(value)
                ),
            )
        )

    tabs_row = ft.Row(
        controls=tab_buttons,
        spacing=3,
        scroll=ft.ScrollMode.AUTO,
    )

    loading = ft.ProgressRing(
        visible=False,
        width=22,
        height=22,
    )

    # ---------------------------------------------------------
    # Load Supabase bookings
    # ---------------------------------------------------------

    def load_bookings() -> None:
        loading.visible = True
        page.update()

        try:
            response = (
                supabase
                .table("bookings")
                .select("*")
                .eq(
                    "status",
                    "upcoming",
                )
                .order("session_date")
                .order("session_time")
                .execute()
            )

            state["bookings"] = (
                response.data or []
            )

            if state["bookings"]:
                first_date = booking_date(
                    state["bookings"][0]
                )

                if first_date is not None:
                    state["year"] = (
                        first_date.year
                    )
                    state["month"] = (
                        first_date.month
                    )
                    state["selected_day"] = (
                        first_date.day
                    )

            show_session_tab(
                state["session_tab"]
            )

        except Exception as error:
            state["bookings"] = []

            show_error(
                "Could not load bookings: "
                f"{error}"
            )

        finally:
            loading.visible = False
            page.update()

    def refresh_bookings(
        event: ft.ControlEvent,
    ) -> None:
        load_bookings()

    # ---------------------------------------------------------
    # Sessions screen and navigation
    # ---------------------------------------------------------

    def logout(
        event: ft.ControlEvent,
    ) -> None:
        try:
            supabase.auth.sign_out()
        except Exception:
            pass

        state["user"] = None
        state["bookings"] = []
        friends_feature.reset()

        show_login_page()

    def placeholder_page(
        title: str,
        icon: str,
    ) -> ft.Control:
        return ft.Container(
            expand=True,
            bgcolor=BACKGROUND,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                tight=True,
                horizontal_alignment=(
                    ft.CrossAxisAlignment.CENTER
                ),
                spacing=12,
                controls=[
                    ft.Icon(
                        icon,
                        size=60,
                        color=SECONDARY_TEXT,
                    ),
                    ft.Text(
                        title,
                        size=24,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        (
                            "This page is not "
                            "included in the demo."
                        ),
                        color=SECONDARY_TEXT,
                        text_align=(
                            ft.TextAlign.CENTER
                        ),
                    ),
                ],
            ),
        )

    user_email_text = ft.Text(
        "",
        size=11,
        color=SECONDARY_TEXT,
    )

    sessions_screen = ft.Container(
        expand=True,
        bgcolor=BACKGROUND,
        padding=ft.Padding.only(
            left=18,
            right=18,
            top=18,
            bottom=8,
        ),
        content=ft.Column(
            expand=True,
            spacing=12,
            controls=[
                ft.Row(
                    alignment=(
                        ft.MainAxisAlignment
                        .SPACE_BETWEEN
                    ),
                    controls=[
                        ft.Column(
                            spacing=1,
                            controls=[
                                ft.Text(
                                    "Sessions",
                                    size=24,
                                    weight=(
                                        ft.FontWeight
                                        .BOLD
                                    ),
                                ),
                                user_email_text,
                            ],
                        ),
                        ft.Row(
                            spacing=0,
                            controls=[
                                loading,
                                ft.IconButton(
                                    icon=(
                                        ft.Icons
                                        .REFRESH
                                    ),
                                    tooltip="Refresh",
                                    on_click=(
                                        refresh_bookings
                                    ),
                                ),
                                mode_button,
                                ft.IconButton(
                                    icon=(
                                        ft.Icons
                                        .LOGOUT
                                    ),
                                    tooltip="Log out",
                                    on_click=logout,
                                ),
                            ],
                        ),
                    ],
                ),
                ft.Container(
                    bgcolor=SURFACE,
                    border_radius=9,
                    padding=3,
                    content=tabs_row,
                ),
                session_body,
            ],
        ),
    )

    main_area = ft.Container(
        expand=True
    )

    bottom_pages = [
        lambda: placeholder_page(
            "Home",
            ft.Icons.HOME_OUTLINED,
        ),
        lambda: placeholder_page(
            "Discover",
            ft.Icons.SEARCH,
        ),
        lambda: friends_feature.build_page(),
        lambda: placeholder_page(
            "Profile",
            ft.Icons.PERSON_OUTLINE,
        ),
        lambda: sessions_screen,
    ]

    def change_bottom_page(
        event: ft.ControlEvent,
    ) -> None:
        index = event.control.selected_index

        main_area.content = (
            bottom_pages[index]()
        )

        page.update()

    bottom_navigation = ft.NavigationBar(
        selected_index=4,
        bgcolor=SURFACE,
        indicator_color=SURFACE_LIGHT,
        on_change=change_bottom_page,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME,
                label="Home",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.SEARCH,
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
                icon=(
                    ft.Icons
                    .CALENDAR_MONTH_OUTLINED
                ),
                selected_icon=(
                    ft.Icons.CALENDAR_MONTH
                ),
                label="Sessions",
            ),
        ],
    )

    def show_sessions_page() -> None:
        user = state["user"]

        if user is None:
            show_login_page()
            return

        user_email_text.value = (
            user.email
            or "Logged-in user"
        )

        main_area.content = sessions_screen

        app_shell.content = ft.Column(
            expand=True,
            spacing=0,
            controls=[
                main_area,
                bottom_navigation,
            ],
        )

        show_session_tab(0)
        page.update()
        load_bookings()

    page.add(root)
    show_login_page()

ft.run(
    main,
    view=ft.AppView.WEB_BROWSER,
    host="0.0.0.0",
    port=8000,
    assets_dir="assets",
)