"""
✅ TodoApp - Professional Todo List Application with Local Storage
تطبيق قائمة المهام الاحترافي مع حفظ محلي

المميزات:
- ✨ إضافة وحذف وتعديل المهام
- 💾 حفظ تلقائي في قاعدة البيانات
- 🔍 البحث والتصفية
- 📊 عرض الإحصائيات
- 🎨 واجهة احترافية
- 🌙 وضع ليلي
- 📅 تاريخ الإنشاء والتعديل
- ⭐ تحديد الأولويات
- 🏷️ التصنيفات والعلامات
- 📱 واجهة سهلة الاستخدام
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from enum import Enum
import sqlite3

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox, QCheckBox,
    QListWidget, QListWidgetItem, QMessageBox, QFileDialog, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QInputDialog, QSpinBox,
    QDateEdit, QMenuBar, QMenu, QProgressBar, QStatusBar, QGroupBox,
    QFormLayout, QDialog, QScrollArea, QFrame
)
from PyQt6.QtGui import QIcon, QFont, QColor, QBrush, QPixmap
from PyQt6.QtCore import Qt, QDate, QDateTime, pyqtSignal, QTimer, QSize

# ═══════════════════════════════════════════════════════════════════════════════
# ⚙️ الإعدادات والثوابت
# ═══════════════════════════════════════════════════════════════════════════════

APP_NAME = "TodoApp"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Rabah Amir"

# مسار قاعدة البيانات
DB_PATH = Path.home() / f".{APP_NAME}" / "todos.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# ألوان Theme
COLORS = {
    "primary": "#6200EE",
    "secondary": "#03DAC6",
    "tertiary": "#FF0266",
    "background": "#1e1e1e",
    "surface": "#2d2d2d",
    "error": "#CF6679",
    "success": "#4CAF50",
    "warning": "#FF9800",
    "info": "#2196F3",
    "text": "#FFFFFF",
    "low": "#4CAF50",
    "medium": "#FF9800",
    "high": "#CF6679",
}

# نمط CSS
STYLE_SHEET = f"""
    QMainWindow {{
        background-color: {COLORS['background']};
    }}
    QLabel {{
        color: {COLORS['text']};
    }}
    QPushButton {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 5px;
        padding: 8px 15px;
        font-weight: bold;
        min-height: 35px;
    }}
    QPushButton:hover {{
        background-color: #7c3ff2;
    }}
    QPushButton:pressed {{
        background-color: #4600bb;
    }}
    QLineEdit, QTextEdit {{
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
        border: 1px solid #444444;
        border-radius: 5px;
        padding: 8px;
        font-size: 11px;
    }}
    QComboBox {{
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
        border: 1px solid #444444;
        border-radius: 5px;
        padding: 5px;
    }}
    QListWidget {{
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
        border: 1px solid #444444;
        border-radius: 5px;
    }}
    QTableWidget {{
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
        border: 1px solid #444444;
    }}
    QTableWidget::item {{
        padding: 5px;
    }}
    QGroupBox {{
        color: {COLORS['text']};
        border: 1px solid #444444;
        border-radius: 5px;
        padding: 10px;
        margin-top: 10px;
    }}
    QMenuBar {{
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
    }}
    QMenuBar::item:selected {{
        background-color: {COLORS['primary']};
    }}
