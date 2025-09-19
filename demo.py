"""Comprehensive wxauto4 demo script.

This script demonstrates how to drive the public interfaces exposed by
:mod:`wxauto4`.  It keeps the implementation defensive so that it can be run on
real WeChat instances without crashing when certain UI elements are missing.

Usage examples
--------------

.. code-block:: bash

    # Send a message and a file to ``Friend`` and then exit
    python demo.py --target Friend --message "你好" --files path/to/file.png

    # Start message listening and keep the script alive for 60 seconds
    python demo.py --listen Friend --listen-duration 60

    # Inspect recent moments and like a friend's post
    python demo.py --moments --like Friend --comment Friend --comment-text "👍"

Most command-line options are optional.  You can also run the script without any
arguments to simply print basic information about the logged-in account.
"""

from __future__ import annotations

import argparse
import signal
import sys
import textwrap
import time
from pathlib import Path
from typing import Iterable, List, Optional

from wxauto4 import Moment, WeChat, WxParam, WxResponse, wxlog


def _format_files(files: Iterable[str]) -> List[str]:
    """Expand and validate file paths.

    Args:
        files: Iterable of file path strings provided by the user.

    Returns:
        A list of absolute paths that exist on disk.  Missing files trigger a
        warning on stdout but do not abort the script.
    """

    resolved: List[str] = []
    for raw in files:
        path = Path(raw).expanduser()
        try:
            path = path.resolve(strict=True)
        except FileNotFoundError:
            print(f"[警告] 找不到文件: {path}")
            continue
        resolved.append(str(path))
    return resolved


def _print_response(title: str, response: WxResponse) -> None:
    """Pretty-print :class:`WxResponse` objects with an action title."""

    status = "成功" if response.is_success else "失败"
    message = response.get("message")
    extra = f" - {message}" if message else ""
    print(f"[{status}] {title}{extra}")
    if response.get("data"):
        print(textwrap.indent(str(response["data"]), prefix="    数据: "))


