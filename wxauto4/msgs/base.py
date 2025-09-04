from wxauto4 import uia
from wxauto4.ui.component import (
    Menu,
    SelectContactWnd
)
from wxauto4.utils import uilock
from wxauto4.param import WxParam, WxResponse, PROJECT_NAME
from abc import ABC, abstractmethod
from typing import (
    Dict, 
    List, 
    Union,
    Any,
    TYPE_CHECKING
)
from hashlib import md5

if TYPE_CHECKING:
    from wxauto4.ui.chatbox import ChatBox

def truncate_string(s: str, n: int=8) -> str:
    s = s.replace('\n', '').strip()
    return s if len(s) <= n else s[:n] + '...'

class Message:
    ...

class BaseMessage(Message, ABC):
    type: str = 'base'
    attr: str = 'base'
    control: uia.Control

    def __init__(
            self, 
            control: uia.Control, 
            parent: "ChatBox",
            additonal_attr: Dict[str, Any]={}
        ):
        self.parent = parent
        self.control = control
        self.direction = additonal_attr.get('direction', None)
        self.distince = additonal_attr.get('direction_distence', None)
        self.root = parent.root
        self.id = self.control.runtimeid
        self.content = self.control.Name
        rect = self.control.BoundingRectangle
        self.hash_text = f'({rect.height()},{rect.width()}){self.content}'
        self.hash = md5(self.hash_text.encode()).hexdigest()

    def __repr__(self):
        cls_name = self.__class__.__name__
        content = truncate_string(self.content)
        return f"<{PROJECT_NAME} - {cls_name}({content}) at {hex(id(self))}>"
    
    def roll_into_view(self):
        if not self.exists():
            return WxResponse.failure('消息目标控件不存在，无法滚动至显示窗口')
        if uia.RollIntoView(
            self.parent.msgbox, 
            self.control
        ) == 'not exist':
            return WxResponse.failure('消息目标控件不存在，无法滚动至显示窗口')
        return WxResponse.success('成功')
    
    def exists(self):
        if self.control.Exists(0) and self.control.BoundingRectangle.height() > 0:
            return True
        return False
    


class HumanMessage(BaseMessage, ABC):
    attr = 'human'

    def __init__(
            self, 
            control: uia.Control, 
            parent: "ChatBox",
            additonal_attr: Dict[str, Any]={}
        ):
        super().__init__(control, parent, additonal_attr)

    @abstractmethod
    def _click(self, x, y, right=False):...

    @abstractmethod
    def _bias(self):...

    def click(self):
        self._click(right=False, x=self._bias*2, y=WxParam.DEFAULT_MESSAGE_YBIAS)

    def right_click(self):
        self._click(right=True, x=self._bias, y=WxParam.DEFAULT_MESSAGE_YBIAS)

    @uilock
    def select_option(self, option: str, timeout=2) -> WxResponse:
        if not self.exists():
            return WxResponse.failure('消息对象已失效')
        self._click(right=True, x=self._bias*2, y=WxParam.DEFAULT_MESSAGE_YBIAS)
        if menu := Menu(self, timeout):
            return menu.select(option)
        else:
            return WxResponse.failure('操作失败')
    
    @uilock
    def forward(
        self, 
        targets: Union[List[str], str], 
        timeout: int = 3,
        interval: float = 0.1
    ) -> WxResponse:
        """转发消息

        Args:
            targets (Union[List[str], str]): 目标用户列表
            timeout (int, optional): 超时时间，单位为秒，若为None则不启用超时设置
            interval (float): 选择联系人时间间隔

        Returns:
            WxResponse: 调用结果
        """
        if not self.exists():
            return WxResponse.failure('消息对象已失效')
        if not self.select_option('转发...', timeout=timeout):
            return WxResponse.failure('当前消息无法转发')
        
        select_wnd = SelectContactWnd(self)
        return select_wnd.send(targets, interval=interval)
    
    @uilock
    def quote(
            self, text: str, 
            at: Union[List[str], str] = None, 
            timeout: int = 3
        ) -> WxResponse:
        """引用消息
        
        Args:
            text (str): 引用内容
            at (List[str], optional): @用户列表
            timeout (int, optional): 超时时间，单位为秒，若为None则不启用超时设置

        Returns:
            WxResponse: 调用结果
        """
        if not self.exists():
            return WxResponse.failure('消息对象已失效')
        if not self.select_option('引用', timeout=timeout):
            return WxResponse.failure('当前消息无法引用')
        
        if at:
            self.parent.input_at(at)

        return self.parent.send_text(text)
