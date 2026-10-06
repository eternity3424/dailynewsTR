"""
Tracker for stories, concepts and quizzes.
Kalıcı JSON dosyalarını yönetir ve aktif hikayeleri/kavramları günceller.
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from typing import Dict, List, Any

from src import config
from src.utils.helpers import now_tr

logger = logging.getLogger(__name__)


class StoryTracker:
    def __init__(self):
        self.stories_file = str(config.TRACKED_STORIES_FILE)
        self.concepts_file = str(config.LEARNED_CONCEPTS_FILE)
        self.quiz_file = str(config.QUIZ_HISTORY_FILE)
        
        raw_stories = self._load_json(self.stories_file, default={"stories": []})
        if isinstance(raw_stories, dict):
            self.stories: List[Dict[str, Any]] = raw_stories.get("stories", [])
        elif isinstance(raw_stories, list):
            self.stories: List[Dict[str, Any]] = raw_stories
        else:
            self.stories = []

    def _load_json(self, filepath: str, default: Any) -> Any:
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
        return default

    def _save_json(self, filepath: str, data: Any):
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving {filepath}: {e}")

    def get_active_stories(self) -> List[Dict[str, Any]]:
        return [s for s in self.stories if isinstance(s, dict) and s.get("status") == "active"]

    def update_stories(self, stories_update: Dict[str, Any]):
        try:
            updated_stories = stories_update.get("updated_stories", [])
            new_stories = stories_update.get("new_stories", [])
            archived_stories = stories_update.get("archived_stories", [])
            
            # Güncellenenleri işle
            for up_story in updated_stories:
                if not isinstance(up_story, dict):
                    continue
                for idx, s in enumerate(self.stories):
                    if isinstance(s, dict) and s.get("id") == up_story.get("id"):
                        self.stories[idx] = up_story
            
            # Arşivlenenleri işaretle
            for s in self.stories:
                if isinstance(s, dict) and s.get("id") in archived_stories:
                    s["status"] = "archived"
                    
            # Yeni hikayeleri ekle
            for n_story in new_stories:
                if not isinstance(n_story, dict):
                    continue
                n_story["id"] = str(uuid.uuid4())
                if "status" not in n_story:
                    n_story["status"] = "active"
                self.stories.append(n_story)
            
            # Maksimum aktif hikaye sınırını uygula
            active_stories = [s for s in self.stories if isinstance(s, dict) and s.get("status") == "active"]
            if len(active_stories) > config.MAX_ACTIVE_STORIES:
                sorted_active = sorted(
                    active_stories,
                    key=lambda x: len(x.get("timeline", [])), 
                    reverse=True
                )
                to_archive = sorted_active[config.MAX_ACTIVE_STORIES:]
                for arc in to_archive:
                    for s in self.stories:
                        if isinstance(s, dict) and s.get("id") == arc.get("id"):
                            s["status"] = "archived"
                            
            self.save()
        except Exception as e:
            logger.error(f"Error updating stories: {e}")

    def save(self):
        self._save_json(self.stories_file, {"stories": self.stories})

    def get_concepts(self) -> List[Dict[str, Any]]:
        raw = self._load_json(self.concepts_file, default={"concepts": []})
        if isinstance(raw, dict):
            return raw.get("concepts", [])
        elif isinstance(raw, list):
            return raw
        return []

    def add_concepts(self, new_concepts: List[Dict[str, Any]]):
        try:
            concepts = self.get_concepts()
            date_str = now_tr().isoformat()
            for c in new_concepts:
                if isinstance(c, dict):
                    c_copy = dict(c)
                    c_copy["date_learned"] = date_str
                    concepts.append(c_copy)
            self._save_json(self.concepts_file, {"concepts": concepts})
        except Exception as e:
            logger.error(f"Error adding concepts: {e}")

    def get_quiz_history(self) -> List[Dict[str, Any]]:
        raw = self._load_json(self.quiz_file, default={"quizzes": []})
        if isinstance(raw, dict):
            return raw.get("quizzes", [])
        elif isinstance(raw, list):
            return raw
        return []

    def add_quiz(self, quiz: Dict[str, Any]):
        try:
            history = self.get_quiz_history()
            quiz_copy = dict(quiz)
            quiz_copy["date"] = now_tr().isoformat()
            history.append(quiz_copy)
            self._save_json(self.quiz_file, {"quizzes": history})
        except Exception as e:
            logger.error(f"Error adding quiz: {e}")
