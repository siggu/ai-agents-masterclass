from pydantic import BaseModel, Field
from typing import List


class SceneOutput(BaseModel):
    id: int = Field(description="장면의 고유 식별자")
    narration: str = Field(description="장면의 나레이션 텍스트")
    visual_description: str = Field(description="장면의 시각적 설명")
    embedded_text: str = Field(description="삽입 텍스트 오버레이 (case/style 자유롭게)")
    embedded_text_location: str = Field(
        description="삽입 텍스트의 위치 (예: 'top center', 'bottom left', 'middle right', 'center' 등)"
    )
    duration: int = Field(description="장면의 지속 시간")


class ContentPlanOutput(BaseModel):
    topic: str = Field(description="콘텐츠 주제")
    total_duration: int = Field(description="총 재생 시간 (초 단위, 반드시 20 이하)")
    scenes: List[SceneOutput] = Field(
        description="장면 목록 (각 장면은 고유한 ID, 나레이션, 시각적 설명, 삽입 텍스트, 텍스트 위치, 지속 시간을 포함)"
    )