"""

# أولويات المهام
class Priority(Enum):
    LOW = "منخفضة"
    MEDIUM = "متوسطة"
    HIGH = "عالية"

# فئات المهام
CATEGORIES = [
    "عمل",
    "شخصي",
    "تسوق",
    "صحة",
    "تعليم",
    "ترفيه",
    "أخرى"
]

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 نموذج المهام
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Todo:
    """نموذج المهمة الواحدة"""
    id: int
    title: str
    description: str
    priority: str
    category: str
    completed: bool
    created_at: str
    due_date: str
    
    def to_dict(self) -> Dict:
        """تحويل إلى قاموس"""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict) -> 'Todo':
        """إنشاء من قاموس"""
        return Todo(**data)


# ═══════════════════════════════════════════════════════════════════════════════
# 💾 قاعدة البيانات
# ═══════════════════════════════════════════════════════════════════════════════

class DatabaseManager:
    """مدير قاعدة البيانات"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """الحصول على اتصال بقاعدة البيانات"""
        return sqlite3.connect(str(self.db_path))
    
    def init_db(self):
        """إنشاء جداول قاعدة البيانات"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # جدول المهام
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT DEFAULT 'متوسطة',
                category TEXT DEFAULT 'أخرى',
                completed BOOLEAN DEFAULT 0,
                created_at TEXT NOT NULL,
                due_date TEXT,
                updated_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_todo(self, todo: Todo) -> int:
        """إضافة مهمة جديدة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO todos (title, description, priority, category, completed, created_at, due_date, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            todo.title,
            todo.description,
            todo.priority,
            todo.category,
            todo.completed,
            todo.created_at,
            todo.due_date,
            datetime.now().isoformat()
        ))
        
        todo_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return todo_id
    
    def get_all_todos(self) -> List[Todo]:
        """الحصول على جميع المهام"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, description, priority, category, completed, created_at, due_date
            FROM todos
            ORDER BY 
                CASE 
                    WHEN priority = 'عالية' THEN 1
                    WHEN priority = 'متوسطة' THEN 2
                    WHEN priority = 'منخفضة' THEN 3
                END,
                created_at DESC
        """)
        
        todos = []
        for row in cursor.fetchall():
            todo = Todo(
                id=row[0],
                title=row[1],
                description=row[2],
                priority=row[3],
                category=row[4],
                completed=bool(row[5]),
                created_at=row[6],
                due_date=row[7]
            )
            todos.append(todo)
        
        conn.close()
        return todos
    
    def get_todo_by_id(self, todo_id: int) -> Optional[Todo]:
        """الحصول على مهمة بواسطة المعرف"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, description, priority, category, completed, created_at, due_date
            FROM todos
            WHERE id = ?
        """, (todo_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Todo(
                id=row[0],
                title=row[1],
                description=row[2],
                priority=row[3],
                category=row[4],
                completed=bool(row[5]),
                created_at=row[6],
                due_date=row[7]
            )
        return None
    
    def update_todo(self, todo: Todo) -> bool:
        """تحديث مهمة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE todos
            SET title = ?, description = ?, priority = ?, category = ?, completed = ?, due_date = ?, updated_at = ?
            WHERE id = ?
        """, (
            todo.title,
            todo.description,
            todo.priority,
            todo.category,
            todo.completed,
            todo.due_date,
            datetime.now().isoformat(),
            todo.id
        ))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    def delete_todo(self, todo_id: int) -> bool:
        """حذف مهمة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    def search_todos(self, query: str) -> List[Todo]:
        """البحث عن مهام"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        search_pattern = f"%{query}%"
        cursor.execute("""
            SELECT id, title, description, priority, category, completed, created_at, due_date
            FROM todos
            WHERE title LIKE ? OR description LIKE ? OR category LIKE ?
            ORDER BY created_at DESC
        """, (search_pattern, search_pattern, search_pattern))
        
        todos = []
        for row in cursor.fetchall():
            todo = Todo(
                id=row[0],
                title=row[1],
                description=row[2],
                priority=row[3],
                category=row[4],
                completed=bool(row[5]),
                created_at=row[6],
                due_date=row[7]
            )
            todos.append(todo)
        
        conn.close()
        return todos
    
    def get_stats(self) -> Dict:
        """الحصول على الإحصائيات"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM todos")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM todos WHERE completed = 1")
        completed = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM todos WHERE priority = 'عالية'")
        high_priority = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total": total,
            "completed": completed,
            "pending": total - completed,
            "high_priority": high_priority,
            "completion_rate": (completed / total * 100) if total > 0 else 0
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 📝 نظام السجلات
# ═══════════════════════════════════════════════════════════════════════════════

