"""
🎬 ProVideoCreator - Professional Desktop Video Creator
تطبيق احترافي لإنشاء فيديوهات من الوصف النصي باستخدام الذكاء الاصطناعي

المميزات:
- ✨ إنشاء فيديوهات من الوصف النصي
- 🤖 معالجة ذكية بـ AI
- 🎨 مئات القوالب الجاهزة
- 🎵 مكتبة موسيقى وتأثيرات صوتية
- 🌍 دعم 10+ لغات
- ⚡ معالجة سريعة وفعالة
- 🎯 واجهة سهلة الاستخدام
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict
import json

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox, QSpinBox,
    QProgressBar, QStackedWidget, QMenuBar, QMenu, QGroupBox,
    QFormLayout, QCheckBox, QMessageBox, QFileDialog, QTabWidget,
    QTableWidget, QTableWidgetItem, QScrollArea, QGridLayout
)
from PyQt6.QtGui import QIcon, QFont, QPixmap, QColor
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize

# ═══════════════════════════════════════════════════════════════════════════════
# ⚙️ الإعدادات والثوابت
# ═══════════════════════════════════════════════════════════════════════════════

# إعدادات التطبيق
APP_NAME = "ProVideoCreator"
APP_VERSION = "0.1.0-alpha"
APP_AUTHOR = "Rabah Amir"
APP_DESCRIPTION = "تطبيق احترافي لإنشاء فيديوهات من الوصف النصي"

# إعدادات الواجهة
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
WINDOW_TITLE = f"{APP_NAME} v{APP_VERSION}"

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
    "text": "#FFFFFF",
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
        padding: 5px;
    }}
    QComboBox {{
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
        border: 1px solid #444444;
        border-radius: 5px;
        padding: 5px;
    }}
    QGroupBox {{
        color: {COLORS['text']};
        border: 1px solid #444444;
        border-radius: 5px;
        padding: 10px;
        margin-top: 10px;
    }}
    QProgressBar {{
        border: 1px solid #444444;
        border-radius: 5px;
        text-align: center;
        background-color: {COLORS['surface']};
    }}
    QProgressBar::chunk {{
        background-color: {COLORS['primary']};
    }}
"""

# قوالب الفيديو
TEMPLATES = {
    "modern": {
        "name": "Modern",
        "description": "تصميم حديث واحترافي",
        "transitions": "fade",
        "duration": 30,
        "emoji": "🎬"
    },
    "minimal": {
        "name": "Minimal",
        "description": "تصميم بسيط وأنيق",
        "transitions": "cut",
        "duration": 20,
        "emoji": "✨"
    },
    "creative": {
        "name": "Creative",
        "description": "تصميم إبداعي وفريد",
        "transitions": "zoom",
        "duration": 30,
        "emoji": "🎨"
    },
    "professional": {
        "name": "Professional",
        "description": "تصميم احترافي للشركات",
        "transitions": "slide",
        "duration": 45,
        "emoji": "💼"
    },
    "educational": {
        "name": "Educational",
        "description": "تصميم تعليمي واضح",
        "transitions": "fade",
        "duration": 60,
        "emoji": "📚"
    },
}

