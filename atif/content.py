from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ImageMediaType = Literal["image/jpeg", "image/png", "image/gif", "image/webp"]
AudioMediaType = Literal[
    "audio/wav",
    "audio/mpeg",
    "audio/mp4",
    "audio/aac",
    "audio/ogg",
    "audio/flac",
    "audio/webm",
    "audio/aiff",
]
ContentPartType = Literal["text", "image", "audio"]

_AUDIO_MEDIA_TYPE_ALIASES: dict[str, AudioMediaType] = {
    "audio/mp3": "audio/mpeg",
    "audio/mpga": "audio/mpeg",
    "audio/x-mpeg": "audio/mpeg",
    "audio/x-wav": "audio/wav",
    "audio/wave": "audio/wav",
    "audio/vnd.wave": "audio/wav",
    "audio/x-m4a": "audio/mp4",
    "audio/m4a": "audio/mp4",
    "audio/x-aac": "audio/aac",
    "audio/x-flac": "audio/flac",
    "audio/x-aiff": "audio/aiff",
}


class ImageSource(BaseModel):
    """Reference to an image stored alongside the trajectory (ATIF v1.6+)."""

    model_config = ConfigDict(extra="forbid")

    media_type: ImageMediaType = Field(..., description="MIME type of the image.")
    path: str = Field(
        ...,
        description="Relative/absolute file path or URL pointing at the image.",
    )


class AudioSource(BaseModel):
    """Reference to an audio file stored alongside the trajectory (ATIF v1.8+)."""

    model_config = ConfigDict(extra="forbid")

    media_type: AudioMediaType = Field(
        ...,
        description="Canonical MIME type of the audio; common aliases are normalized.",
    )
    path: str = Field(
        ...,
        description="Relative/absolute file path or URL pointing at the audio.",
    )
    duration_sec: float | None = Field(
        default=None,
        ge=0,
        description="Duration of the audio in seconds; omit when unknown.",
    )

    @field_validator("media_type", mode="before")
    @classmethod
    def _normalize_media_type(cls, v: Any) -> Any:
        if not isinstance(v, str):
            return v
        normalized = v.strip().lower()
        return _AUDIO_MEDIA_TYPE_ALIASES.get(normalized, normalized)


class ContentPart(BaseModel):
    """One element of a multimodal `message` or `content` array (ATIF v1.6+)."""

    model_config = ConfigDict(extra="forbid")

    type: ContentPartType
    text: str | None = None
    source: ImageSource | AudioSource | None = None

    @model_validator(mode="after")
    def _check_payload(self) -> "ContentPart":
        if self.type == "text":
            if self.text is None:
                raise ValueError("ContentPart of type 'text' requires `text`.")
            if self.source is not None:
                raise ValueError("ContentPart of type 'text' must omit `source`.")
            return self

        if self.source is None:
            raise ValueError(f"ContentPart of type {self.type!r} requires `source`.")
        if self.text is not None:
            raise ValueError(f"ContentPart of type {self.type!r} must omit `text`.")
        expected = ImageSource if self.type == "image" else AudioSource
        if not isinstance(self.source, expected):
            raise ValueError(
                f"ContentPart of type {self.type!r} requires an `{expected.__name__}`, "
                f"got media_type={self.source.media_type!r}."
            )
        return self
