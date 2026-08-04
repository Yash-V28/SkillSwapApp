import calendar
from datetime import date

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
SELECTED = "#777777"
ACCENT = "#3F8C85"


# ---------------------------------------------------------
# Demo sessions
# ---------------------------------------------------------

DEMO_SESSIONS = [
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
        "icon": ft.Icons.MUSIC_NOTE,
        "type": "online",
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
        "location": "Riverside Sports Centre, Main Football Pitch",
        "icon": ft.Icons.SPORTS_SOCCER,
        "type": "in_person",
    },
]


def main(page: ft.Page) -> None:
    page.title = "SkillSwap Sessions"
    page.padding = 0
    page.bgcolor = PAGE_BACKGROUND
    page.theme_mode = ft.ThemeMode.DARK

    state = {
        "year": 2026,
        "month": 8,
        "selected_day": 18,
        "session_tab": 0,
        "mobile_mode": True,
        "selected_session": None,
    }

    main_content = ft.Container(expand=True)

    app_shell = ft.Container(
        width=390,
        bgcolor=BACKGROUND,
        border_radius=20,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        border=ft.Border.all(1, "#4A4A4A"),
    )

    # ---------------------------------------------------------
    # Shared helpers
    # ---------------------------------------------------------

    def sessions_for_day(day: int) -> list[dict]:
        return [
            session
            for session in DEMO_SESSIONS
            if session["year"] == state["year"]
            and session["month"] == state["month"]
            and session["day"] == day
        ]

    def has_session(day: int) -> bool:
        return len(sessions_for_day(day)) > 0

    def format_selected_date() -> str:
        selected = date(
            state["year"],
            state["month"],
            state["selected_day"],
        )
        return selected.strftime("%A, %d %B %Y")

    def show_snackbar(message: str) -> None:
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ACCENT,
        )
        page.snack_bar.open = True
        page.update()

    # ---------------------------------------------------------
    # Session dialog
    # ---------------------------------------------------------

    meeting_dialog = ft.AlertDialog(modal=True)

    def close_session_dialog(event: ft.ControlEvent) -> None:
        meeting_dialog.open = False
        page.update()

    def confirm_session_action(event: ft.ControlEvent) -> None:
        session = state["selected_session"]

        if session is None:
            return

        meeting_dialog.open = False
        page.update()

        if session["type"] == "online":
            show_snackbar(
                f"You joined the demo {session['skill']} session."
            )
        else:
            show_snackbar(
                f"You checked in for {session['skill']} at "
                f"{session['location']}."
            )

    def open_session_dialog(
        event: ft.ControlEvent,
        session: dict,
    ) -> None:
        state["selected_session"] = session

        is_online = session["type"] == "online"

        meeting_dialog.title = ft.Text(
            "Join demo session"
            if is_online
            else "Attend in-person session"
        )

        details: list[ft.Control] = [
            ft.Text(
                f"{session['skill']} with {session['teacher']}",
                weight=ft.FontWeight.BOLD,
            ),
            ft.Text(
                f"{session['day']} August 2026 at {session['time']}",
                color=SECONDARY_TEXT,
            ),
            ft.Text(
                f"Duration: {session['duration']}",
                color=SECONDARY_TEXT,
            ),
        ]

        if is_online:
            details.append(
                ft.Text(
                    "This is a demonstration meeting. "
                    "No real video call will start.",
                    color=SECONDARY_TEXT,
                )
            )
        else:
            details.extend(
                [
                    ft.Divider(color=BORDER),
                    ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Icon(
                                ft.Icons.LOCATION_ON_OUTLINED,
                                color=ACCENT,
                            ),
                            ft.Text(
                                session["location"],
                                expand=True,
                            ),
                        ],
                    ),
                    ft.Text(
                        "Arrive around 10 minutes early and meet "
                        "the coach beside the main football pitch.",
                        color=SECONDARY_TEXT,
                    ),
                ]
            )

        meeting_dialog.content = ft.Column(
            tight=True,
            spacing=10,
            controls=details,
        )

        meeting_dialog.actions = [
            ft.TextButton(
                "Cancel",
                on_click=close_session_dialog,
            ),
            ft.FilledButton(
                "Join now" if is_online else "Check in",
                icon=(
                    ft.Icons.VIDEO_CALL
                    if is_online
                    else ft.Icons.LOCATION_ON
                ),
                bgcolor=ACCENT,
                color="#FFFFFF",
                on_click=confirm_session_action,
            ),
        ]

        meeting_dialog.open = True
        page.update()

    page.overlay.append(meeting_dialog)

    # ---------------------------------------------------------
    # Mobile/Desktop mode
    # ---------------------------------------------------------

    mode_button = ft.IconButton(
        icon=ft.Icons.PHONE_IPHONE,
        tooltip="Switch to desktop mode",
    )

    def toggle_device_mode(event: ft.ControlEvent) -> None:
        state["mobile_mode"] = not state["mobile_mode"]

        if state["mobile_mode"]:
            app_shell.width = 390
            app_shell.border_radius = 20
            mode_button.icon = ft.Icons.PHONE_IPHONE
            mode_button.tooltip = "Switch to desktop mode"
        else:
            app_shell.width = 900
            app_shell.border_radius = 8
            mode_button.icon = ft.Icons.DESKTOP_WINDOWS
            mode_button.tooltip = "Switch to mobile mode"

        page.update()

    mode_button.on_click = toggle_device_mode

    # ---------------------------------------------------------
    # Session card
    # ---------------------------------------------------------

    def session_card(session: dict) -> ft.Container:
        is_online = session["type"] == "online"

        information_rows: list[ft.Control] = [
            ft.Row(
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
            information_rows.append(
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.START,
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
                                    horizontal=10,
                                    vertical=5,
                                ),
                                border_radius=12,
                                bgcolor="#244743",
                                content=ft.Text(
                                    "Upcoming",
                                    size=11,
                                    color="#A9E8DF",
                                ),
                            ),
                        ],
                    ),
                    ft.Divider(color=BORDER),
                    *information_rows,
                    ft.FilledButton(
                        (
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
                        on_click=lambda event, selected=session: (
                            open_session_dialog(event, selected)
                        ),
                    ),
                ],
            ),
        )

    # ---------------------------------------------------------
    # Calendar
    # ---------------------------------------------------------

    selected_date_text = ft.Text(
        "",
        size=14,
        weight=ft.FontWeight.BOLD,
        color=PRIMARY_TEXT,
    )

    selected_date_area = ft.Container()
    calendar_grid = ft.Column(spacing=6)

    month_title = ft.Text(
        "",
        size=19,
        weight=ft.FontWeight.BOLD,
        color=PRIMARY_TEXT,
    )

    def update_selected_date_area() -> None:
        selected_date_text.value = format_selected_date()
        selected_sessions = sessions_for_day(state["selected_day"])

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
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
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
        update_selected_date_area()
        build_calendar()
        page.update()

    def make_day_cell(day: int | None) -> ft.Control:
        if day is None:
            return ft.Container(height=42)

        is_selected = day == state["selected_day"]
        day_has_session = has_session(day)

        return ft.Container(
            height=42,
            alignment=ft.Alignment.CENTER,
            border_radius=21,
            bgcolor=SELECTED if is_selected else None,
            ink=True,
            on_click=lambda event, selected_day=day: select_day(
                selected_day
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
                        visible=day_has_session,
                        alignment=ft.Alignment.BOTTOM_CENTER,
                        padding=ft.Padding.only(bottom=2),
                        content=ft.Container(
                            width=5,
                            height=5,
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

        month_title.value = f"{calendar.month_name[month]} {year}"

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
        month = state["month"] + amount
        year = state["year"]

        if month < 1:
            month = 12
            year -= 1
        elif month > 12:
            month = 1
            year += 1

        state["month"] = month
        state["year"] = year
        state["selected_day"] = 1

        build_calendar()
        update_selected_date_area()
        page.update()

    # ---------------------------------------------------------
    # Session tabs
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
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
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
                    ),
                    ft.Text(
                        description,
                        color=SECONDARY_TEXT,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
        )

    def build_calendar_view() -> ft.Control:
        build_calendar()
        update_selected_date_area()

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=16,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.CHEVRON_LEFT,
                            bgcolor=SURFACE_LIGHT,
                            on_click=lambda event: change_month(-1),
                        ),
                        month_title,
                        ft.IconButton(
                            icon=ft.Icons.CHEVRON_RIGHT,
                            bgcolor=SURFACE_LIGHT,
                            on_click=lambda event: change_month(1),
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
        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=14,
            controls=[
                ft.Text(
                    "Upcoming sessions",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),
                *[
                    ft.Column(
                        spacing=8,
                        controls=[
                            ft.Text(
                                date(
                                    session["year"],
                                    session["month"],
                                    session["day"],
                                ).strftime("%A, %d %B %Y"),
                                color=SECONDARY_TEXT,
                            ),
                            session_card(session),
                        ],
                    )
                    for session in DEMO_SESSIONS
                ],
            ],
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

        for button_index, button in enumerate(session_tab_buttons):
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
                shape=ft.RoundedRectangleBorder(radius=7),
            )

        if index == 0:
            session_body.content = build_calendar_view()
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
                "Sessions you are teaching will appear here.",
            )
        else:
            session_body.content = empty_state(
                ft.Icons.CHECK_CIRCLE_OUTLINE,
                "No completed sessions",
                "Completed sessions will appear here.",
            )

        page.update()

    for index, tab_name in enumerate(session_tab_names):
        session_tab_buttons.append(
            ft.TextButton(
                content=ft.Text(tab_name, size=13),
                on_click=lambda event, tab_index=index: show_session_tab(
                    tab_index
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
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
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
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
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
                        "This page is not included in this demo.",
                        color=SECONDARY_TEXT,
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

    def change_bottom_page(event: ft.ControlEvent) -> None:
        selected_index = event.control.selected_index
        main_content.content = bottom_pages[selected_index]()
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
    show_session_tab(0)

    page.add(
        ft.Container(
            expand=True,
            alignment=ft.Alignment.TOP_CENTER,
            padding=20,
            content=app_shell,
        )
    )


if __name__ == "__main__":
    ft.run(
        main,
        port=8550,
        view=ft.AppView.WEB_BROWSER,
    )