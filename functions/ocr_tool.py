"""
OCR Tool - Image to Text
Extract text from images using Tesseract OCR
Bilingual: English and Amharic
"""

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty
from kivy.app import App
from threading import Thread
import os
from datetime import datetime

# Try to import pytesseract
try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

Builder.load_string('''
<OCRScreen>:
    canvas:
        Color:
            rgba: (0.1, 0.1, 0.1, 1) if app.dark_mode else (0.95, 0.95, 0.95, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        spacing: 10
        padding: 15
        
        # Top Bar
        BoxLayout:
            size_hint_y: 0.1
            spacing: 10
            
            Button:
                text: '←'
                font_size: '24sp'
                size_hint_x: 0.15
                background_normal: ''
                background_color: (0.3, 0.3, 0.3, 1)
                color: 1, 1, 1, 1
                on_release: root.go_back()
            
            Label:
                id: title_label
                text: ''
                font_size: '20sp'
                bold: True
                color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
                size_hint_x: 0.7
                text_size: self.size
                halign: 'center'
                valign: 'middle'
            
            BoxLayout:
                size_hint_x: 0.15
        
        # Image Selection
        BoxLayout:
            size_hint_y: 0.15
            orientation: 'vertical'
            spacing: 5
            
            Label:
                id: select_label
                text: ''
                font_size: '16sp'
                color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
                size_hint_y: 0.3
                text_size: self.size
                halign: 'left'
                valign: 'middle'
            
            Button:
                id: select_btn
                text: ''
                size_hint_y: 0.7
                background_normal: ''
                background_color: (0.2, 0.6, 0.8, 1)
                color: 1, 1, 1, 1
                on_release: root.choose_image()
        
        # Image Preview
        BoxLayout:
            size_hint_y: 0.25
            orientation: 'vertical'
            spacing: 5
            
            Label:
                id: preview_label
                text: ''
                font_size: '16sp'
                color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
                size_hint_y: 0.1
            
            BoxLayout:
                size_hint_y: 0.9
                canvas:
                    Color:
                        rgba: (0.2, 0.2, 0.2, 1) if app.dark_mode else (0.8, 0.8, 0.8, 1)
                    Rectangle:
                        pos: self.pos
                        size: self.size
                
                Image:
                    id: preview_image
                    source: root.image_path if root.image_path else ''
                    allow_stretch: True
                    keep_ratio: True
        
        # Language Selection
        BoxLayout:
            size_hint_y: 0.12
            orientation: 'vertical'
            spacing: 5
            
            Label:
                id: lang_label
                text: ''
                font_size: '16sp'
                color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
                size_hint_y: 0.3
            
            Spinner:
                id: lang_spinner
                size_hint_y: 0.7
                text: 'English'
                values: ['English', 'አማርኛ']
                on_text: root.on_language_select(self.text)
                background_color: (0.2, 0.2, 0.2, 1) if app.dark_mode else (1, 1, 1, 1)
                color: (1, 1, 1, 1) if app.dark_mode else (0, 0, 0, 1)
        
        # Extract Button
        Button:
            id: extract_btn
            text: ''
            size_hint_y: 0.1
            background_normal: ''
            background_color: (0.2, 0.8, 0.2, 1)
            color: 1, 1, 1, 1
            on_release: root.extract_text()
            disabled: not root.image_path or root.is_processing
        
        # Progress Section
        BoxLayout:
            size_hint_y: 0.1
            orientation: 'vertical'
            spacing: 5
            
            Label:
                id: progress_label
                text: root.progress_text
                size_hint_y: 0.4
                color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
            
            ProgressBar:
                id: progress_bar
                value: root.progress_value
                max: 100
                size_hint_y: 0.6
        
        # Extracted Text
        BoxLayout:
            size_hint_y: 0.3
            orientation: 'vertical'
            spacing: 5
            
            Label:
                id: result_label
                text: ''
                font_size: '16sp'
                color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
                size_hint_y: 0.1
            
            TextInput:
                id: extracted_text
                text: root.extracted_text
                readonly: True
                background_color: (0.2, 0.2, 0.2, 1) if app.dark_mode else (1, 1, 1, 1)
                foreground_color: (1, 1, 1, 1) if app.dark_mode else (0, 0, 0, 1)
                size_hint_y: 0.9
        
        # Action Buttons
        BoxLayout:
            size_hint_y: 0.1
            spacing: 10
            
            Button:
                id: save_btn
                text: ''
                background_normal: ''
                background_color: (0.4, 0.4, 0.8, 1)
                color: 1, 1, 1, 1
                on_release: root.save_text()
                disabled: not root.extracted_text
            
            Button:
                id: copy_btn
                text: ''
                background_normal: ''
                background_color: (0.6, 0.6, 0.6, 1)
                color: 1, 1, 1, 1
                on_release: root.copy_text()
                disabled: not root.extracted_text
        
        # Clear Button
        Button:
            id: clear_btn
            text: ''
            size_hint_y: 0.05
            background_normal: ''
            background_color: (0.6, 0.6, 0.6, 1)
            color: 1, 1, 1, 1
            on_release: root.clear_all()
''')

