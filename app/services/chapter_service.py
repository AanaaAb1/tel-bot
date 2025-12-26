from sqlalchemy.orm import Session
from app.models.chapter import Chapter
from app.models.course import Course
from app.database.session import SessionLocal
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# Standalone functions for backward compatibility
def get_chapters_by_course(course_id: int) -> List[Chapter]:
    """Get all chapters for a specific course"""
    db = SessionLocal()
    try:
        chapters = db.query(Chapter).filter(
            Chapter.course_id == course_id
        ).order_by(Chapter.order_index, Chapter.name).all()
        return chapters
    except Exception as e:
        logger.error(f"Error getting chapters for course {course_id}: {e}")
        return []
    finally:
        db.close()

def get_chapter_by_id(chapter_id: int) -> Optional[Chapter]:
    """Get chapter by ID"""
    db = SessionLocal()
    try:
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        return chapter
    except Exception as e:
        logger.error(f"Error getting chapter {chapter_id}: {e}")
        return None
    finally:
        db.close()

class ChapterService:
    """Service for managing course chapters"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_chapter(self, course_id: int, name: str, description: str = None, order_index: int = 0) -> Chapter:
        """Create a new chapter for a course"""
        try:
            # Verify course exists
            course = self.db.query(Course).filter(Course.id == course_id).first()
            if not course:
                raise ValueError(f"Course with ID {course_id} not found")
            
            chapter = Chapter(
                course_id=course_id,
                name=name,
                description=description,
                order_index=order_index
            )
            
            self.db.add(chapter)
            self.db.commit()
            self.db.refresh(chapter)
            
            logger.info(f"Created chapter '{name}' for course {course_id}")
            return chapter
            
        except Exception as e:
            logger.error(f"Error creating chapter: {e}")
            self.db.rollback()
            raise
    
    def get_chapters_by_course(self, course_id: int) -> List[Chapter]:
        """Get all chapters for a specific course"""
        try:
            chapters = self.db.query(Chapter).filter(
                Chapter.course_id == course_id
            ).order_by(Chapter.order_index, Chapter.name).all()
            
            return chapters
            
        except Exception as e:
            logger.error(f"Error getting chapters for course {course_id}: {e}")
            return []
    
    def get_chapter_by_id(self, chapter_id: int) -> Optional[Chapter]:
        """Get chapter by ID"""
        try:
            chapter = self.db.query(Chapter).filter(Chapter.id == chapter_id).first()
            return chapter
            
        except Exception as e:
            logger.error(f"Error getting chapter {chapter_id}: {e}")
            return None
    
    def update_chapter(self, chapter_id: int, name: str = None, description: str = None, 
                      order_index: int = None) -> Optional[Chapter]:
        """Update chapter information"""
        try:
            chapter = self.get_chapter_by_id(chapter_id)
            if not chapter:
                return None
            
            if name is not None:
                chapter.name = name
            if description is not None:
                chapter.description = description
            if order_index is not None:
                chapter.order_index = order_index
            
            self.db.commit()
            self.db.refresh(chapter)
            
            logger.info(f"Updated chapter {chapter_id}")
            return chapter
            
        except Exception as e:
            logger.error(f"Error updating chapter {chapter_id}: {e}")
            self.db.rollback()
            return None
    
    def delete_chapter(self, chapter_id: int) -> bool:
        """Delete a chapter"""
        try:
            chapter = self.get_chapter_by_id(chapter_id)
            if not chapter:
                return False
            
            self.db.delete(chapter)
            self.db.commit()
            
            logger.info(f"Deleted chapter {chapter_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting chapter {chapter_id}: {e}")
            self.db.rollback()
            return False
    
    def get_chapters_with_question_count(self, course_id: int) -> List[dict]:
        """Get chapters with question count for a course"""
        try:
            chapters = self.db.query(Chapter).filter(
                Chapter.course_id == course_id
            ).order_by(Chapter.order_index, Chapter.name).all()
            
            result = []
            for chapter in chapters:
                question_count = len(chapter.questions)
                result.append({
                    'id': chapter.id,
                    'name': chapter.name,
                    'description': chapter.description,
                    'order_index': chapter.order_index,
                    'question_count': question_count
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting chapters with question count: {e}")
            return []
    
    def reorder_chapters(self, course_id: int, chapter_orders: List[tuple]) -> bool:
        """Reorder chapters for a course (list of (chapter_id, new_order) tuples)"""
        try:
            for chapter_id, new_order in chapter_orders:
                chapter = self.get_chapter_by_id(chapter_id)
                if chapter and chapter.course_id == course_id:
                    chapter.order_index = new_order
            
            self.db.commit()
            logger.info(f"Reordered chapters for course {course_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error reordering chapters: {e}")
            self.db.rollback()
            return False

