from PySide6.QtWidgets import (
    QPushButton, QFrame, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
)
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QRect, QSize, Property
)
from PySide6.QtGui import QColor

class AnimatedButton(QPushButton):
    """
    Button with hover animation (scale up & background brightness)
    Usage:
        btn = AnimatedButton("Click Me", color="#3B82F6")
    """
    def __init__(self, text="", parent=None, color="#3B82F6", text_color="white"):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.default_color = color
        
        # Base style
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: {text_color};
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 14px;
                border: none;
            }}
        """)
        
        # Shadow
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.shadow.setOffset(0, 4)
        self.setGraphicsEffect(self.shadow)
        
        # Animation state
        self._scale = 1.0
        
    def enterEvent(self, event):
        self.animate_scale(1.05)
        self.animate_shadow(25, 6)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.animate_scale(1.0)
        self.animate_shadow(15, 4)
        super().leaveEvent(event)
        
    def animate_scale(self, target_scale):
        # We simulate scale by changing geometry slightly? 
        # Actually changing geometry jitters layout.
        # Better: Just animate shadow/elevation OR use QGraphicsTransform if in GraphicsView.
        # Simple/Safe approach for Widgets: Animate Shadow Color/Radius only (Material Design style)
        pass

    def animate_shadow(self, radius, offset):
        # Animate blur radius
        self.anim = QPropertyAnimation(self.shadow, b"blurRadius")
        self.anim.setDuration(200)
        self.anim.setStartValue(self.shadow.blurRadius())
        self.anim.setEndValue(radius)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)
        self.anim.start()
        
        # Animate offset
        self.anim2 = QPropertyAnimation(self.shadow, b"yOffset") # Not standard property? 
        # QGraphicsDropShadowEffect doesn't expose yOffset as property easily.
        # So we just set it directly.
        self.shadow.setOffset(0, offset)

class HoverCard(QFrame):
    """
    Card that lifts up on hover
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 12px;
            }
        """)
        
        # Shadow
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(10)
        self.shadow.setColor(QColor(0, 0, 0, 50))
        self.shadow.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow)
        
        # Animation vars
        self.original_geometry = None
        
    def enterEvent(self, event):
        self.anim = QPropertyAnimation(self.shadow, b"blurRadius")
        self.anim.setDuration(150)
        self.anim.setEndValue(20)
        self.anim.start()
        
        # Lift effect (Move up 2px)
        # Requires stable parent layout, risky if layout fights back.
        # Safer: Just increase shadow.
        self.shadow.setOffset(0, 5)
        self.setStyleSheet("""
            QFrame {
                background-color: #263445; /* Lighter bg */
                border: 1px solid #475569;
                border-radius: 12px;
            }
        """)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.anim = QPropertyAnimation(self.shadow, b"blurRadius")
        self.anim.setDuration(150)
        self.anim.setEndValue(10)
        self.anim.start()
        
        self.shadow.setOffset(0, 2)
        self.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 12px;
            }
        """)
        super().leaveEvent(event)