def setup_logger() -> logging.Logger:
    """إعداد نظام السجلات"""
    logger = logging.getLogger(APP_NAME)
    logger.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()


# ═══════════════════════════════════════════════════════════════════════════════
# 🗂️ نوافذ الحوار
# ═══════════════════════════════════════════════════════════════════════════════

class AddEditTodoDialog(QDialog):
    """نافذة حوار لإضافة/تعديل المهام"""
    
    def __init__(self, parent=None, todo: Optional[Todo] = None):
        super().__init__(parent)
        self.todo = todo
        self.init_ui()
    
    def init_ui(self):
        """إنشاء الواجهة"""
        self.setWindowTitle("تعديل المهمة" if self.todo else "إضافة مهمة جديدة")
        self.setGeometry(100, 100, 500, 400)
        
        layout = QFormLayout()
        
        # العنوان
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("أدخل عنوان المهمة")
        if self.todo:
            self.title_input.setText(self.todo.title)
        layout.addRow("العنوان:", self.title_input)
        
        # الوصف
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("أدخل وصف المهمة (اختياري)")
        if self.todo:
            self.description_input.setText(self.todo.description)
        layout.addRow("الوصف:", self.description_input)
        
        # الأولوية
        self.priority_combo = QComboBox()
        self.priority_combo.addItems([p.value for p in Priority])
        if self.todo:
            self.priority_combo.setCurrentText(self.todo.priority)
        layout.addRow("الأولوية:", self.priority_combo)
        
        # الفئة
        self.category_combo = QComboBox()
        self.category_combo.addItems(CATEGORIES)
        if self.todo:
            self.category_combo.setCurrentText(self.todo.category)
        layout.addRow("الفئة:", self.category_combo)
        
        # تاريخ الاستحقاق
        self.due_date_input = QLineEdit()
        self.due_date_input.setPlaceholderText("YYYY-MM-DD")
        if self.todo and self.todo.due_date:
            self.due_date_input.setText(self.todo.due_date)
        layout.addRow("تاريخ الاستحقاق:", self.due_date_input)
        
        # الأزرار
        buttons_layout = QHBoxLayout()
        
        btn_save = QPushButton("💾 حفظ")
        btn_save.clicked.connect(self.accept)
        buttons_layout.addWidget(btn_save)
        
        btn_cancel = QPushButton("❌ إلغاء")
        btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(btn_cancel)
        
        layout.addRow("", buttons_layout)
        
        self.setLayout(layout)
        self.setStyleSheet(STYLE_SHEET)
    
    def get_data(self) -> Optional[Todo]:
        """الحصول على بيانات المهمة"""
        title = self.title_input.text().strip()
        
        if not title:
            QMessageBox.warning(self, "تنبيه", "يجب إدخال عنوان المهمة!")
            return None
        
        return Todo(
            id=self.todo.id if self.todo else 0,
            title=title,
            description=self.description_input.toPlainText(),
            priority=self.priority_combo.currentText(),
            category=self.category_combo.currentText(),
            completed=self.todo.completed if self.todo else False,
            created_at=self.todo.created_at if self.todo else datetime.now().isoformat(),
            due_date=self.due_date_input.text().strip() or None
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 🖼️ الشاشات والنوافذ
# ═══════════════════════════════════════════════════════════════════════════════

class TodoListWidget(QWidget):
    """عرض قائمة المهام"""
    
    todo_selected = pyqtSignal(Todo)
    todo_deleted = pyqtSignal(int)
    todo_completed = pyqtSignal(int, bool)
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
    
    def init_ui(self):
        """إنشاء الواجهة"""
        layout = QVBoxLayout()
        
        # شريط البحث والتصفية
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 ابحث عن المهام...")
        self.search_input.textChanged.connect(self.search)
        search_layout.addWidget(self.search_input)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["جميع المهام", "المهام المكتملة", "المهام المعلقة"])
        self.filter_combo.currentIndexChanged.connect(self.filter_todos)
        search_layout.addWidget(self.filter_combo)
        
        layout.addLayout(search_layout)
        
        # جدول المهام
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["✓", "العنوان", "الوصف", "الأولوية", "الفئة", "تاريخ الاستحقاق", "تاريخ الإنشاء"])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemClicked.connect(self.on_item_clicked)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_todos(self, todos: List[Todo] = None):
        """تحميل المهام في الجدول"""
        if todos is None:
            todos = self.db_manager.get_all_todos()
        
        self.table.setRowCount(0)
        
        for todo in todos:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # الاختيار
            checkbox = QCheckBox()
            checkbox.setChecked(todo.completed)
            checkbox.stateChanged.connect(lambda state, t_id=todo.id: self.toggle_todo(t_id))
            self.table.setCellWidget(row, 0, checkbox)
            
            # العنوان
            title_item = QTableWidgetItem(todo.title)
            if todo.completed:
                title_item.setForeground(QBrush(QColor("#888888")))
            self.table.setItem(row, 1, title_item)
            
            # الوصف
            desc_item = QTableWidgetItem(todo.description[:50] + "..." if len(todo.description) > 50 else todo.description)
            self.table.setItem(row, 2, desc_item)
            
            # الأولوية
            priority_item = QTableWidgetItem(todo.priority)
            if todo.priority == "عالية":
                priority_item.setForeground(QBrush(QColor(COLORS["error"])))
            elif todo.priority == "متوسطة":
                priority_item.setForeground(QBrush(QColor(COLORS["warning"])))
            else:
                priority_item.setForeground(QBrush(QColor(COLORS["success"])))
            self.table.setItem(row, 3, priority_item)
            
            # الفئة
            self.table.setItem(row, 4, QTableWidgetItem(todo.category))
            
            # تاريخ الاستحقاق
            due_date = todo.due_date if todo.due_date else "-"
            self.table.setItem(row, 5, QTableWidgetItem(due_date))
            
            # تاريخ الإنشاء
            created_date = todo.created_at.split("T")[0]
            self.table.setItem(row, 6, QTableWidgetItem(created_date))
            
            # حفظ معرف المهمة
            self.table.item(row, 1).setData(Qt.ItemDataRole.UserRole, todo.id)
    
    def on_item_clicked(self):
        """عند النقر على مهمة"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            todo_id = self.table.item(current_row, 1).data(Qt.ItemDataRole.UserRole)
            todo = self.db_manager.get_todo_by_id(todo_id)
            if todo:
                self.todo_selected.emit(todo)
    
    def toggle_todo(self, todo_id: int):
        """تبديل حالة المهمة"""
        todo = self.db_manager.get_todo_by_id(todo_id)
        if todo:
            todo.completed = not todo.completed
            self.db_manager.update_todo(todo)
            self.todo_completed.emit(todo_id, todo.completed)
            self.load_todos()
    
    def search(self):
        """البحث عن المهام"""
        query = self.search_input.text().strip()
        if query:
            todos = self.db_manager.search_todos(query)
            self.load_todos(todos)
        else:
            self.load_todos()
    
    def filter_todos(self):
        """تصفية المهام"""
        filter_type = self.filter_combo.currentText()
        todos = self.db_manager.get_all_todos()
        
        if filter_type == "المهام المكتملة":
            todos = [t for t in todos if t.completed]
        elif filter_type == "المهام المعلقة":
            todos = [t for t in todos if not t.completed]
        
        self.load_todos(todos)


class StatsWidget(QWidget):
    """عرض الإحصائيات"""
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
    
    def init_ui(self):
        """إنشاء الواجهة"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # العنوان
        title = QLabel("📊 الإحصائيات")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # الإحصائيات
        grid_layout = QHBoxLayout()
        
        # إجمالي المهام
        total_group = QGroupBox("📋 إجمالي المهام")
        total_layout = QVBoxLayout()
        self.total_label = QLabel("0")
        self.total_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_label.setStyleSheet("color: #6200EE;")
        total_layout.addWidget(self.total_label)
        total_group.setLayout(total_layout)
        grid_layout.addWidget(total_group)
        
        # المهام المكتملة
        completed_group = QGroupBox("✅ المهام المكتملة")
        completed_layout = QVBoxLayout()
        self.completed_label = QLabel("0")
        self.completed_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        self.completed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.completed_label.setStyleSheet(f"color: {COLORS['success']};")
        completed_layout.addWidget(self.completed_label)
        completed_group.setLayout(completed_layout)
        grid_layout.addWidget(completed_group)
        
        # المهام المعلقة
        pending_group = QGroupBox("⏳ المهام المعلقة")
        pending_layout = QVBoxLayout()
        self.pending_label = QLabel("0")
        self.pending_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        self.pending_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pending_label.setStyleSheet(f"color: {COLORS['warning']};")
        pending_layout.addWidget(self.pending_label)
        pending_group.setLayout(pending_layout)
        grid_layout.addWidget(pending_group)
        
        # المهام ذات الأولوية العالية
        high_group = QGroupBox("🔴 أولوية عالية")
        high_layout = QVBoxLayout()
        self.high_label = QLabel("0")
        self.high_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        self.high_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.high_label.setStyleSheet(f"color: {COLORS['error']};")
        high_layout.addWidget(self.high_label)
        high_group.setLayout(high_layout)
        grid_layout.addWidget(high_group)
        
        layout.addLayout(grid_layout)
        
        # نسبة الإنجاز
        progress_label = QLabel("نسبة الإنجاز:")
        progress_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        self.progress_text = QLabel("0%")
        self.progress_text.setFont(QFont("Arial", 12))
        self.progress_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_text)
        
        layout.addStretch()
        
        self.setLayout(layout)
    
    def update_stats(self):
        """تحديث الإحصائيات"""
        stats = self.db_manager.get_stats()
        
        self.total_label.setText(str(stats["total"]))
        self.completed_label.setText(str(stats["completed"]))
        self.pending_label.setText(str(stats["pending"]))
        self.high_label.setText(str(stats["high_priority"]))
        
        progress = int(stats["completion_rate"])
        self.progress_bar.setValue(progress)
        self.progress_text.setText(f"{progress}%")


