import flet as ft
from datetime import datetime, timedelta


def main(page: ft.Page):
    page.title = "脚本管理器"
    page.window_width = 800
    page.window_height = 600
    page.theme_mode = ft.ThemeMode.DARK

    expire_date = datetime.now() + timedelta(days=30)

    scripts = [
        "甜甜香气刷怪",
        "（未来）自动捕捉",
        "（未来）自动孵蛋",
    ]

    selected_script = ft.Text("当前未选择脚本")

    username = ft.TextField(label="用户名")
    delay = ft.TextField(label="操作延迟(ms)", value="300")

    key_input = ft.TextField(label="授权密钥", password=True)
    expire_text = ft.Text(
        f"授权到期时间：{expire_date.strftime('%Y-%m-%d')}"
    )

    script_dropdown = ft.Dropdown(
        label="选择脚本（一次只能运行一个）",
        options=[ft.dropdown.Option(s) for s in scripts],
    )

    def on_script_change(e):
        selected_script.value = f"已选择：{e.control.value}"
        page.update()

    script_dropdown.on_change = on_script_change

    status_text = ft.Text("状态：未运行")

    def start_script(e):
        if not script_dropdown.value:
            status_text.value = "⚠️ 请先选择脚本"
        else:
            status_text.value = f"▶ 正在运行：{script_dropdown.value}"
        page.update()

    start_btn = ft.ElevatedButton(
        text="启动脚本",
        icon=ft.icons.PLAY_ARROW,
        on_click=start_script
    )

    page.add(
        ft.Column([
            ft.Text("⚙️ 用户设置", size=18, weight="bold"),
            username,
            delay,

            ft.Divider(),

            ft.Text("🔑 授权信息", size=18, weight="bold"),
            key_input,
            expire_text,

            ft.Divider(),

            ft.Text("📜 脚本控制", size=18, weight="bold"),
            script_dropdown,
            selected_script,

            ft.Divider(),

            start_btn,
            status_text
        ], spacing=15)
    )


ft.app(target=main)
