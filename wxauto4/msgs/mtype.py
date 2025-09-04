from .base import (
    BaseMessage, 
    HumanMessage,
)
from wxauto4 import uia
from wxauto4.param import (
    WxParam, 
    WxResponse, 
    PROJECT_NAME
)

from typing import (
    Dict, 
    List, 
    Any,
    TYPE_CHECKING
)
import re
if TYPE_CHECKING:
    from wxauto4.ui.chatbox import ChatBox


class TextMessage(BaseMessage):
    type = 'text'

    def __init__(
            self, 
            control: uia.Control, 
            parent: "ChatBox",
            additonal_attr: Dict[str, Any]={}
        ):
        super().__init__(control, parent, additonal_attr)

class QuoteMessage(BaseMessage):
    type = 'quote'
    repattern = r"^(.*?) \n引用 (.*?) 的消息 : (.*?)$"

    def __init__(
            self, 
            control: uia.Control, 
            parent: "ChatBox",
            additonal_attr: Dict[str, Any]={}
        ):
        super().__init__(control, parent, additonal_attr)
        self.content, self.quote_nickname, self.quote_content = \
            re.findall(self.repattern, self.content, re.DOTALL)[0]
        
class VoiceMessage(BaseMessage):
    type = 'voice'

    def __init__(
            self, 
            control: uia.Control, 
            parent: "ChatBox",
            additonal_attr: Dict[str, Any]={}
        ):
        super().__init__(control, parent, additonal_attr)

class ImageMessage(BaseMessage):
    type = 'image'
    
    def __init__(
            self, 
            control: uia.Control, 
            parent: "ChatBox",
            additonal_attr: Dict[str, Any]={}
        ):
        super().__init__(control, parent, additonal_attr)

class VideoMessage(BaseMessage):
    type = 'video'
    repattern = r'视频(\d+):(\d+)'
    
    def __init__(
            self, 
            control: uia.Control, 
            parent: "ChatBox",
            additonal_attr: Dict[str, Any]={}
        ):
        super().__init__(control, parent, additonal_attr)

class FileMessage(BaseMessage):
    type = 'file'
    repattern = r"^文件\n([^\n]+)\n(\d+(\.\d+)?)(B|KB|MB|GB|TB)\n微信电脑版$"
    
    def __init__(
            self, 
            control: uia.Control, 
            parent: "ChatBox",
            additonal_attr: Dict[str, Any]={}
        ):
        super().__init__(control, parent, additonal_attr)

class OtherMessage(BaseMessage):
    type = 'other'
    
    def __init__(
            self, 
            control: uia.Control, 
            parent: "ChatBox",
            additonal_attr: Dict[str, Any]={}
        ):
        super().__init__(control, parent, additonal_attr)