# ═══════════════════════════════════════════════════════════════════════════════
# 🪟 النافذة الرئيسية
# ═══════════════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    """النافذة الرئيسية للتطبيق"""
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager(DB_PATH)
        self.init_ui()
        self.apply_styles()
        logger.info(f"✅ تم إنشاء {APP_NAME} v{APP_VERSION}")
    
    def init_ui(self):
        """إنشاء الواجهة"""
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setGeometry(100, 100, 1400, 800)
        self.setMinimumSize(1000, 600)
        
        # النافذة المركزية
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # العنوان
        title = QLabel("✅ TodoApp - مدير المهام المحترف")
        title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        main_layout.addWidget(title)
        
        # شريط الأدوات
        toolbar_layout = QHBoxLayout()
        
        btn_add = QPushButton("➕ مهمة جديدة")
        btn_add.setMinimumHeight(45)
        btn_add.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        btn_add.clicked.connect(self.add_todo)
        toolbar_layout.addWidget(btn_add)
        
        btn_edit = QPushButton("✏️ تعديل")
        btn_edit.setMinimumHeight(45)
        btn_edit.clicked.connect(self.edit_todo)
        toolbar_layout.addWidget(btn_edit)
        
        btn_delete = QPushButton("🗑️ حذف")
        btn_delete.setMinimumHeight(45)
        btn_delete.setStyleSheet(f"background-color: {COLORS['error']};")
        btn_delete.clicked.connect(self.delete_todo)
        toolbar_layout.addWidget(btn_delete)
        
        toolbar_layout.addStretch()
        
        btn_refresh = QPushButton("🔄 تحديث")
        btn_refresh.setMinimumHeight(45)
        btn_refresh.clicked.connect(self.refresh_data)
        toolbar_layout.addWidget(btn_refresh)
        
        btn_export = QPushButton("💾 تصدير JSON")
        btn_export.setMinimumHeight(45)
        btn_export.clicked.connect(self.export_todos)
        toolbar_layout.addWidget(btn_export)
        
        main_layout.addLayout(toolbar_layout)
        
        # التبويبات
        self.tabs = QTabWidget()
        
        # تبويب المهام
        self.todo_list_widget = TodoListWidget(self.db_manager)
        self.todo_list_widget.todo_selected.connect(self.show_todo_details)
        self.tabs.addTab(self.todo_list_widget, "📋 المهام")
        
        # تبويب الإحصائيات
        self.stats_widget = StatsWidget(self.db_manager)
        self.tabs.addTab(self.stats_widget, "📊 الإحصائيات")
        
        main_layout.addWidget(self.tabs)
        
        # شريط الحالة
        self.statusBar().showMessage("🟢 جاهز")
        
        # شريط القوائم
        self.create_menu_bar()
        
        # تحميل البيانات
        self.refresh_data()
    
    def create_menu_bar(self):
        """إنشاء شريط القوائم"""
        menubar = self.menuBar()
        
        # ملف
        file_menu = menubar.addMenu("📁 ملف")
        file_menu.addAction("➕ مهمة جديدة", self.add_todo)
        file_menu.addAction("💾 حفظ (تم حفظه تلقائياً)", self.save_todos)
        file_menu.addAction("💾 تصدير JSON", self.export_todos)
        file_menu.addSeparator()
        file_menu.addAction("🚪 خروج", self.close)
        
        # تعديل
        edit_menu = menubar.addMenu("✏️ تعديل")
        edit_menu.addAction("✏️ تعديل المهمة", self.edit_todo)
        edit_menu.addAction("🗑️ حذف المهمة", self.delete_todo)
        edit_menu.addAction("🔄 تحديث", self.refresh_data)
        
        # عرض
        view_menu = menubar.addMenu("👁️ عرض")
        view_menu.addAction("📋 المهام", lambda: self.tabs.setCurrentIndex(0))
        view_menu.addAction("📊 الإحصائيات", lambda: self.tabs.setCurrentIndex(1))
        
        # مساعدة
        help_menu = menubar.addMenu("❓ مساعدة")
        help_menu.addAction("📖 حول البرنامج", self.show_about)
    
    def add_todo(self):
        """إضافة مهمة جديدة"""
        dialog = AddEditTodoDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            todo = dialog.get_data()
            if todo:
                todo_id = self.db_manager.add_todo(todo)
                logger.info(f"✅ تم إضافة مهمة جديدة: {todo.title}")
                self.refresh_data()
                self.statusBar().showMessage(f"✅ تم إضافة المهمة: {todo.title}")
    
    def edit_todo(self):
        """تعديل المهمة المختارة"""
        current_row = self.todo_list_widget.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار مهمة لتعديلها!")
            return
        
        todo_id = self.todo_list_widget.table.item(current_row, 1).data(Qt.ItemDataRole.UserRole)
        todo = self.db_manager.get_todo_by_id(todo_id)
        
        if todo:
            dialog = AddEditTodoDialog(self, todo)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_todo = dialog.get_data()
                if updated_todo:
                    self.db_manager.update_todo(updated_todo)
                    logger.info(f"✏️ تم تعديل المهمة: {updated_todo.title}")
                    self.refresh_data()
                    self.statusBar().showMessage(f"✅ تم تعديل المهمة: {updated_todo.title}")
    
    def delete_todo(self):
        """حذف المهمة المختارة"""
        current_row = self.todo_list_widget.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار مهمة لحذفها!")
            return
        
        todo_id = self.todo_list_widget.table.item(current_row, 1).data(Qt.ItemDataRole.UserRole)
        todo = self.db_manager.get_todo_by_id(todo_id)
        
        if todo:
            reply = QMessageBox.question(
                self,
                "تأكيد الحذف",
                f"هل تريد حذف المهمة:\n{todo.title}؟",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.db_manager.delete_todo(todo_id)
                logger.info(f"🗑️ تم حذف المهمة: {todo.title}")
                self.refresh_data()
                self.statusBar().showMessage(f"🗑️ تم حذف المهمة: {todo.title}")
    
    def show_todo_details(self, todo: Todo):
        """عرض تفاصيل المهمة"""
        details = f"""
        📋 عنوان المهمة: {todo.title}
        
        📝 الوصف: {todo.description}
        
        🎯 الأولوية: {todo.priority}
        
        🏷️ الفئة: {todo.category}
        
        📅 تاريخ الاستحقاق: {todo.due_date if todo.due_date else "-"}
        
        🕐 تاريخ الإنشاء: {todo.created_at.split('T')[0]}
        
        ✓ الحالة: {'مكتملة ✅' if todo.completed else 'معلقة ⏳'}
        """
        
        QMessageBox.information(self, "تفاصيل المهمة", details)
    
    def refresh_data(self):
        """تحديث البيانات"""
        self.todo_list_widget.load_todos()
        self.stats_widget.update_stats()
        self.statusBar().showMessage("✅ تم التحديث")
        logger.info("🔄 تم تحديث البيانات")
    
    def save_todos(self):
        """حفظ المهام (تم حفظها تلقائياً)"""
        QMessageBox.information(self, "حفظ", "✅ تم حفظ المهام تلقائياً في قاعدة البيانات!")
        logger.info("💾 تم حفظ المهام")
    
    def export_todos(self):
        """تصدير المهام إلى JSON"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "تصدير المهام",
            str(Path.home() / "todos.json"),
            "JSON Files (*.json)"
        )
        
        if file_path:
            todos = self.db_manager.get_all_todos()
            data = [todo.to_dict() for todo in todos]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "نجاح", f"✅ تم تصدير المهام إلى:\n{file_path}")
            logger.info(f"📤 تم تصدير المهام: {file_path}")
    
    def show_about(self):
        """عرض معلومات عن البرنامج"""
        about_text = f"""
        ✅ {APP_NAME}
        
        الإصدار: {APP_VERSION}
        طوّره: {APP_AUTHOR}
        
        🎯 مدير المهام الاحترافي مع حفظ محلي
        
        المميزات:
        ✅ إضافة وتعديل وحذف المهام
        ✅ حفظ تلقائي في قاعدة بيانات محلية
        ✅ البحث والتصفية
        ✅ الإحصائيات والإحصاءات
        ✅ تحديد الأولويات والفئات
        ✅ تصدير JSON
        ✅ واجهة احترافية
        
        📍 مسار قاعدة البيانات:
        {DB_PATH}
        """
        
        QMessageBox.information(self, "عن البرنامج", about_text)
    
    def apply_styles(self):
        """تطبيق الأنماط"""
        self.setStyleSheet(STYLE_SHEET)
    
    def closeEvent(self, event):
        """معالجة إغلاق النافذة"""
        reply = QMessageBox.question(
            self,
            "تأكيد الخروج",
            "هل تريد الخروج من البرنامج؟\nتم حفظ جميع المهام تلقائياً.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            logger.info("👋 جاري إغلاق التطبيق...")
            event.accept()
        else:
            event.ignore()


# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 نقطة البداية
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """الدالة الرئيسية"""
    try:
        logger.info(f"🚀 بدء تشغيل {APP_NAME} v{APP_VERSION}")
        
        app = QApplication(sys.argv)
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion(APP_VERSION)
        
        logger.info(f"🪟 جاري إنشاء النافذة الرئيسية...")
        main_window = MainWindow()
        main_window.show()
        
        logger.info("✨ تم تشغيل التطبيق بنجاح!")
        logger.info("=" * 80)
        
        sys.exit(app.exec())
    
    except Exception as e:
        logger.error(f"❌ خطأ: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