class OCRScreen(Screen):
    """OCR Screen for text extraction from images"""
    
    image_path = StringProperty('')
    extracted_text = StringProperty('')
    is_processing = False
    progress_value = NumericProperty(0)
    progress_text = StringProperty('')
    status_text = StringProperty('')
    current_lang = StringProperty('en')
    selected_lang = 'eng'
    
    strings = {
        'en': {
            'ocr': 'Image to Text',
            'select_image': 'Select Image:',
            'choose_image': 'Choose Image',
            'preview': 'Preview:',
            'select_lang': 'Select Language:',
            'extract': 'Extract Text',
            'extracted_text': 'Extracted Text:',
            'save': 'Save as TXT',
            'copy': 'Copy',
            'clear': 'Clear',
            'select_image_first': 'Please select an image first',
            'no_tesseract': 'OCR not available. Install pytesseract',
            'processing': 'Processing image...',
            'complete': 'Text extraction complete!',
            'error': 'Error extracting text',
            'saved': 'Text saved successfully!',
            'save_error': 'Error saving text',
            'copied': 'Text copied to clipboard!',
            'copy_error': 'Error copying text',
            'ready': 'Ready'
        },
        'am': {
            'ocr': 'ምስል ወደ ጽሁፍ',
            'select_image': 'ምስል ይምረጡ:',
            'choose_image': 'ምስል ምረጥ',
            'preview': 'ቅድመ እይታ:',
            'select_lang': 'ቋንቋ ይምረጡ:',
            'extract': 'ጽሁፍ አውጣ',
            'extracted_text': 'የተወጣ ጽሁፍ:',
            'save': 'እንደ TXT አስቀምጥ',
            'copy': 'ቅዳ',
            'clear': 'አጽዳ',
            'select_image_first': 'እባክዎ መጀመሪያ ምስል ይምረጡ',
            'no_tesseract': 'OCR አይገኝም። pytesseract ይጫኑ',
            'processing': 'ምስል በማስኬድ ላይ...',
            'complete': 'ጽሁፍ ማውጣት ተጠናቋል!',
            'error': 'ጽሁፍ በማውጣት ላይ ስህተት',
            'saved': 'ጽሁፍ በተሳካ ሁኔታ ተቀምጧል!',
            'save_error': 'ጽሁፍ በማስቀመጥ ላይ ስህተት',
            'copied': 'ጽሁፍ ወደ ክሊፕቦርድ ተቀድቷል!',
            'copy_error': 'ጽሁፍ በመቅዳት ላይ ስህተት',
            'ready': 'ዝግጁ'
        }
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
    
    def on_pre_enter(self):
        self.app = App.get_running_app()
        self.current_lang = self.app.current_lang
        self.update_ui_language()
        self.update_fonts()
    
    def on_enter(self):
        self.update_ui_language()
        self.update_fonts()
    
    def update_fonts(self):
        """Update font for all widgets based on current language"""
        if not self.app:
            return
        
        font_name = 'Abyssinica' if self.app.current_lang == 'am' and self.app.FONT_REGISTERED else 'Roboto'
        
        for widget in self.walk():
            if hasattr(widget, 'font_name'):
                widget.font_name = font_name
    
    def get_string(self, key, default=''):
        return self.strings[self.current_lang].get(key, default)
    
    def update_ui_language(self):
        self.ids.title_label.text = self.get_string('ocr')
        self.ids.select_label.text = self.get_string('select_image')
        self.ids.select_btn.text = self.get_string('choose_image')
        self.ids.preview_label.text = self.get_string('preview')
        self.ids.lang_label.text = self.get_string('select_lang')
        self.ids.extract_btn.text = self.get_string('extract')
        self.ids.result_label.text = self.get_string('extracted_text')
        self.ids.save_btn.text = self.get_string('save')
        self.ids.copy_btn.text = self.get_string('copy')
        self.ids.clear_btn.text = self.get_string('clear')
    
    def on_language_select(self, text):
        if text == 'አማርኛ':
            self.selected_lang = 'amh'
        else:
            self.selected_lang = 'eng'
    
    def choose_image(self):
        from kivy.uix.filechooser import FileChooserListView
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical')
        filechooser = FileChooserListView(path=os.path.expanduser('~'), 
                                         filters=['*.png', '*.jpg', '*.jpeg'])
        content.add_widget(filechooser)
        
        btn_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        select_btn = Button(text=self.get_string('choose_image'))
        cancel_btn = Button(text='Cancel' if self.app.current_lang == 'en' else 'ሰርዝ')
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(title=self.get_string('select_image'), content=content, size_hint=(0.9, 0.9))
        
        def on_select(instance):
            if filechooser.selection:
                self.image_path = filechooser.selection[0]
                self.ids.preview_image.source = self.image_path
            popup.dismiss()
        
        select_btn.bind(on_release=on_select)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()
    
    def extract_text(self):
        if not self.image_path:
            self.show_popup(self.get_string('select_image_first'))
            return
        
        if not TESSERACT_AVAILABLE:
            self.show_popup(self.get_string('no_tesseract'))
            return
        
        self.is_processing = True
        self.ids.extract_btn.disabled = True
        self.progress_value = 0
        self.progress_text = self.get_string('processing')
        
        Thread(target=self._extract_thread).start()
    
    def _extract_thread(self):
        try:
            Clock.schedule_once(lambda dt: self._update_progress(30), 0)
            
            # Open and process image
            image = Image.open(self.image_path)
            
            Clock.schedule_once(lambda dt: self._update_progress(60), 0)
            
            # Perform OCR
            text = pytesseract.image_to_string(image, lang=self.selected_lang)
            
            Clock.schedule_once(lambda dt: self._extract_complete(text.strip()), 0)
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self._extract_error(str(e)), 0)
    
    def _update_progress(self, value):
        self.progress_value = value
    
    def _extract_complete(self, text):
        self.extracted_text = text
        self.ids.extracted_text.text = text
        self.progress_value = 100
        self.progress_text = self.get_string('complete')
        self.is_processing = False
        self.ids.extract_btn.disabled = False
        self.show_popup(self.get_string('complete'))
    
    def _extract_error(self, error):
        self.progress_text = self.get_string('error')
        self.is_processing = False
        self.ids.extract_btn.disabled = False
        self.show_popup(self.get_string('error'))
    
    def save_text(self):
        """Save extracted text with user-friendly message"""
        if not self.extracted_text:
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"ocr_{timestamp}.txt"
            save_path = os.path.join(self.app.get_storage_path('downloads'), filename)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(self.extracted_text)
            
            friendly_message = f"✓ Saved in: eyoTools > Downloads\nFile: {filename}"
            self.show_popup(friendly_message)
        except:
            self.show_popup(self.get_string('save_error'))
    
    def copy_text(self):
        from kivy.core.clipboard import Clipboard
        try:
            Clipboard.copy(self.extracted_text)
            self.show_popup(self.get_string('copied'))
        except:
            self.show_popup(self.get_string('copy_error'))
    
    def clear_all(self):
        self.image_path = ''
        self.extracted_text = ''
        self.ids.preview_image.source = ''
        self.ids.extracted_text.text = ''
        self.progress_value = 0
        self.progress_text = ''
    
    def show_popup(self, message):
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        label = Label(text=message)
        if self.app.current_lang == 'am' and self.app.FONT_REGISTERED:
            label.font_name = 'Abyssinica'
        content.add_widget(label)
        
        btn = Button(text='OK', size_hint_y=0.3)
        if self.app.current_lang == 'am' and self.app.FONT_REGISTERED:
            btn.font_name = 'Abyssinica'
        content.add_widget(btn)
        
        popup = Popup(title='Message', content=content, size_hint=(0.8, 0.4))
        btn.bind(on_release=popup.dismiss)
        popup.open()
    
    def go_back(self):
        self.manager.current = 'home'