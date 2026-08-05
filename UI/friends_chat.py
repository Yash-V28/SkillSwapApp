from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

import flet as ft


class FriendsChatFeature:
    """Friends, requests, and one-to-one chat UI backed by Supabase."""

    def __init__(
        self,
        *,
        page: ft.Page,
        supabase: Any,
        state: dict[str, Any],
        background: str,
        surface: str,
        surface_light: str,
        border: str,
        primary_text: str,
        secondary_text: str,
        accent: str,
        accent_dark: str,
        accent_light: str,
    ) -> None:
        self.page = page
        self.supabase = supabase
        self.state = state
        self.background = background
        self.surface = surface
        self.surface_light = surface_light
        self.border = border
        self.primary_text = primary_text
        self.secondary_text = secondary_text
        self.accent = accent
        self.accent_dark = accent_dark
        self.accent_light = accent_light

        self.current_tab = 0
        self.selected_friend: dict[str, Any] | None = None
        self.message_channel: Any = None
        self.messages: list[dict[str, Any]] = []

        self.search_field = ft.TextField(
            label="Search by email",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=10,
            expand=True,
        )
        self.search_results = ft.Column(spacing=10)
        self.requests_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        self.friends_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        self.messages_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=10,
            auto_scroll=True,
        )
        self.message_field = ft.TextField(
            hint_text="Write a message...",
            multiline=True,
            min_lines=1,
            max_lines=3,
            expand=True,
            border_radius=12,
        )
        self.content_area = ft.Container(expand=True)
        self.loading = ft.ProgressRing(visible=False, width=22, height=22)

    # ------------------------------------------------------------------
    # Session/profile lifecycle
    # ------------------------------------------------------------------

    def on_login(self, user: Any) -> None:
        """Create/update the signed-in user's profile."""
        email = getattr(user, "email", None) or ""
        metadata = getattr(user, "user_metadata", None) or {}
        display_name = metadata.get("display_name") or email.split("@")[0]

        try:
            (
                self.supabase.table("profiles")
                .upsert(
                    {
                        "id": user.id,
                        "email": email,
                        "display_name": display_name,
                        "last_seen_at": datetime.now(timezone.utc).isoformat(),
                    },
                    on_conflict="id",
                )
                .execute()
            )
        except Exception as error:
            self._show_error(f"Could not create your profile: {error}")

    def reset(self) -> None:
        self.selected_friend = None
        self.messages = []
        self.current_tab = 0
        if self.message_channel is not None:
            self.page.run_task(self._remove_message_channel)

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    @property
    def current_user(self) -> Any:
        return self.state.get("user")

    def _show_error(self, message: str) -> None:
        self.page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("Something went wrong"),
                content=ft.Text(message),
                actions=[
                    ft.TextButton(
                        "Close",
                        on_click=lambda _: self.page.pop_dialog(),
                    )
                ],
            )
        )

    def _show_message(self, title: str, message: str) -> None:
        self.page.show_dialog(
            ft.AlertDialog(
                title=ft.Text(title),
                content=ft.Text(message),
                actions=[
                    ft.TextButton(
                        "Close",
                        on_click=lambda _: self.page.pop_dialog(),
                    )
                ],
            )
        )

    def _profile_name(self, profile: dict[str, Any]) -> str:
        return (
            profile.get("display_name")
            or profile.get("email")
            or "SkillSwap user"
        )

    def _avatar(self, profile: dict[str, Any], size: int = 44) -> ft.Control:
        avatar_url = profile.get("avatar_url")
        if avatar_url:
            return ft.CircleAvatar(
                radius=size / 2,
                foreground_image_src=avatar_url,
            )

        name = self._profile_name(profile).strip()
        initial = name[:1].upper() if name else "?"
        return ft.CircleAvatar(
            radius=size / 2,
            bgcolor=self.accent,
            content=ft.Text(initial, color="#FFFFFF", weight=ft.FontWeight.BOLD),
        )

    def _status_text(self, profile: dict[str, Any]) -> str:
        value = profile.get("last_seen_at")
        if not value:
            return "Offline"
        try:
            last_seen = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            age_seconds = (datetime.now(timezone.utc) - last_seen).total_seconds()
            return "Online" if age_seconds < 120 else "Offline"
        except ValueError:
            return "Offline"

    def _set_loading(self, loading: bool) -> None:
        self.loading.visible = loading
        self.page.update()

    # ------------------------------------------------------------------
    # Main Friends page
    # ------------------------------------------------------------------

    def build_page(self) -> ft.Control:
        if self.current_user is None:
            return ft.Container(
                expand=True,
                bgcolor=self.background,
                alignment=ft.Alignment.CENTER,
                content=ft.Text("Log in to use Friends.", color=self.secondary_text),
            )

        self._touch_last_seen()
        self.show_tab(self.current_tab)

        tab_buttons = []
        labels = ["Friends", "Requests", "Find people"]
        icons = [ft.Icons.GROUP, ft.Icons.MAIL_OUTLINE, ft.Icons.PERSON_SEARCH]
        for index, (label, icon) in enumerate(zip(labels, icons)):
            tab_buttons.append(
                ft.TextButton(
                    content=ft.Row(
                        tight=True,
                        spacing=5,
                        controls=[ft.Icon(icon, size=17), ft.Text(label, size=12)],
                    ),
                    style=ft.ButtonStyle(
                        bgcolor=self.surface_light if index == self.current_tab else None,
                        color=self.primary_text if index == self.current_tab else self.secondary_text,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=lambda _, value=index: self.show_tab(value),
                )
            )

        return ft.Container(
            expand=True,
            bgcolor=self.background,
            padding=ft.Padding.only(left=18, right=18, top=18, bottom=8),
            content=ft.Column(
                expand=True,
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=1,
                                controls=[
                                    ft.Text("Friends", size=24, weight=ft.FontWeight.BOLD),
                                    ft.Text(
                                        getattr(self.current_user, "email", "") or "",
                                        size=11,
                                        color=self.secondary_text,
                                    ),
                                ],
                            ),
                            ft.Row(
                                spacing=0,
                                controls=[
                                    self.loading,
                                    ft.IconButton(
                                        icon=ft.Icons.REFRESH,
                                        tooltip="Refresh",
                                        on_click=lambda _: self.show_tab(self.current_tab),
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ft.Container(
                        bgcolor=self.surface,
                        border_radius=9,
                        padding=3,
                        content=ft.Row(
                            controls=tab_buttons,
                            spacing=2,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                    ),
                    self.content_area,
                ],
            ),
        )

    def show_tab(self, index: int) -> None:
        self.current_tab = index
        self.selected_friend = None

        if index == 0:
            self.content_area.content = self._friends_view()
            self.load_friends()
        elif index == 1:
            self.content_area.content = self._requests_view()
            self.load_requests()
        else:
            self.content_area.content = self._search_view()

        self.page.update()

    # ------------------------------------------------------------------
    # Search and friend requests
    # ------------------------------------------------------------------

    def _search_view(self) -> ft.Control:
        return ft.Column(
            expand=True,
            spacing=12,
            controls=[
                ft.Text("Find people", size=18, weight=ft.FontWeight.BOLD),
                ft.Row(
                    controls=[
                        self.search_field,
                        ft.FilledButton(
                            "Search",
                            icon=ft.Icons.SEARCH,
                            bgcolor=self.accent,
                            color="#FFFFFF",
                            on_click=self.search_users,
                        ),
                    ]
                ),
                self.search_results,
            ],
        )

    def search_users(self, _: ft.ControlEvent) -> None:
        query = (self.search_field.value or "").strip()
        self.search_results.controls.clear()

        if len(query) < 3:
            self.search_results.controls.append(
                ft.Text("Enter at least 3 characters.", color=self.secondary_text)
            )
            self.page.update()
            return

        self._set_loading(True)
        try:
            response = self.supabase.rpc(
                "search_profiles_by_email",
                {"search_text": query},
            ).execute()
            rows = response.data or []

            if not rows:
                self.search_results.controls.append(
                    ft.Text("No users found.", color=self.secondary_text)
                )
            else:
                for profile in rows:
                    self.search_results.controls.append(self._search_result_card(profile))
        except Exception as error:
            self._show_error(f"Could not search for users: {error}")
        finally:
            self._set_loading(False)
            self.page.update()

    def _search_result_card(self, profile: dict[str, Any]) -> ft.Control:
        return ft.Container(
            bgcolor=self.surface_light,
            border=ft.Border.all(1, self.border),
            border_radius=12,
            padding=12,
            content=ft.Row(
                controls=[
                    self._avatar(profile),
                    ft.Column(
                        expand=True,
                        spacing=2,
                        controls=[
                            ft.Text(self._profile_name(profile), weight=ft.FontWeight.BOLD),
                            ft.Text(profile.get("email") or "", color=self.secondary_text, size=12),
                        ],
                    ),
                    ft.FilledButton(
                        "Add",
                        icon=ft.Icons.PERSON_ADD,
                        bgcolor=self.accent,
                        color="#FFFFFF",
                        on_click=lambda _, target=profile: self.send_friend_request(target),
                    ),
                ],
            ),
        )

    def send_friend_request(self, profile: dict[str, Any]) -> None:
        try:
            result = self.supabase.rpc(
                "send_friend_request",
                {"target_email": profile.get("email")},
            ).execute()
            message = (result.data or {}).get("message") if isinstance(result.data, dict) else None
            self._show_message("Friend request", message or "Friend request sent.")
        except Exception as error:
            self._show_error(f"Could not send friend request: {error}")

    # ------------------------------------------------------------------
    # Incoming requests
    # ------------------------------------------------------------------

    def _requests_view(self) -> ft.Control:
        return ft.Column(
            expand=True,
            spacing=12,
            controls=[
                ft.Text("Incoming requests", size=18, weight=ft.FontWeight.BOLD),
                self.requests_column,
            ],
        )

    def load_requests(self) -> None:
        self.requests_column.controls.clear()
        self._set_loading(True)
        try:
            response = self.supabase.rpc("get_incoming_friend_requests").execute()
            requests = response.data or []
            if not requests:
                self.requests_column.controls.append(
                    self._empty_state(
                        ft.Icons.MARK_EMAIL_READ_OUTLINED,
                        "No pending requests",
                        "New friend requests will appear here.",
                    )
                )
            else:
                for request in requests:
                    self.requests_column.controls.append(self._request_card(request))
        except Exception as error:
            self._show_error(f"Could not load friend requests: {error}")
        finally:
            self._set_loading(False)
            self.page.update()

    def _request_card(self, request: dict[str, Any]) -> ft.Control:
        profile = {
            "id": request.get("sender_id"),
            "email": request.get("sender_email"),
            "display_name": request.get("sender_display_name"),
            "avatar_url": request.get("sender_avatar_url"),
        }
        return ft.Container(
            bgcolor=self.surface_light,
            border=ft.Border.all(1, self.border),
            border_radius=12,
            padding=12,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        controls=[
                            self._avatar(profile),
                            ft.Column(
                                expand=True,
                                spacing=2,
                                controls=[
                                    ft.Text(self._profile_name(profile), weight=ft.FontWeight.BOLD),
                                    ft.Text(profile.get("email") or "", color=self.secondary_text, size=12),
                                ],
                            ),
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ft.FilledButton(
                                "Accept",
                                icon=ft.Icons.CHECK,
                                bgcolor=self.accent,
                                color="#FFFFFF",
                                on_click=lambda _, request_id=request.get("request_id"): self.respond_request(request_id, True),
                            ),
                            ft.OutlinedButton(
                                "Decline",
                                icon=ft.Icons.CLOSE,
                                on_click=lambda _, request_id=request.get("request_id"): self.respond_request(request_id, False),
                            ),
                        ]
                    ),
                ],
            ),
        )

    def respond_request(self, request_id: str, accept: bool) -> None:
        try:
            self.supabase.rpc(
                "respond_friend_request",
                {"request_uuid": request_id, "accept_request": accept},
            ).execute()
            self.load_requests()
            self._show_message(
                "Request updated",
                "Friend request accepted." if accept else "Friend request declined.",
            )
        except Exception as error:
            self._show_error(f"Could not update the request: {error}")

    # ------------------------------------------------------------------
    # Friends list
    # ------------------------------------------------------------------

    def _friends_view(self) -> ft.Control:
        return ft.Column(
            expand=True,
            spacing=12,
            controls=[
                ft.Text("Your friends", size=18, weight=ft.FontWeight.BOLD),
                self.friends_column,
            ],
        )

    def load_friends(self) -> None:
        self.friends_column.controls.clear()
        self._set_loading(True)
        try:
            response = self.supabase.rpc("get_my_friends").execute()
            friends = response.data or []
            if not friends:
                self.friends_column.controls.append(
                    self._empty_state(
                        ft.Icons.GROUP_OFF_OUTLINED,
                        "No friends yet",
                        "Search for someone by email and send a request.",
                    )
                )
            else:
                for friend in friends:
                    self.friends_column.controls.append(self._friend_card(friend))
        except Exception as error:
            self._show_error(f"Could not load friends: {error}")
        finally:
            self._set_loading(False)
            self.page.update()

    def _friend_card(self, friend: dict[str, Any]) -> ft.Control:
        status = self._status_text(friend)
        status_icon = ft.Icons.CIRCLE
        return ft.Container(
            bgcolor=self.surface_light,
            border=ft.Border.all(1, self.border),
            border_radius=12,
            padding=12,
            content=ft.Row(
                controls=[
                    self._avatar(friend),
                    ft.Column(
                        expand=True,
                        spacing=2,
                        controls=[
                            ft.Text(self._profile_name(friend), weight=ft.FontWeight.BOLD),
                            ft.Text(friend.get("email") or "", color=self.secondary_text, size=12),
                            ft.Row(
                                tight=True,
                                spacing=5,
                                controls=[
                                    ft.Icon(status_icon, size=9, color=self.accent if status == "Online" else self.secondary_text),
                                    ft.Text(status, size=11, color=self.secondary_text),
                                ],
                            ),
                        ],
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CHAT_BUBBLE_OUTLINE,
                        tooltip="Open chat",
                        on_click=lambda _, selected=friend: self.open_chat(selected),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.PERSON_REMOVE_OUTLINED,
                        tooltip="Remove friend",
                        on_click=lambda _, selected=friend: self.confirm_remove_friend(selected),
                    ),
                ],
            ),
        )

    def confirm_remove_friend(self, friend: dict[str, Any]) -> None:
        self.page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("Remove friend?"),
                content=ft.Text(f"Remove {self._profile_name(friend)} from your friends list?"),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda _: self.page.pop_dialog()),
                    ft.FilledButton(
                        "Remove",
                        bgcolor=self.accent,
                        color="#FFFFFF",
                        on_click=lambda _: self.remove_friend(friend),
                    ),
                ],
            )
        )

    def remove_friend(self, friend: dict[str, Any]) -> None:
        self.page.pop_dialog()
        try:
            self.supabase.rpc(
                "remove_friend",
                {"friend_user_id": friend.get("friend_id")},
            ).execute()
            self.load_friends()
        except Exception as error:
            self._show_error(f"Could not remove friend: {error}")

    # ------------------------------------------------------------------
    # Chat
    # ------------------------------------------------------------------

    def open_chat(self, friend: dict[str, Any]) -> None:
        self.selected_friend = friend
        self.content_area.content = self._chat_view(friend)
        self.page.update()
        self.load_messages()
        self.page.run_task(self._subscribe_to_messages)

    def _chat_view(self, friend: dict[str, Any]) -> ft.Control:
        return ft.Column(
            expand=True,
            spacing=10,
            controls=[
                ft.Container(
                    bgcolor=self.surface,
                    border_radius=12,
                    padding=10,
                    content=ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                on_click=lambda _: self.show_tab(0),
                            ),
                            self._avatar(friend, 40),
                            ft.Column(
                                expand=True,
                                spacing=1,
                                controls=[
                                    ft.Text(self._profile_name(friend), weight=ft.FontWeight.BOLD),
                                    ft.Text(self._status_text(friend), size=11, color=self.secondary_text),
                                ],
                            ),
                        ]
                    ),
                ),
                ft.Container(
                    expand=True,
                    bgcolor=self.surface,
                    border_radius=12,
                    content=self.messages_list,
                ),
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.END,
                    controls=[
                        self.message_field,
                        ft.IconButton(
                            icon=ft.Icons.SEND,
                            bgcolor=self.accent,
                            icon_color="#FFFFFF",
                            tooltip="Send",
                            on_click=self.send_message,
                        ),
                    ],
                ),
            ],
        )

    def load_messages(self) -> None:
        friend = self.selected_friend
        user = self.current_user
        if friend is None or user is None:
            return

        try:
            response = self.supabase.rpc(
                "get_conversation",
                {"other_user_id": friend.get("friend_id")},
            ).execute()
            self.messages = response.data or []
            self._render_messages()
        except Exception as error:
            self._show_error(f"Could not load messages: {error}")

    def _render_messages(self) -> None:
        user = self.current_user
        self.messages_list.controls.clear()

        if not self.messages:
            self.messages_list.controls.append(
                ft.Container(
                    padding=30,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text(
                        "No messages yet. Say hello!",
                        color=self.secondary_text,
                        text_align=ft.TextAlign.CENTER,
                    ),
                )
            )
        else:
            for message in self.messages:
                mine = user is not None and message.get("sender_id") == user.id
                self.messages_list.controls.append(self._message_bubble(message, mine))

        self.page.update()

    def _message_bubble(self, message: dict[str, Any], mine: bool) -> ft.Control:
        created = str(message.get("created_at") or "")
        try:
            parsed = datetime.fromisoformat(created.replace("Z", "+00:00"))
            timestamp = parsed.astimezone().strftime("%H:%M")
        except ValueError:
            timestamp = ""

        return ft.Row(
            alignment=ft.MainAxisAlignment.END if mine else ft.MainAxisAlignment.START,
            controls=[
                ft.Container(
                    width=270,
                    bgcolor=self.accent if mine else self.surface_light,
                    border_radius=ft.BorderRadius.only(
                        top_left=14,
                        top_right=14,
                        bottom_left=14 if mine else 3,
                        bottom_right=3 if mine else 14,
                    ),
                    padding=12,
                    content=ft.Column(
                        spacing=5,
                        controls=[
                            ft.Text(
                                message.get("content") or "",
                                color="#FFFFFF" if mine else self.primary_text,
                                selectable=True,
                            ),
                            ft.Text(
                                timestamp,
                                size=10,
                                color="#DDEDEA" if mine else self.secondary_text,
                                text_align=ft.TextAlign.RIGHT,
                            ),
                        ],
                    ),
                )
            ],
        )

    def send_message(self, _: ft.ControlEvent) -> None:
        user = self.current_user
        friend = self.selected_friend
        content = (self.message_field.value or "").strip()

        if user is None or friend is None:
            return
        if not content:
            return
        if len(content) > 2000:
            self._show_error("Messages must be 2,000 characters or fewer.")
            return

        try:
            (
                self.supabase.table("messages")
                .insert(
                    {
                        "sender_id": user.id,
                        "receiver_id": friend.get("friend_id"),
                        "content": content,
                    }
                )
                .execute()
            )
            self.message_field.value = ""
            self.page.update()
            # Realtime normally refreshes this immediately; this fallback keeps
            # the demo responsive if Realtime is temporarily unavailable.
            self.load_messages()
        except Exception as error:
            self._show_error(f"Could not send the message: {error}")

    async def _subscribe_to_messages(self) -> None:
        await self._remove_message_channel()
        user = self.current_user
        friend = self.selected_friend
        if user is None or friend is None:
            return

        channel_name = f"messages-{user.id}-{friend.get('friend_id')}"

        def handle_change(_: Any) -> None:
            if self.selected_friend is not None:
                self.load_messages()

        try:
            self.message_channel = (
                self.supabase.channel(channel_name)
                .on_postgres_changes(
                    "INSERT",
                    schema="public",
                    table="messages",
                    callback=handle_change,
                )
            )
            await self.message_channel.subscribe()
        except Exception as error:
            # Chat still works through the immediate fallback reload after send.
            print(f"Realtime subscription warning: {error}")

    async def _remove_message_channel(self) -> None:
        if self.message_channel is None:
            return
        try:
            await self.supabase.remove_channel(self.message_channel)
        except Exception:
            pass
        finally:
            self.message_channel = None

    # ------------------------------------------------------------------
    # Miscellaneous
    # ------------------------------------------------------------------

    def _touch_last_seen(self) -> None:
        user = self.current_user
        if user is None:
            return
        try:
            (
                self.supabase.table("profiles")
                .update({"last_seen_at": datetime.now(timezone.utc).isoformat()})
                .eq("id", user.id)
                .execute()
            )
        except Exception:
            pass

    def _empty_state(self, icon: str, title: str, message: str) -> ft.Control:
        return ft.Container(
            expand=True,
            padding=30,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Icon(icon, size=54, color=self.secondary_text),
                    ft.Text(title, size=19, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    ft.Text(message, color=self.secondary_text, text_align=ft.TextAlign.CENTER),
                ],
            ),
        )
