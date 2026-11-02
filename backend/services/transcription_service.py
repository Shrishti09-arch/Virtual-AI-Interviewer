"""
Local Speech-to-Text & Communication Analysis Service
Provides local Whisper audio transcription (or manual fallback) and deep speech analytics:
WPM pacing, filler word detection, pause analysis, vocabulary diversity, and structural clarity.

ETHICAL NOTICE:
This system analyzes objective verbal indicators (fluency, pacing, fillers, structure).
It does NOT claim to detect emotions, honesty, or personality traits from vocal pitch or facial appearance.
"""
import os
import re
import logging
from typing import Dict, Any, List, Optional
from app.services.interview_service import InterviewService, FILLER_WORDS, STAR_MARKERS

logger = logging.getLogger(__name__)


class TranscriptionService:
    """
    Speech transcription and communication performance analysis engine.
    """

    DISCLAIMER = (
        "Communication analysis is computed purely from linguistic and pacing markers "
        "(words per minute, filler words, vocabulary diversity, and structural signposts). "
        "It does not evaluate facial expressions, physiological stress, honesty, or personality."
    )

    @classmethod
    def transcribe_audio(
        cls,
        audio_path_or_bytes: Any,
        language: str = "en",
        model_size: str = "base"
    ) -> Dict[str, Any]:
        """
        Transcribe audio recording using local Whisper or faster-whisper.
        Falls back smoothly if local whisper weights/library are not installed.
        """
        # Check if faster-whisper or openai-whisper is installed
        try:
            import whisper  # type: ignore
            model = whisper.load_model(model_size)
            if isinstance(audio_path_or_bytes, str) and os.path.exists(audio_path_or_bytes):
                result = model.transcribe(audio_path_or_bytes, language=language)
                text = result.get("text", "").strip()
                return {
                    "transcript": text,
                    "engine": "local-whisper",
                    "success": True,
                    "duration_seconds": result.get("duration", 0),
                    "segments": result.get("segments", [])
                }
        except ImportError:
            logger.info("Local Whisper not installed. Using manual transcript entry / fallback mode.")
        except Exception as e:
            logger.warning(f"Local Whisper transcription error: {e}. Fallback available.")

        # Graceful fallback response
        return {
            "transcript": "",
            "engine": "manual-entry-required",
            "success": False,
            "message": "Local Whisper model not detected. Please use manual transcript entry or type your response."
        }

    @classmethod
    def analyze_communication(
        cls,
        answer_text: str,
        speaking_duration_seconds: int = 60,
        pauses_count: int = 0
    ) -> Dict[str, Any]:
        """
        Extract objective communication indicators:
        - Speaking duration
        - Words per minute (WPM)
        - Filler words frequency and distribution
        - Immediate word repetitions
        - Pauses count
        - Vocabulary diversity / richness
        - STAR framework structural markers
        """
        stats = InterviewService.analyze_communication(
            answer_text=answer_text,
            time_spent_seconds=speaking_duration_seconds,
            pauses_count=pauses_count
        )
        stats["ethical_disclaimer"] = cls.DISCLAIMER
        return stats


transcription_service = TranscriptionService()

__all__ = ["TranscriptionService", "transcription_service", "FILLER_WORDS", "STAR_MARKERS"]
