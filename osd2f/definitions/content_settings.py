from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, EmailStr


class FileSetting(BaseModel):
    in_key: Optional[str]
    accepted_fields: List[str]
    anonymizers: Optional[List[Dict[str, str]]]
    headlines: Optional[List[str]]
    html_css_element: Optional[str]
    html_css_fields: Optional[List[Dict[str, str]]]
    csv_skip_n_lines_at_top: Optional[int]


class UploadSettings(BaseModel):
    files: Dict[str, FileSetting]


class BlockTypeEnum(str, Enum):
    jumbotron = "jumbotron"
    twoblockrow = "two_block_row"


class ImagePositionEnum(str, Enum):
    right = "right"
    left = "left"


class ContentButton(BaseModel):
    name: str
    link: str
    label: str


class PageTypeEnum(str, Enum):
    home = "home"
    privacy = "privacy"
    donate = "donate"


class CirclesRowCircle(BaseModel):
    image: str
    title: Optional[str]
    subtitle: Optional[str]


class ContentBlock(BaseModel):
    type: BlockTypeEnum
    id: str
    title: Optional[str]
    lines: List[str]
    buttons: List[ContentButton]
    image: Optional[str]
    image_pos: Optional[ImagePositionEnum]
    circles_row: Optional[List[CirclesRowCircle]]

    class Config:
        use_enum_values = True


class ContentPage(BaseModel):
    active: bool
    name: str
    blocks: List[ContentBlock]


class UploadBox(BaseModel):
    header: Optional[str]
    explanation: List[str]


class PreviewComponent(BaseModel):
    entries_in_file_text: str
    title: str
    explanation: List[str]
    previous_file_button: str
    next_file_button: str
    remove_rows_button: str
    search_prompt: str
    search_box_placeholder: str
    file_text: Optional[str]
    entries_per_page_text: Optional[str]
    today_text: Optional[str]
    close_text: Optional[str]
    startdate_text: Optional[str]
    enddate_text: Optional[str]
    no_matches_text: Optional[str]
    show_all_text: Optional[str]


class ConsentPopup(BaseModel):
    title: str
    lead: str
    points: Optional[List[str]]
    end_text: str
    decline_button: str
    accept_button: str


class UploadPage(BaseModel):
    blocks: List[ContentBlock]
    upload_box: UploadBox
    thanks_text: str
    file_indicator_text: str
    processing_text: str
    empty_selection: str
    donate_button: str
    inspect_button: str
    preview_component: PreviewComponent
    consent_popup: ConsentPopup


class ContentSettings(BaseModel):
    project_title: str
    contact_us: EmailStr
    static_pages: Dict[PageTypeEnum, ContentPage]
    upload_page: UploadPage
    survey_base_url: Optional[str]
    survey_js_callback: Optional[str]

    class Config:
        use_enum_values = True