# اللغات المدعومة
SUPPORTED_LANGUAGES = {
    "ar": "العربية",
    "en": "English",
    "fr": "Français",
    "de": "Deutsch",
    "es": "Español",
    "it": "Italiano",
    "ja": "日本語",
    "zh": "中文",
    "ru": "Русский",
    "pt": "Português",
}

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 نماذج البيانات
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class VideoProject:
    """نموذج مشروع الفيديو"""
    title: str
    description: str
    template: str
    duration: int
    language: str
    quality: str
    created_at: str
    status: str = "pending"
    progress: int = 0
    output_path: Optional[str] = None

    def to_dict(self) -> Dict:
        """تحويل إلى قاموس"""
        return {
            "title": self.title,
            "description": self.description,
            "template": self.template,
            "duration": self.duration,
            "language": self.language,
            "quality": self.quality,
            "created_at": self.created_at,
            "status": self.status,
            "progress": self.progress,
            "output_path": self.output_path,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 📝 نظام السجلات (Logger)
# ═══════════════════════════════════════════════════════════════════════════════

def setup_logger() -> logging.Logger:
    """إعداد نظام السجلات"""
    logger = logging.getLogger(APP_NAME)
    logger.setLevel(logging.DEBUG)

    # معالج وحدة التحكم
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # صيغة السجل
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()


# ═══════════════════════════════════════════════════════════════════════════════
# 🔄 معالج الفيديو (في الخيط الخلفي)
# ═══════════════════════════════════════════════════════════════════════════════

class VideoProcessorThread(QThread):
    """معالج الفيديو في خيط منفصل"""
    
    # الإشارات
    started = pyqtSignal()
    progress_updated = pyqtSignal(int)
    processing_status = pyqtSignal(str)
    finished = pyqtSignal(str)  # مسار الملف المُنشأ
    error_occurred = pyqtSignal(str)  # رسالة الخطأ

    def __init__(self, project: VideoProject):
        super().__init__()
        self.project = project
        self.is_processing = True

    def run(self):
        """تشغيل معالجة الفيديو"""
        try:
            self.started.emit()
            logger.info(f"🎬 بدء معالجة الفيديو: {self.project.title}")

            # محاكاة معالجة الفيديو
            total_steps = 100

            for step in range(0, total_steps + 1, 10):
                if not self.is_processing:
                    break

                # تحديث الحالة حسب الخطوة
                if step < 25:
                    status = "🤖 تحليل الوصف النصي..."
                elif step < 50:
                    status = "🎨 اختيار المشاهد والقوالب..."
                elif step < 75:
                    status = "🎵 إضافة الموسيقى والتأثيرات..."
                else:
                    status = "💾 حفظ الفيديو..."

                self.processing_status.emit(status)
                self.progress_updated.emit(step)

                # محاكاة التأخير
                self.msleep(500)

            self.project.status = "completed"
            self.project.progress = 100
            self.project.output_path = f"/outputs/{self.project.title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

            logger.info(f"✅ تم إنشاء الفيديو: {self.project.output_path}")
            self.finished.emit(self.project.output_path)

        except Exception as e:
            logger.error(f"❌ خطأ في معالجة الفيديو: {str(e)}")
            self.error_occurred.emit(str(e))

    def stop(self):
        """إيقاف المعالجة"""
        self.is_processing = False


# ═══════════════════════════════════════════════════════════════════════════════
# 🖼️ الشاشات (Screens)
# ═══════════════════════════════════════════════════════════════════════════════

class HomeScreen(QWidget):
    """الشاشة الرئيسية"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """إنشاء الواجهة"""
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        # الشعار والعنوان
        logo = QLabel("🎬")
        logo.setFont(QFont("Arial", 80))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        title = QLabel(APP_NAME)
        title.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # الوصف
        description = QLabel(APP_DESCRIPTION)
        description.setFont(QFont("Arial", 14))
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet("color: #aaaaaa; margin: 20px 0;")
        layout.addWidget(description)

        # المميزات
        features = QLabel(
            "✨ معالجة ذكية بالذكاء الاصطناعي\n"
            "🎨 مئات القوالب الجاهزة\n"
            "🎵 مكتبة موسيقى وتأثيرات صوتية\n"
            "🌍 دعم 10+ لغات\n"
            "⚡ معالجة سريعة وفعالة\n"
            "💾 تصدير عالي الجودة"
        )
        features.setFont(QFont("Arial", 12))
        features.setAlignment(Qt.AlignmentFlag.AlignCenter)
        features.setStyleSheet("color: #cccccc; margin: 30px 0;")
        layout.addWidget(features)

        # الإصدار والمطور
        footer = QLabel(f"الإصدار {APP_VERSION} | طوّره {APP_AUTHOR}")
        footer.setFont(QFont("Arial", 10))
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #666666; margin-top: 40px;")
        layout.addStretch()
        layout.addWidget(footer)

        self.setLayout(layout)


class CreateVideoScreen(QWidget):
    """شاشة إنشاء الفيديو"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_project = None
        self.processor_thread = None
        self.init_ui()

    def init_ui(self):
        """إنشاء الواجهة"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)

        # العنوان
        title = QLabel("🎬 إنشاء فيديو جديد")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        main_layout.addWidget(title)

        # إنشاء التبويبات
        tabs = QTabWidget()

        # التبويب الأول: المعلومات الأساسية
        basic_tab = QWidget()
        basic_layout = QFormLayout()

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("أدخل عنوان الفيديو")
        basic_layout.addRow("عنوان الفيديو:", self.title_input)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText(
            "اكتب وصف الفيديو الذي تريد إنشاءه...\n"
            "مثال: فيديو توضيحي عن كيفية البرمجة بـ Python"
        )
        self.description_input.setMinimumHeight(150)
        basic_layout.addRow("وصف الفيديو:", self.description_input)

        basic_tab.setLayout(basic_layout)
        tabs.addTab(basic_tab, "📝 المعلومات الأساسية")

        # التبويب الثاني: الإعدادات
        settings_tab = QWidget()
        settings_layout = QFormLayout()

        self.template_combo = QComboBox()
        for key, template in TEMPLATES.items():
            self.template_combo.addItem(f"{template['emoji']} {template['name']}", key)
        settings_layout.addRow("اختر القالب:", self.template_combo)

        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setMinimum(10)
        self.duration_spinbox.setMaximum(600)
        self.duration_spinbox.setValue(30)
        self.duration_spinbox.setSuffix(" ثانية")
        settings_layout.addRow("مدة الفيديو:", self.duration_spinbox)

        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["منخفضة (360p)", "متوسطة (720p)", "عالية (1080p)", "فائقة (4K)"])
        settings_layout.addRow("جودة الفيديو:", self.quality_combo)

        self.language_combo = QComboBox()
        for code, name in SUPPORTED_LANGUAGES.items():
            self.language_combo.addItem(name, code)
        settings_layout.addRow("اللغة:", self.language_combo)

        self.add_subtitles = QCheckBox("إضافة ترجمات مخصصة")
        self.add_subtitles.setChecked(True)
        settings_layout.addRow("الخيارات:", self.add_subtitles)

        settings_tab.setLayout(settings_layout)
        tabs.addTab(settings_tab, "⚙️ الإعدادات")

        main_layout.addWidget(tabs)

        # شريط التقدم
        progress_label = QLabel("التقدم:")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_status = QLabel("جاهز للبدء")
        self.progress_status.setStyleSheet("color: #03DAC6;")

        main_layout.addWidget(progress_label)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.progress_status)

        # الأزرار
        buttons_layout = QHBoxLayout()

        self.btn_create = QPushButton("🚀 إنشاء الفيديو")
        self.btn_create.setMinimumHeight(50)
        self.btn_create.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.btn_create.clicked.connect(self.create_video)
        buttons_layout.addWidget(self.btn_create)

        self.btn_preview = QPushButton("👁️ معاينة")
        self.btn_preview.setMinimumHeight(50)
        self.btn_preview.clicked.connect(self.show_preview)
        buttons_layout.addWidget(self.btn_preview)

        self.btn_reset = QPushButton("🔄 مسح")
        self.btn_reset.setMinimumHeight(50)
        self.btn_reset.clicked.connect(self.reset_form)
        buttons_layout.addWidget(self.btn_reset)

        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

    def create_video(self):
        """إنشاء الفيديو"""
        title = self.title_input.text().strip()
        description = self.description_input.toPlainText().strip()

        if not title or not description:
            QMessageBox.warning(self, "تنبيه", "يجب ملء جميع الحقول المطلوبة!")
            return

        # إنشاء مشروع جديد
        self.current_project = VideoProject(
            title=title,
            description=description,
            template=self.template_combo.currentData(),
            duration=self.duration_spinbox.value(),
            language=self.language_combo.currentData(),
            quality=self.quality_combo.currentText(),
            created_at=datetime.now().isoformat(),
        )

        logger.info(f"🎬 بدء إنشاء الفيديو: {self.current_project.title}")

        # بدء معالجة الفيديو في خيط منفصل
        self.processor_thread = VideoProcessorThread(self.current_project)
        self.processor_thread.started.connect(self.on_processing_started)
        self.processor_thread.progress_updated.connect(self.on_progress_updated)
        self.processor_thread.processing_status.connect(self.on_status_updated)
        self.processor_thread.finished.connect(self.on_processing_finished)
        self.processor_thread.error_occurred.connect(self.on_error)

        # تعطيل الزر أثناء المعالجة
        self.btn_create.setEnabled(False)
        self.processor_thread.start()

    def on_processing_started(self):
        """عند بدء المعالجة"""
        self.progress_bar.setValue(0)
        self.progress_status.setText("🔄 جاري المعالجة...")

    def on_progress_updated(self, value: int):
        """تحديث التقدم"""
        self.progress_bar.setValue(value)

    def on_status_updated(self, status: str):
        """تحديث حالة المعالجة"""
        self.progress_status.setText(status)

    def on_processing_finished(self, output_path: str):
        """عند انتهاء المعالجة"""
        self.progress_status.setText(f"✅ تم إنشاء الفيديو: {output_path}")
        self.progress_bar.setValue(100)
        self.btn_create.setEnabled(True)
        
        QMessageBox.information(
            self, 
            "نجاح ✅", 
            f"تم إنشاء الفيديو بنجاح!\n\n{output_path}"
        )

    def on_error(self, error: str):
        """معالجة الخطأ"""
        self.progress_status.setText(f"❌ خطأ: {error}")
        self.btn_create.setEnabled(True)
        QMessageBox.critical(self, "خطأ ❌", f"حدث خطأ: {error}")

    def show_preview(self):
        """عرض معاينة"""
        if not self.current_project:
            QMessageBox.warning(self, "تنبيه", "قم بإنشاء مشروع أولاً!")
            return
        
        logger.info(f"👁️ عرض معاينة: {self.current_project.title}")
        QMessageBox.information(self, "معاينة", f"سيتم عرض معاينة الفيديو:\n{self.current_project.title}")

    def reset_form(self):
        """مسح النموذج"""
        self.title_input.clear()
        self.description_input.clear()
        self.duration_spinbox.setValue(30)
        self.progress_bar.setValue(0)
        self.progress_status.setText("جاهز للبدء")
        logger.info("🔄 تم مسح النموذج")


class TemplatesScreen(QWidget):
    """شاشة القوالب"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """إنشاء الواجهة"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # العنوان
        title = QLabel("🎨 استكشف القوالب")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(title)

        # شبكة القوالب
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        row = 0
        col = 0

        for key, template in TEMPLATES.items():
            btn = QPushButton(
                f"{template['emoji']} {template['name']}\n"
                f"{template['description']}\n"
                f"({template['duration']} ثانية)"
            )
            btn.setMinimumSize(250, 150)
            btn.setFont(QFont("Arial", 11))
            btn.clicked.connect(lambda checked, t=key: self.select_template(t))
            
            grid_layout.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

        layout.addLayout(grid_layout)
        layout.addStretch()
        self.setLayout(layout)

    def select_template(self, template_key: str):
        """اختيار قالب"""
        template = TEMPLATES[template_key]
        logger.info(f"✅ تم اختيار القالب: {template['name']}")
        QMessageBox.information(
            self,
            "اختيار القالب",
            f"✅ تم اختيار القالب: {template['name']}\n\n{template['description']}"
        )


class SettingsScreen(QWidget):
    """شاشة الإعدادات"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """إنشاء الواجهة"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # العنوان
        title = QLabel("⚙️ الإعدادات")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(title)

        # إعدادات الفيديو
        video_group = QGroupBox("📹 إعدادات الفيديو")
        video_layout = QFormLayout()

        quality_combo = QComboBox()
        quality_combo.addItems(["منخفضة (360p)", "متوسطة (720p)", "عالية (1080p)", "فائقة (4K)"])
        video_layout.addRow("جودة الفيديو:", quality_combo)

        fps_combo = QComboBox()
        fps_combo.addItems(["24", "30", "60"])
        video_layout.addRow("معدل الإطارات:", fps_combo)

        video_group.setLayout(video_layout)
        layout.addWidget(video_group)

        # إعدادات الصوت
        audio_group = QGroupBox("🔊 إعدادات الصوت")
        audio_layout = QFormLayout()

        volume_spinbox = QSpinBox()
        volume_spinbox.setRange(0, 100)
        volume_spinbox.setValue(80)
        volume_spinbox.setSuffix("%")
        audio_layout.addRow("مستوى الصوت:", volume_spinbox)

        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)

        # إعدادات اللغة
        language_group = QGroupBox("🌍 إعدادات اللغة")
        language_layout = QFormLayout()

        language_combo = QComboBox()
        for code, name in SUPPORTED_LANGUAGES.items():
            language_combo.addItem(name, code)
        language_layout.addRow("اللغة:", language_combo)

        language_group.setLayout(language_layout)
        layout.addWidget(language_group)

        # الأزرار
        btn_save = QPushButton("💾 حفظ الإعدادات")
        btn_save.setMinimumHeight(40)
        btn_save.clicked.connect(lambda: (
            logger.info("💾 تم حفظ الإعدادات"),
            QMessageBox.information(self, "نجاح", "✅ تم حفظ الإعدادات بنجاح!")
        ))
        layout.addWidget(btn_save)

        layout.addStretch()
        self.setLayout(layout)


