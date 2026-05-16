from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ImageMediaType = Literal["image/jpeg", "image/png", "image/gif", "image/webp"]
ContentPartType = Literal["text", "image"]


class ImageSource(BaseModel):
    """Reference to an image stored alongside the trajectory (ATIF v1.6+)."""

    model_config = ConfigDict(extra="forbid")

    media_type: ImageMediaType = Field(..., description="MIME type of the image.")
    path: str = Field(
        ...,
        description="Relative/absolute file path or URL pointing at the image.",
    )


class ContentPart(BaseModel):
    """One element of a multimodal `message` or `content` array (ATIF v1.6+)."""

    model_config = ConfigDict(extra="forbid")

    type: ContentPartType
    text: str | None = None
    source: ImageSource | None = None

    @model_validator(mode="after")
    def _check_payload(self) -> "ContentPart":
        if self.type == "text":
            if self.text is None:
                raise ValueError("ContentPart of type 'text' requires `text`.")
            if self.source is not None:
                raise ValueError("ContentPart of type 'text' must omit `source`.")
        else:
            if self.source is None:
                raise ValueError("ContentPart of type 'image' requires `source`.")
            if self.text is not None:
                raise ValueError("ContentPart of type 'image' must omit `text`.")
        return self