class WeChatDemo:
    """Aggregate high-level demonstrations of wxauto4 features."""

    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        if args.language:
            WxParam.LANGUAGE = args.language
        listener = args.start_listener or bool(args.listen)
        self.wx = WeChat(start_listener=listener, debug=args.debug)
        wxlog.debug("WeChat demo initialized")

    # ------------------------------------------------------------------
    # Basic information
    # ------------------------------------------------------------------
    def show_basic_info(self) -> None:
        print("=" * 60)
        print("当前账号信息")
        print("=" * 60)
        print(f"昵称: {self.wx.nickname}")
        try:
            print(f"微信安装路径: {self.wx.path}")
        except Exception:
            print("微信安装路径: 未知 (需要在真实环境中运行)")
        try:
            print(f"微信数据目录: {self.wx.dir}")
        except Exception:
            print("微信数据目录: 未知 (需要在真实环境中运行)")

    # ------------------------------------------------------------------
    # Chat related features
    # ------------------------------------------------------------------
    def send_message(self) -> None:
        args = self.args
        if not args.message:
            return

        target = args.target
        if not target:
            print("[提示] 未指定 target, 将向当前聊天窗口发送消息")
        response = self.wx.SendMsg(
            msg=args.message,
            who=target,
            clear=not args.keep_editor,
            at=args.at,
            exact=args.exact,
        )
        _print_response("发送消息", response)

    def send_files(self) -> None:
        if not self.args.files:
            return
        files = _format_files(self.args.files)
        if not files:
            print("[提示] 没有可发送的文件")
            return
        response = self.wx.SendFiles(files if len(files) > 1 else files[0], who=self.args.target, exact=self.args.exact)
        _print_response("发送文件", response)

    def switch_chat(self) -> None:
        if not self.args.target:
            return
        result = self.wx.ChatWith(self.args.target, exact=self.args.exact, force=self.args.force, force_wait=self.args.force_wait)
        if isinstance(result, WxResponse):
            _print_response("切换聊天窗口", result)
        else:
            nickname = result or self.args.target
            print(f"[成功] 切换到聊天窗口: {nickname}")

    def list_sessions(self) -> None:
        if not self.args.list_sessions:
            return
        sessions = self.wx.GetSession()
        print("当前会话列表:")
        for session in sessions:
            print(f" - {session.name} (未读 {session.unread_count})")

    def dump_messages(self) -> None:
        if not self.args.show_messages:
            return
        messages = self.wx.GetAllMessage()
        print(f"当前聊天窗口共 {len(messages)} 条消息")
        for msg in messages:
            print(f"[{msg.attr}] {msg.sender}: {msg.content}")

    # ------------------------------------------------------------------
    # Listener related features
    # ------------------------------------------------------------------
    def _listener_callback(self, msg, chat):  # type: ignore[no-untyped-def]
        """Default message listener callback printing and optional reply."""

        print(f"[监听] 来自 {chat}: {msg.content}")
        if self.args.auto_reply:
            chat.SendMsg(self.args.auto_reply, clear=True)

    def setup_listener(self) -> None:
        if not self.args.listen:
            return
        targets = self.args.listen
        if isinstance(targets, str):
            targets = [targets]
        for target in targets:
            response = self.wx.AddListenChat(target, self._listener_callback)
            if isinstance(response, WxResponse) and not response:
                _print_response(f"监听 {target}", response)
            else:
                print(f"[成功] 已对 {target} 开始监听消息")

    # ------------------------------------------------------------------
    # Sub window helpers
    # ------------------------------------------------------------------
    def handle_subwindows(self) -> None:
        if not self.args.subwindow:
            return
        nickname = self.args.subwindow
        chat = self.wx.GetSubWindow(nickname)
        if not chat:
            print(f"[提示] 未找到 {nickname} 的子窗口，可尝试先调用 --listen {nickname}")
            return
        response = chat.SendMsg(self.args.message or "这是子窗口示例消息", clear=True)
        _print_response(f"通过子窗口向 {nickname} 发送消息", response)

    def list_subwindows(self) -> None:
        if not self.args.list_subwindows:
            return
        subwins = self.wx.GetAllSubWindow()
        if not subwins:
            print("当前没有独立的子窗口")
            return
        print("子窗口列表:")
        for sub in subwins:
            print(f" - {sub.who}")

    # ------------------------------------------------------------------
    # Navigation helpers
    # ------------------------------------------------------------------
    def navigate_tabs(self) -> None:
        if not self.args.navigate:
            return
        print("切换到聊天页...")
        self.wx.SwitchToChat()
        time.sleep(0.5)
        print("切换到联系人页...")
        self.wx.SwitchToContact()
        time.sleep(0.5)
        print("切换到收藏页...")
        self.wx.SwitchToFavorites()
        time.sleep(0.5)
        print("切换到文件传输页...")
        self.wx.SwitchToFiles()
        time.sleep(0.5)
        print("切换到朋友圈...")
        self.wx.SwitchToMoments()
        time.sleep(0.5)
        print("切换到搜一搜...")
        self.wx.SwitchToBrowser()

    # ------------------------------------------------------------------
    # Moments
    # ------------------------------------------------------------------
    def show_moments(self) -> None:
        if not self.args.moments:
            return
        moment: Moment = self.wx.Moment
        items = moment.GetMoments(refresh=self.args.refresh_moments)
        if not items:
            print("未读取到朋友圈动态")
            return
        print(f"读取到 {len(items)} 条朋友圈动态")
        for idx, item in enumerate(items, 1):
            print("-" * 40)
            print(f"[{idx}] 发布者: {item.publisher}")
            print(f"    时间: {item.timestamp}")
            if item.text:
                print("    内容:")
                print(textwrap.indent(item.text, prefix="        "))
            if likes := item.like_users:
                print(f"    点赞: {', '.join(likes)}")
            if comments := item.comment_list:
                print("    评论:")
                for comment in comments:
                    reply = f" 回复 {comment.reply_to}" if comment.reply_to else ""
                    print(f"        {comment.author}{reply}: {comment.content}")

        if self.args.like:
            item = moment.FindMomentByPublisher(self.args.like, refresh=False)
            if not item:
                print(f"[提示] 未找到 {self.args.like} 的朋友圈动态")
            else:
                response = moment.Like(item, cancel=self.args.cancel_like)
                _print_response("朋友圈点赞", response)
        if self.args.comment:
            if not self.args.comment_text:
                print("[提示] --comment 需要配合 --comment-text 使用")
            else:
                item = moment.FindMomentByPublisher(self.args.comment, refresh=False)
                if not item:
                    print(f"[提示] 未找到 {self.args.comment} 的朋友圈动态")
                else:
                    response = moment.Comment(item, self.args.comment_text, reply_to=self.args.reply_to)
                    _print_response("朋友圈评论", response)

    # ------------------------------------------------------------------
    def wait_for_listener(self) -> None:
        duration = self.args.listen_duration
        if not duration:
            return
        print(f"监听中，持续 {duration} 秒，按 Ctrl+C 可提前结束")
        try:
            end_time = time.time() + duration
            while time.time() < end_time:
                time.sleep(1)
        except KeyboardInterrupt:
            print("捕获到 Ctrl+C, 准备退出...")

    def shutdown(self) -> None:
        if getattr(self.wx, "_listener_is_listening", False):
            self.wx.StopListening()
        print("演示结束")