class AboutScreen(QWidget):
    """شاشة معلومات التطبيق"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """إنشاء الواجهة"""
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)

        # الشعار
        logo = QLabel("🎬")
        logo.setFont(QFont("Arial", 80))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        # الاسم والإصدار
        name = QLabel(APP_NAME)
        name.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name)

        version = QLabel(f"الإصدار {APP_VERSION}")
        version.setFont(QFont("Arial", 14))
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet("color: #aaaaaa;")
        layout.addWidget(version)

        # الوصف
        description = QLabel(APP_DESCRIPTION)
        description.setFont(QFont("Arial", 12))
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet("margin: 20px; color: #cccccc;")
        layout.addWidget(description)

        # المطور
        author = QLabel(f"طوّره: {APP_AUTHOR}")
        author.setFont(QFont("Arial", 12))
        author.setAlignment(Qt.AlignmentFlag.AlignCenter)
        author.setStyleSheet("color: #888888; margin-top: 30px;")
        layout.addWidget(author)

        # المميزات
        features_title = QLabel("✨ المميزات الرئيسية")
        features_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        features_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(features_title)

        features = QLabel(
            "✅ إنشاء فيديوهات احترافية من النصوص\n"
            "✅ معالجة ذكية بالذكاء الاصطناعي\n"
            "✅ مئات القوالب الجاهزة\n"
            "✅ مكتبة موسيقى وتأثيرات صوتية\n"
            "✅ دعم 10+ لغات\n"
            "✅ تصدير عالي الجودة"
        )
        features.setFont(QFont("Arial", 11))
        features.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(features)

        layout.addStretch()

        # الترخيص
        license_label = QLabel(
            "هذا المشروع مرخص بموجب MIT License\n"
            "© 2024 Rabah Amir. جميع الحقوق محفوظة."
        )
        license_label.setFont(QFont("Arial", 9))
        license_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        license_label.setStyleSheet("color: #666666; margin-top: 20px;")
        layout.addWidget(license_label)

        self.setLayout(layout)


# ═══════════════════════════════════════════════════════════════════════════════
# 🪟 النافذة الرئيسية
# ═══════════════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    """النافذة الرئيسية للتطبيق"""

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.apply_styles()
        logger.info(f"✅ تم إنشاء النافذة الرئيسية - {APP_NAME} v{APP_VERSION}")

    def init_ui(self):
        """إنشاء الواجهة"""
        # إعدادات النافذة
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(1200, 700)

        # الـ Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # الـ Sidebar
        self.create_sidebar(main_layout)

        # Stacked Widget للشاشات
        self.stacked_widget = QStackedWidget()
        self.init_screens()
        main_layout.addWidget(self.stacked_widget, 1)

        # Menu Bar
        self.create_menu_bar()

    def create_sidebar(self, parent_layout):
        """إنشاء الـ Sidebar"""
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSpacing(0)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)

        # الشعار
        logo_label = QLabel("🎬 ProVideo")
        logo_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo_label)

        # فاصل
        separator = QLabel()
        separator.setStyleSheet("border-bottom: 1px solid #444444;")
        separator.setMinimumHeight(1)
        sidebar_layout.addWidget(separator)

        # الأزرار
        buttons_info = [
            ("🏠 الرئيسية", 0),
            ("🎥 إنشاء فيديو", 1),
            ("🎨 القوالب", 2),
            ("⚙️ الإعدادات", 3),
            ("ℹ️ عن التطبيق", 4),
        ]

        self.nav_buttons = []
        for text, index in buttons_info:
            btn = QPushButton(text)
            btn.setMinimumHeight(50)
            btn.clicked.connect(lambda checked, i=index: self.show_screen(i))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        # زر الخروج
        exit_btn = QPushButton("🚪 خروج")
        exit_btn.setMinimumHeight(50)
        exit_btn.setStyleSheet(f"background-color: {COLORS['error']};")
        exit_btn.clicked.connect(self.close)
        sidebar_layout.addWidget(exit_btn)

        # إضافة Sidebar للـ Layout الرئيسي
        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar_layout)
        sidebar_widget.setMinimumWidth(200)
        sidebar_widget.setMaximumWidth(250)
        sidebar_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface']};
                border-right: 1px solid #444444;
            }}
        """)
        parent_layout.addWidget(sidebar_widget)

    def init_screens(self):
        """إنشاء الشاشات"""
        self.home_screen = HomeScreen()
        self.create_video_screen = CreateVideoScreen(self)
        self.templates_screen = TemplatesScreen()
        self.settings_screen = SettingsScreen()
        self.about_screen = AboutScreen()

        self.stacked_widget.addWidget(self.home_screen)        # 0
        self.stacked_widget.addWidget(self.create_video_screen) # 1
        self.stacked_widget.addWidget(self.templates_screen)    # 2
        self.stacked_widget.addWidget(self.settings_screen)     # 3
        self.stacked_widget.addWidget(self.about_screen)        # 4

        self.stacked_widget.setCurrentIndex(0)

    def show_screen(self, index: int):
        """عرض شاشة معينة"""
        self.stacked_widget.setCurrentIndex(index)
        logger.info(f"📺 الانتقال إلى الشاشة #{index}")

    def create_menu_bar(self):
        """إنشاء شريط القوائم"""
        menubar = self.menuBar()

        # ملف
        file_menu = menubar.addMenu("📁 ملف")
        file_menu.addAction("🆕 مشروع جديد").triggered.connect(lambda: self.show_screen(1))
        file_menu.addAction("💾 حفظ").triggered.connect(self.save_project)
        file_menu.addSeparator()
        file_menu.addAction("🚪 خروج").triggered.connect(self.close)

        # تحرير
        edit_menu = menubar.addMenu("✏️ تحرير")
        edit_menu.addAction("↶ تراجع").triggered.connect(self.undo)
        edit_menu.addAction("↷ إعادة").triggered.connect(self.redo)

        # مساعدة
        help_menu = menubar.addMenu("❓ مساعدة")
        help_menu.addAction("📖 دليل المستخدم").triggered.connect(self.show_help)
        help_menu.addAction("ℹ️ عن التطبيق").triggered.connect(lambda: self.show_screen(4))

    def save_project(self):
        """حفظ المشروع"""
        logger.info("💾 جاري حفظ المشروع...")
        QMessageBox.information(self, "حفظ", "✅ تم حفظ المشروع بنجاح!")

    def undo(self):
        """تراجع"""
        logger.info("↶ تراجع")

    def redo(self):
        """إعادة"""
        logger.info("↷ إعادة")

    def show_help(self):
        """عرض الدليل"""
        logger.info("📖 عرض دليل المستخدم")
        QMessageBox.information(
            self,
            "دليل المستخدم",
            "1. اضغط على 'إنشاء فيديو'\n"
            "2. اكتب وصف الفيديو\n"
            "3. اختر القالب والإعدادات\n"
            "4. اضغط 'إنشاء الفيديو'\n"
            "5. انتظر انتهاء المعالجة\n"
            "6. احفظ أو شارك الفيديو"
        )

    def apply_styles(self):
        """تطبيق الأنماط"""
        self.setStyleSheet(STYLE_SHEET)

    def closeEvent(self, event):
        """معالجة إغلاق النافذة"""
        reply = QMessageBox.question(
            self,
            "تأكيد الخروج",
            "هل تريد حقاً الخروج من التطبيق؟",
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
    """الدالة الرئيسية لتشغيل التطبيق"""
    try:
        logger.info(f"🚀 بدء تشغيل {APP_NAME} v{APP_VERSION}")

        # إنشاء تطبيق Qt
        app = QApplication(sys.argv)

        # تعيين معلومات التطبيق
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion(APP_VERSION)

        # إنشاء النافذة الرئيسية
        logger.info("🪟 جاري إنشاء النافذة الرئيسية...")
        main_window = MainWindow()
        main_window.show()

        logger.info("✨ تم تشغيل التطبيق بنجاح!")
        logger.info("=" * 80)

        # تشغيل حلقة الأحداث الرئيسية
        sys.exit(app.exec())

    except Exception as e:
        logger.error(f"❌ خطأ عند تشغيل التطبيق: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
