import calendar
from datetime import date
from typing import Any

import flet as ft


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
SELECTED = "#666666"
ACCENT = "#3F8C85"
ACCENT_DARK = "#244743"
ACCENT_LIGHT = "#A9E8DF"


# ---------------------------------------------------------
# Demonstration bookings
# ---------------------------------------------------------

DEMO_SESSIONS: list[dict[str, Any]] = [
    {
        "year": 2026,
        "month": 8,
        "day": 18,
        "time": "2:00 PM",
        "skill": "Beginner Guitar",
        "teacher": "Sam",
        "duration": "1 hour",
        "format": "Online session",
        "location": None,
        "type": "online",
        "icon": ft.Icons.MUSIC_NOTE,
    },
    {
        "year": 2026,
        "month": 8,
        "day": 19,
        "time": "3:30 PM",
        "skill": "Football Training",
        "teacher": "Daniel",
        "duration": "90 minutes",
        "format": "In-person session",
        "location": (
            "Riverside Sports Centre, Main Football Pitch"
        ),
        "type": "in_person",
        "icon": ft.Icons.SPORTS_SOCCER,
    },
]


def main(page: ft.Page) -> None:
    page.title = "SkillSwap Sessions Demo"
    page.padding = 0
    page.bgcolor = PAGE_BACKGROUND
    page.theme_mode = ft.ThemeMode.DARK

    state: dict[str, Any] = {
        "year": 2026,
        "month": 8,
        "selected_day": 18,
        "session_tab": 0,
        "mobile_mode": True,
    }

    main_content = ft.Container(expand=True)

    app_shell = ft.Container(
        width=390,
        height=800,
        bgcolor=BACKGROUND,
        border_radius=20,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        border=ft.Border.all(1, "#4A4A4A"),
    )

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    def sessions_for_day(day: int) -> list[dict[str, Any]]:
        return [
            session
            for session in DEMO_SESSIONS
            if session["year"] == state["year"]
            and session["month"] == state["month"]
            and session["day"] == day
        ]

    def day_has_session(day: int) -> bool:
        return bool(sessions_for_day(day))

    def format_selected_date() -> str:
        selected = date(
            state["year"],
            state["month"],
            state["selected_day"],
        )

        return selected.strftime("%A, %d %B %Y")

    def close_dialog(event: ft.ControlEvent) -> None:
        page.pop_dialog()

    def show_message(message: str) -> None:
        dialog = ft.AlertDialog(
            title=ft.Text("Demo complete"),
            content=ft.Text(message),
            actions=[
                ft.TextButton(
                    "Close",
                    on_click=close_dialog,
                )
            ],
        )

        page.show_dialog(dialog)

    # ---------------------------------------------------------
    # Booking dialogs
    # ---------------------------------------------------------

    def complete_booking_action(
        event: ft.ControlEvent,
        session: dict[str, Any],
    ) -> None:
        page.pop_dialog()

        if session["type"] == "online":
            show_message(
                f"You joined the demo "
                f"{session['skill']} session."
            )
        else:
            show_message(
                f"You checked in for "
                f"{session['skill']} at "
                f"{session['location']}."
            )

    def show_booking_dialog(
        event: ft.ControlEvent,
        session: dict[str, Any],
    ) -> None:
        is_online = session["type"] == "online"

        details: list[ft.Control] = [
            ft.Text(
                f"{session['skill']} with "
                f"{session['teacher']}",
                size=17,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.CALENDAR_MONTH,
                        size=18,
                        color=ACCENT,
                    ),
                    ft.Text(
                        date(
                            session["year"],
                            session["month"],
                            session["day"],
                        ).strftime("%A, %d %B %Y")
                    ),
                ]
            ),
            ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.SCHEDULE,
                        size=18,
                        color=ACCENT,
                    ),
                    ft.Text(
                        f"{session['time']} · "
                        f"{session['duration']}"
                    ),
                ]
            ),
        ]

        if is_online:
            details.extend(
                [
                    ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.VIDEO_CALL_OUTLINED,
                                size=18,
                                color=ACCENT,
                            ),
                            ft.Text("Online demonstration meeting"),
                        ]
                    ),
                    ft.Text(
                        "No real video call will begin. "
                        "The button only demonstrates the "
                        "joining process.",
                        color=SECONDARY_TEXT,
                    ),
                ]
            )
        else:
            details.extend(
                [
                    ft.Row(
                        vertical_alignment=(
                            ft.CrossAxisAlignment.START
                        ),
                        controls=[
                            ft.Icon(
                                ft.Icons.LOCATION_ON_OUTLINED,
                                size=20,
                                color=ACCENT,
                            ),
                            ft.Text(
                                session["location"],
                                expand=True,
                            ),
                        ],
                    ),
                    ft.Text(
                        "Arrive around 10 minutes early and "
                        "meet the coach beside the main "
                        "football pitch.",
                        color=SECONDARY_TEXT,
                    ),
                ]
            )

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Join demo session"
                if is_online
                else "In-person booking"
            ),
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=details,
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=close_dialog,
                ),
                ft.FilledButton(
                    content=(
                        "Join now"
                        if is_online
                        else "Check in"
                    ),
                    icon=(
                        ft.Icons.VIDEO_CALL
                        if is_online
                        else ft.Icons.LOCATION_ON
                    ),
                    bgcolor=ACCENT,
                    color="#FFFFFF",
                    on_click=lambda e, selected=session: (
                        complete_booking_action(e, selected)
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.show_dialog(dialog)

    # ---------------------------------------------------------
    # Mobile and desktop modes
    # ---------------------------------------------------------

    mode_button = ft.IconButton(
        icon=ft.Icons.PHONE_IPHONE,
        tooltip="Switch to desktop mode",
    )

    def toggle_device_mode(event: ft.ControlEvent) -> None:
        state["mobile_mode"] = not state["mobile_mode"]

        if state["mobile_mode"]:
            app_shell.width = 390
            app_shell.height = 800
            app_shell.border_radius = 20

            mode_button.icon = ft.Icons.PHONE_IPHONE
            mode_button.tooltip = "Switch to desktop mode"
        else:
            app_shell.width = 900
            app_shell.height = 760
            app_shell.border_radius = 8

            mode_button.icon = ft.Icons.DESKTOP_WINDOWS
            mode_button.tooltip = "Switch to mobile mode"

        page.update()

    mode_button.on_click = toggle_device_mode

    # ---------------------------------------------------------
    # Session cards
    # ---------------------------------------------------------

    def session_card(
        session: dict[str, Any],
    ) -> ft.Container:
        is_online = session["type"] == "online"

        information: list[ft.Control] = [
            ft.Row(
                wrap=True,
                spacing=8,
                controls=[
                    ft.Icon(
                        ft.Icons.SCHEDULE,
                        size=18,
                        color=SECONDARY_TEXT,
                    ),
                    ft.Text(
                        session["time"],
                        color=SECONDARY_TEXT,
                    ),
                    ft.Icon(
                        ft.Icons.TIMER_OUTLINED,
                        size=18,
                        color=SECONDARY_TEXT,
                    ),
                    ft.Text(
                        session["duration"],
                        color=SECONDARY_TEXT,
                    ),
                ],
            ),
            ft.Row(
                controls=[
                    ft.Icon(
                        (
                            ft.Icons.VIDEO_CALL_OUTLINED
                            if is_online
                            else ft.Icons.PERSON_PIN_CIRCLE_OUTLINED
                        ),
                        size=18,
                        color=SECONDARY_TEXT,
                    ),
                    ft.Text(
                        session["format"],
                        color=SECONDARY_TEXT,
                    ),
                ],
            ),
        ]

        if not is_online:
            information.append(
                ft.Row(
                    vertical_alignment=(
                        ft.CrossAxisAlignment.START
                    ),
                    controls=[
                        ft.Icon(
                            ft.Icons.LOCATION_ON_OUTLINED,
                            size=18,
                            color=ACCENT,
                        ),
                        ft.Text(
                            session["location"],
                            expand=True,
                            color=SECONDARY_TEXT,
                        ),
                    ],
                )
            )

        return ft.Container(
            bgcolor=SURFACE_LIGHT,
            border_radius=12,
            padding=16,
            border=ft.Border.all(1, BORDER),
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        vertical_alignment=(
                            ft.CrossAxisAlignment.CENTER
                        ),
                        controls=[
                            ft.Container(
                                width=44,
                                height=44,
                                border_radius=12,
                                bgcolor=ACCENT,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Icon(
                                    session["icon"],
                                    color="#FFFFFF",
                                ),
                            ),
                            ft.Column(
                                expand=True,
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        session["skill"],
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        f"With {session['teacher']}",
                                        color=SECONDARY_TEXT,
                                    ),
                                ],
                            ),
                            ft.Container(
                                padding=ft.Padding.symmetric(
                                    horizontal=9,
                                    vertical=5,
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
                    *information,
                    ft.FilledButton(
                        content=(
                            "Join Meeting"
                            if is_online
                            else "View Location and Check In"
                        ),
                        icon=(
                            ft.Icons.VIDEO_CALL
                            if is_online
                            else ft.Icons.LOCATION_ON
                        ),
                        bgcolor=ACCENT,
                        color="#FFFFFF",
                        height=46,
                        on_click=lambda e, selected=session: (
                            show_booking_dialog(e, selected)
                        ),
                    ),
                ],
            ),
        )

    # ---------------------------------------------------------
    # Calendar
    # ---------------------------------------------------------

    month_title = ft.Text(
        "",
        size=19,
        weight=ft.FontWeight.BOLD,
        color=PRIMARY_TEXT,
    )

    calendar_grid = ft.Column(spacing=6)

    selected_date_text = ft.Text(
        "",
        size=14,
        weight=ft.FontWeight.BOLD,
        color=PRIMARY_TEXT,
    )

    selected_date_area = ft.Container()

    def update_selected_date_area() -> None:
        selected_date_text.value = format_selected_date()

        selected_sessions = sessions_for_day(
            state["selected_day"]
        )

        if selected_sessions:
            selected_date_area.content = ft.Column(
                spacing=12,
                controls=[
                    selected_date_text,
                    *[
                        session_card(session)
                        for session in selected_sessions
                    ],
                ],
            )
        else:
            selected_date_area.content = ft.Column(
                spacing=8,
                horizontal_alignment=(
                    ft.CrossAxisAlignment.CENTER
                ),
                controls=[
                    selected_date_text,
                    ft.Text(
                        "No sessions scheduled for this date.",
                        color=SECONDARY_TEXT,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            )

    def select_day(day: int) -> None:
        state["selected_day"] = day

        build_calendar()
        update_selected_date_area()
        page.update()

    def make_day_cell(
        day: int | None,
    ) -> ft.Control:
        if day is None:
            return ft.Container(height=42)

        is_selected = day == state["selected_day"]
        has_booking = day_has_session(day)

        return ft.Container(
            height=42,
            alignment=ft.Alignment.CENTER,
            border_radius=21,
            bgcolor=SELECTED if is_selected else None,
            ink=True,
            on_click=lambda e, selected_day=day: (
                select_day(selected_day)
            ),
            content=ft.Stack(
                width=38,
                height=38,
                controls=[
                    ft.Container(
                        alignment=ft.Alignment.CENTER,
                        content=ft.Text(
                            str(day),
                            size=14,
                            color=(
                                PRIMARY_TEXT
                                if is_selected
                                else SECONDARY_TEXT
                            ),
                            weight=(
                                ft.FontWeight.BOLD
                                if is_selected
                                else ft.FontWeight.NORMAL
                            ),
                        ),
                    ),
                    ft.Container(
                        visible=has_booking,
                        alignment=ft.Alignment.BOTTOM_CENTER,
                        padding=ft.Padding.only(bottom=2),
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
            f"{calendar.month_name[month]} {year}"
        )

        month_calendar = calendar.Calendar(
            firstweekday=6
        ).monthdayscalendar(year, month)

        weekday_names = [
            "Sun",
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri",
            "Sat",
        ]

        rows: list[ft.Control] = [
            ft.Row(
                controls=[
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Text(
                            weekday,
                            size=12,
                            color=SECONDARY_TEXT,
                        ),
                    )
                    for weekday in weekday_names
                ]
            )
        ]

        for week in month_calendar:
            rows.append(
                ft.Row(
                    controls=[
                        ft.Container(
                            expand=True,
                            content=make_day_cell(
                                day if day != 0 else None
                            ),
                        )
                        for day in week
                    ]
                )
            )

        calendar_grid.controls = rows

    def change_month(amount: int) -> None:
        new_month = state["month"] + amount
        new_year = state["year"]

        if new_month < 1:
            new_month = 12
            new_year -= 1

        elif new_month > 12:
            new_month = 1
            new_year += 1

        state["month"] = new_month
        state["year"] = new_year
        state["selected_day"] = 1

        build_calendar()
        update_selected_date_area()
        page.update()

    # ---------------------------------------------------------
    # Session tab pages
    # ---------------------------------------------------------

    session_body = ft.Container(expand=True)

    def empty_state(
        icon: str,
        heading: str,
        description: str,
    ) -> ft.Control:
        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            padding=30,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=(
                    ft.CrossAxisAlignment.CENTER
                ),
                spacing=12,
                controls=[
                    ft.Icon(
                        icon,
                        size=58,
                        color=SECONDARY_TEXT,
                    ),
                    ft.Text(
                        heading,
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        description,
                        color=SECONDARY_TEXT,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
        )

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
                        ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.CHEVRON_LEFT,
                            bgcolor=SURFACE_LIGHT,
                            on_click=lambda e: change_month(-1),
                        ),
                        month_title,
                        ft.IconButton(
                            icon=ft.Icons.CHEVRON_RIGHT,
                            bgcolor=SURFACE_LIGHT,
                            on_click=lambda e: change_month(1),
                        ),
                    ],
                ),
                ft.Container(
                    bgcolor=SURFACE,
                    border=ft.Border.all(1, BORDER),
                    border_radius=10,
                    padding=12,
                    content=calendar_grid,
                ),
                ft.Container(
                    bgcolor=SURFACE,
                    border_radius=12,
                    padding=16,
                    content=selected_date_area,
                ),
            ],
        )

    def upcoming_view() -> ft.Control:
        controls: list[ft.Control] = [
            ft.Text(
                "Upcoming sessions",
                size=18,
                weight=ft.FontWeight.BOLD,
            )
        ]

        for session in DEMO_SESSIONS:
            session_date = date(
                session["year"],
                session["month"],
                session["day"],
            )

            controls.append(
                ft.Column(
                    spacing=8,
                    controls=[
                        ft.Text(
                            session_date.strftime(
                                "%A, %d %B %Y"
                            ),
                            color=SECONDARY_TEXT,
                        ),
                        session_card(session),
                    ],
                )
            )

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=14,
            controls=controls,
        )

    session_tab_names = [
        "Calendar",
        "Requests",
        "Upcoming",
        "Teaching",
        "Completed",
    ]

    session_tab_buttons: list[ft.TextButton] = []

    def show_session_tab(index: int) -> None:
        state["session_tab"] = index

        for button_index, button in enumerate(
            session_tab_buttons
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
                shape=ft.RoundedRectangleBorder(
                    radius=7
                ),
            )

        if index == 0:
            session_body.content = calendar_view()

        elif index == 1:
            session_body.content = empty_state(
                ft.Icons.MAIL_OUTLINE,
                "No booking requests",
                "New booking requests will appear here.",
            )

        elif index == 2:
            session_body.content = upcoming_view()

        elif index == 3:
            session_body.content = empty_state(
                ft.Icons.SCHOOL_OUTLINED,
                "No teaching sessions",
                "Sessions you teach will appear here.",
            )

        else:
            session_body.content = empty_state(
                ft.Icons.CHECK_CIRCLE_OUTLINE,
                "No completed sessions",
                "Completed sessions will appear here.",
            )

        page.update()

    for index, tab_name in enumerate(
        session_tab_names
    ):
        session_tab_buttons.append(
            ft.TextButton(
                content=ft.Text(
                    tab_name,
                    size=13,
                ),
                on_click=lambda e, tab_index=index: (
                    show_session_tab(tab_index)
                ),
            )
        )

    session_tabs = ft.Row(
        controls=session_tab_buttons,
        scroll=ft.ScrollMode.AUTO,
        spacing=3,
    )

    sessions_screen = ft.Container(
        expand=True,
        bgcolor=BACKGROUND,
        padding=ft.Padding.only(
            left=18,
            right=18,
            top=20,
            bottom=8,
        ),
        content=ft.Column(
            expand=True,
            spacing=12,
            controls=[
                ft.Row(
                    alignment=(
                        ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    controls=[
                        ft.Text(
                            "Sessions",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                        ),
                        mode_button,
                    ],
                ),
                ft.Container(
                    bgcolor=SURFACE,
                    border_radius=9,
                    padding=3,
                    content=session_tabs,
                ),
                session_body,
            ],
        ),
    )

    # ---------------------------------------------------------
    # Bottom navigation
    # ---------------------------------------------------------

    def placeholder_screen(
        title: str,
        icon: str,
    ) -> ft.Control:
        return ft.Container(
            expand=True,
            bgcolor=BACKGROUND,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
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
                        "This page is not included in the demo.",
                        color=SECONDARY_TEXT,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
        )

    bottom_pages = [
        lambda: placeholder_screen(
            "Home",
            ft.Icons.HOME_OUTLINED,
        ),
        lambda: placeholder_screen(
            "Discover",
            ft.Icons.SEARCH,
        ),
        lambda: placeholder_screen(
            "Friends",
            ft.Icons.GROUP_OUTLINED,
        ),
        lambda: placeholder_screen(
            "Profile",
            ft.Icons.PERSON_OUTLINE,
        ),
        lambda: sessions_screen,
    ]

    def change_bottom_page(
        event: ft.ControlEvent,
    ) -> None:
        selected_index = event.control.selected_index
        main_content.content = bottom_pages[
            selected_index
        ]()
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
                icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
                selected_icon=ft.Icons.CALENDAR_MONTH,
                label="Sessions",
            ),
        ],
    )

    app_shell.content = ft.Column(
        expand=True,
        spacing=0,
        controls=[
            main_content,
            bottom_navigation,
        ],
    )

    main_content.content = sessions_screen

    page.add(
        ft.Container(
            expand=True,
            alignment=ft.Alignment.TOP_CENTER,
            padding=20,
            content=app_shell,
        )
    )

    show_session_tab(0)


if __name__ == "__main__":
    ft.run(
        main,
        port=8550,
        view=ft.AppView.WEB_BROWSER,
    )