# ----------------------------------------------------------------------
# CLI parsing
# ----------------------------------------------------------------------

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="wxauto4 功能演示脚本")
    parser.add_argument("--target", help="聊天对象昵称", default=None)
    parser.add_argument("--message", help="要发送的消息内容", default=None)
    parser.add_argument("--keep-editor", help="发送消息后保留输入框内容", action="store_true")
    parser.add_argument("--files", nargs="*", help="要发送的文件路径", default=None)
    parser.add_argument("--exact", help="聊天搜索使用精确匹配", action="store_true")
    parser.add_argument("--force", help="强制切换聊天窗口", action="store_true")
    parser.add_argument("--force-wait", type=float, default=0.5, help="强制切换等待时间")
    parser.add_argument("--list-sessions", action="store_true", help="打印会话列表")
    parser.add_argument("--show-messages", action="store_true", help="打印当前聊天窗口消息")
    parser.add_argument("--listen", nargs="*", help="监听聊天对象，支持多个")
    parser.add_argument("--listen-duration", type=int, default=0, help="监听持续时间（秒）")
    parser.add_argument("--auto-reply", help="监听时自动回复内容")
    parser.add_argument("--subwindow", help="对子窗口发送消息")
    parser.add_argument("--list-subwindows", action="store_true", help="列出所有子窗口")
    parser.add_argument("--navigate", action="store_true", help="演示侧边栏导航切换")
    parser.add_argument("--moments", action="store_true", help="读取朋友圈动态")
    parser.add_argument("--refresh-moments", action="store_true", help="强制刷新朋友圈控件缓存")
    parser.add_argument("--like", help="给指定好友的朋友圈点赞")
    parser.add_argument("--cancel-like", action="store_true", help="取消点赞")
    parser.add_argument("--comment", help="给指定好友朋友圈发表评论")
    parser.add_argument("--comment-text", help="朋友圈评论内容")
    parser.add_argument("--reply-to", help="朋友圈回复对象（用于回复评论）")
    parser.add_argument("--language", choices=["cn", "cn_t", "en"], help="设置微信语言")
    parser.add_argument("--start-listener", action="store_true", help="启动时立即开启监听线程")
    parser.add_argument("--at", nargs="*", help="发送消息时 @ 的用户")
    parser.add_argument("--debug", action="store_true", help="启用调试日志")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    demo = WeChatDemo(args)

    def _signal_handler(signum, frame):  # type: ignore[unused-argument]
        print("收到退出信号，正在停止...")
        demo.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    try:
        demo.show_basic_info()
        demo.switch_chat()
        demo.list_sessions()
        demo.list_subwindows()
        demo.send_message()
        demo.send_files()
        demo.dump_messages()
        demo.navigate_tabs()
        demo.setup_listener()
        demo.handle_subwindows()
        demo.show_moments()
        demo.wait_for_listener()
    finally:
        demo.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
