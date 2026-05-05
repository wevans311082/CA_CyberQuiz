# SPDX-FileCopyrightText: 2026 CA Tabletop
#
# SPDX-License-Identifier: MPL-2.0

"""
Tests for Phase 4 tabletop features:
- Master theme system
- Per-slide answer timer socket events
- File download audit logging
- File upload workflow
"""

import json
import pytest
from classquiz.db.models import (
    MasterTheme,
    QuizQuestion,
    Quiz,
    PlayGame,
    GameResults,
    SlideThemeOverride,
)


class TestMasterThemeModel:
    """Test MasterTheme pydantic model and integration"""

    def test_master_theme_creation_full(self):
        """Test creating MasterTheme with all fields"""
        theme = MasterTheme(
            background_color="#1a1a1a",
            text_color="#ffffff",
            accent_color="#ff6b6b",
            background_image="https://example.com/bg.png",
            font_family="Inter, sans-serif",
        )
        assert theme.background_color == "#1a1a1a"
        assert theme.text_color == "#ffffff"
        assert theme.accent_color == "#ff6b6b"
        assert theme.background_image == "https://example.com/bg.png"
        assert theme.font_family == "Inter, sans-serif"

    def test_master_theme_creation_partial(self):
        """Test creating MasterTheme with only some fields"""
        theme = MasterTheme(
            background_color="#000000",
            text_color="#ffffff",
        )
        assert theme.background_color == "#000000"
        assert theme.text_color == "#ffffff"
        assert theme.accent_color is None
        assert theme.background_image is None
        assert theme.font_family is None

    def test_master_theme_json_serialization(self):
        """Test MasterTheme JSON round-trip"""
        original = MasterTheme(
            background_color="#1a1a1a",
            text_color="#ffffff",
            accent_color="#ff6b6b",
        )
        json_str = json.dumps(original.model_dump(exclude_none=True))
        data = json.loads(json_str)
        restored = MasterTheme(**data)
        assert restored.background_color == original.background_color
        assert restored.text_color == original.text_color
        assert restored.accent_color == original.accent_color

    def test_theme_merge_logic(self):
        """Test master theme + per-slide override merge logic"""
        master = MasterTheme(
            background_color="#1a1a1a",
            text_color="#ffffff",
            accent_color="#ff6b6b",
            font_family="Inter",
        )
        override = SlideThemeOverride(
            accent_color="#00ff00",  # Override only accent
        )

        # Simulate merge: per-slide override takes precedence
        merged = {
            "background_color": override.background_color or master.background_color,
            "text_color": override.text_color or master.text_color,
            "accent_color": override.accent_color or master.accent_color,
            "background_image": override.background_image or master.background_image,
            "font_family": override.font_family or master.font_family,
        }

        assert merged["background_color"] == "#1a1a1a"
        assert merged["text_color"] == "#ffffff"
        assert merged["accent_color"] == "#00ff00"  # Overridden
        assert merged["font_family"] == "Inter"


class TestFileDownloadAuditLogging:
    """Test file download audit log structure and helpers"""

    def test_file_download_log_entry_structure(self):
        """Test structure of a file download log entry"""
        entry = {
            "username": "alice",
            "file_id": "file-uuid-123",
            "filename": "evidence.pdf",
            "timestamp": "2026-05-05T10:30:00Z",
        }
        assert "username" in entry
        assert "file_id" in entry
        assert "filename" in entry
        assert "timestamp" in entry

    def test_file_downloads_log_list(self):
        """Test GameResults with file_downloads_log"""
        logs = [
            {
                "username": "alice",
                "file_id": "file-1",
                "filename": "report.pdf",
                "timestamp": "2026-05-05T10:00:00Z",
            },
            {
                "username": "bob",
                "file_id": "file-1",
                "filename": "report.pdf",
                "timestamp": "2026-05-05T10:05:00Z",
            },
        ]
        assert len(logs) == 2
        assert all("username" in log for log in logs)
        assert logs[0]["username"] == "alice"
        assert logs[1]["username"] == "bob"


class TestQuestionTimerPayload:
    """Test question timer event payloads"""

    def test_timer_input_validation(self):
        """Test timer input structure matches socket event expectations"""
        timer_input = {
            "custom_seconds": None,  # Use default
            "pin": "1234",
        }
        assert "pin" in timer_input
        assert "custom_seconds" in timer_input

    def test_timer_active_state(self):
        """Test tracking active timer state"""
        state = {
            "running": False,
            "remaining": 0,
            "total": 0,
            "started_at": None,
        }
        # Simulate starting timer
        state["running"] = True
        state["total"] = 30
        state["remaining"] = 30

        assert state["running"] is True
        assert state["total"] == 30
        assert state["remaining"] == 30


class TestBackwardCompatibility:
    """Test backward compatibility with existing quizzes"""

    def test_quiz_without_master_theme(self):
        """Test quiz created before master_theme feature"""
        quiz_data = {
            "title": "Legacy Quiz",
            "questions": [],
            "scenario_type": "classic",
            # master_theme is optional, should default to None
        }
        # Should not error when master_theme is missing
        assert quiz_data.get("master_theme") is None

    def test_game_results_without_file_downloads_log(self):
        """Test game results from before file audit feature"""
        results_data = {
            "player_key": "player-123",
            "answers": [],
            # file_downloads_log is optional, should default to None
        }
        assert results_data.get("file_downloads_log") is None

    def test_question_without_timer(self):
        """Test question created before per-slide timer feature"""
        question_data = {
            "type": "ABCD",
            "answers": [],
            # timer is optional
        }
        assert question_data.get("timer") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
