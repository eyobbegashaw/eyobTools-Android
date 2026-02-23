"""
Background Remover Tool
Remove image backgrounds using PIL-based approach (no OpenCV required)
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
from PIL import Image, ImageFilter, ImageOps

# No OpenCV needed!

STRINGS = {
    'en': {
        'bg_remover': 'Background Remover',
        'select_image': 'Select Image:',
        'choose_image': 'Choose Image',
        'preview': 'Preview:',
        'remove_bg': 'Remove Background',
        'result': 'Result:',
        'save': 'Save Image',
        'clear': 'Clear All',
        'processing': 'Processing image...',
        'processing_step1': 'Loading image...',
        'processing_step2': 'Analyzing image edges...',
        'processing_step3': 'Creating transparency...',
        'processing_step4': 'Refining edges...',
        'complete': 'Background removed successfully!',
        'error': 'Error processing image',
        'select_image_first': 'Please select an image first',
        'saved': 'Image saved successfully!',
        'save_error': 'Error saving image',
        'ready': 'Ready',
        'select_image_prompt': 'Select an image to begin',
        'tap_to_keep': 'Tap on areas to keep',
        'tap_to_remove': 'Tap on areas to remove'
    },
    'am': {
        'bg_remover': 'ዳራ አስወጋጅ',
        'select_image': 'ምስል ይምረጡ:',
        'choose_image': 'ምስል ምረጥ',
        'preview': 'ቅድመ እይታ:',
        'remove_bg': 'ዳራ አስወግድ',
        'result': 'ውጤት:',
        'save': 'ምስል አስቀምጥ',
        'clear': 'ሁሉንም አጽዳ',
        'processing': 'ምስል በማስኬድ ላይ...',
        'processing_step1': 'ምስል በመጫን ላይ...',
        'processing_step2': 'የምስል ጠርዞች በመተንተን ላይ...',
        'processing_step3': 'ግልጽነት በመፍጠር ላይ...',
        'processing_step4': 'ጠርዞች በማጣራት ላይ...',
        'complete': 'ዳራ በተሳካ ሁኔታ ተወግዷል!',
        'error': 'ምስል በማስኬድ ላይ ስህተት',
        'select_image_first': 'እባክዎ መጀመሪያ ምስል ይምረጡ',
        'saved': 'ምስል በተሳካ ሁኔታ ተቀምጧል!',
        'save_error': 'ምስል በማስቀመጥ ላይ ስህተት',
        'ready': 'ዝግጁ',
        'select_image_prompt': 'ለመጀመር ምስል ይምረጡ',
        'tap_to_keep': 'ማስቀመጥ የሚፈልጉትን ቦታ ይንኩ',
        'tap_to_remove': 'ማስወገድ የሚፈልጉትን ቦታ ይንኩ'
    }
}

Builder.load_string('''
<BackgroundRemoverScreen>:
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
        
        # Image Selection Section
        BoxLayout:
            size_hint_y: 0.12
            orientation: 'vertical'
            spacing: 5
            
            Label:
                id: select_label
                text: ''
                font_size: '14sp'
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
        
        # Image Preview Section
        BoxLayout:
            size_hint_y: 0.3
            orientation: 'vertical'
            spacing: 5
            
            Label:
                id: preview_label
                text: ''
                font_size: '14sp'
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
        
        # Process Button
        Button:
            id: process_btn
            text: ''
            size_hint_y: 0.08
            background_normal: ''
            background_color: (0.2, 0.8, 0.2, 1)
            color: 1, 1, 1, 1
            on_release: root.process_image()
            disabled: not root.image_path or root.is_processing
        
        # Progress Section
        BoxLayout:
            size_hint_y: 0.12
            orientation: 'vertical'
            spacing: 5
            
            Label:
                id: progress_label
                text: root.progress_text
                size_hint_y: 0.3
                font_size: '12sp'
                color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
            
            ProgressBar:
                id: progress_bar
                value: root.progress_value
                max: 100
                size_hint_y: 0.4
            
            Label:
                id: status_label
                text: root.status_text
                size_hint_y: 0.3
                font_size: '12sp'
                color: (0.7, 0.7, 0.7, 1) if app.dark_mode else (0.4, 0.4, 0.4, 1)
        
        # Result Preview (after processing)
        BoxLayout:
            size_hint_y: 0.3
            orientation: 'vertical'
            spacing: 5
            opacity: 1 if root.result_path else 0
            
            Label:
                id: result_label
                text: ''
                font_size: '14sp'
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
                    id: result_image
                    source: root.result_path if root.result_path else ''
                    allow_stretch: True
                    keep_ratio: True
        
        # Save Button
        Button:
            id: save_btn
            text: ''
            size_hint_y: 0.05
            background_normal: ''
            background_color: (0.4, 0.4, 0.8, 1)
            color: 1, 1, 1, 1
            on_release: root.save_image()
            opacity: 1 if root.result_path else 0
            disabled: not root.result_path
        
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

class BackgroundRemoverScreen(Screen):
    """Background Remover Screen using PIL-based approach (no OpenCV)"""
    
    # Properties
    image_path = StringProperty('')
    result_path = StringProperty('')
    is_processing = False
    progress_value = NumericProperty(0)
    progress_text = StringProperty('')
    status_text = StringProperty('')
    current_lang = StringProperty('en')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
    
    def on_pre_enter(self):
        """Called before screen enters"""
        self.app = App.get_running_app()
        self.current_lang = self.app.current_lang
        self.update_ui_language()
        self.update_fonts()
        self.status_text = self.get_string('select_image_prompt')
    
    def on_enter(self):
        """Called when screen enters"""
        self.update_ui_language()
        self.update_fonts()
    
    def update_fonts(self):
        """Update font for all widgets based on current language"""
        if not self.app:
            return
        
        font_name = 'Abyssinica' if self.app.current_lang == 'am' and self.app.FONT_REGISTERED else 'Roboto'
        
        # Update all labels and buttons with the appropriate font
        for widget in self.walk():
            if hasattr(widget, 'font_name'):
                widget.font_name = font_name
    
    def get_string(self, key):
        """Get string in current language"""
        if self.app and hasattr(self.app, 'current_lang'):
            return STRINGS[self.app.current_lang].get(key, STRINGS['en'].get(key, key))
        return STRINGS['en'].get(key, key)
    
    def update_ui_language(self):
        """Update all UI text elements based on language"""
        self.ids.title_label.text = self.get_string('bg_remover')
        self.ids.select_label.text = self.get_string('select_image')
        self.ids.select_btn.text = self.get_string('choose_image')
        self.ids.preview_label.text = self.get_string('preview')
        self.ids.process_btn.text = self.get_string('remove_bg')
        self.ids.result_label.text = self.get_string('result')
        self.ids.save_btn.text = self.get_string('save')
        self.ids.clear_btn.text = self.get_string('clear')
        
        # Update progress and status texts if they exist
        if self.progress_text:
            self.progress_text = self.get_string('processing')
        if self.status_text:
            self.status_text = self.get_string('select_image_prompt')
    
    def choose_image(self):
        """Open file chooser to select image"""
        from kivy.uix.filechooser import FileChooserListView
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical')
        filechooser = FileChooserListView(path=os.path.expanduser('~'), 
                                         filters=['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif'])
        content.add_widget(filechooser)
        
        btn_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        select_btn = Button(text=self.get_string('choose_image'))
        cancel_btn = Button(text='Cancel' if self.app.current_lang == 'en' else 'ሰርዝ')
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(title=self.get_string('select_image'), 
                     content=content, 
                     size_hint=(0.9, 0.9))
        
        def on_select(instance):
            if filechooser.selection:
                self.image_path = filechooser.selection[0]
                self.ids.preview_image.source = self.image_path
                self.status_text = self.get_string('ready')
            popup.dismiss()
        
        select_btn.bind(on_release=on_select)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()
    
    def process_image(self):
        """Remove background from image using PIL-based approach"""
        if not self.image_path:
            self.show_popup(self.get_string('select_image_first'))
            return
        
        self.is_processing = True
        self.ids.process_btn.disabled = True
        self.progress_value = 0
        self.progress_text = self.get_string('processing')
        self.status_text = self.get_string('processing_step1')
        
        # Run in thread to avoid blocking UI
        Thread(target=self._process_thread).start()
    
    def _remove_background_pil(self, image):
        """
        Remove background using PIL-based techniques
        This is a simplified approach that works well for objects with distinct edges
        """
        # Convert to RGBA if not already
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Get image data
        datas = image.getdata()
        
        # Create a new image with transparency
        new_data = []
        
        # Get the background color from corners (assume corners are background)
        width, height = image.size
        
        # Sample colors from corners
        corners = [
            image.getpixel((0, 0)),           # Top-left
            image.getpixel((width-1, 0)),      # Top-right
            image.getpixel((0, height-1)),      # Bottom-left
            image.getpixel((width-1, height-1)) # Bottom-right
        ]
        
        # Calculate average background color
        bg_r = sum(c[0] for c in corners) // 4
        bg_g = sum(c[1] for c in corners) // 4
        bg_b = sum(c[2] for c in corners) // 4
        
        # Threshold for color similarity
        threshold = 60
        
        # Process each pixel
        for item in datas:
            r, g, b, a = item
            
            # Check if pixel is similar to background color
            if (abs(r - bg_r) < threshold and 
                abs(g - bg_g) < threshold and 
                abs(b - bg_b) < threshold):
                # Make transparent
                new_data.append((r, g, b, 0))
            else:
                # Keep original
                new_data.append((r, g, b, a))
        
        # Create new image with transparency
        image.putdata(new_data)
        
        # Apply edge enhancement to clean up
        image = image.filter(ImageFilter.EDGE_ENHANCE)
        
        return image
    
    def _remove_background_advanced(self, image):
        """
        Advanced background removal using edge detection and masking
        """
        # Convert to RGBA
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Create a grayscale version for edge detection
        gray = image.convert('L')
        
        # Find edges
        edges = gray.filter(ImageFilter.FIND_EDGES)
        
        # Apply a threshold to edges
        edge_data = edges.getdata()
        edge_threshold = 50
        
        # Create a mask based on edges
        width, height = image.size
        mask = Image.new('L', (width, height), 0)
        mask_data = []
        
        for value in edge_data:
            if value > edge_threshold:
                mask_data.append(255)  # Edge pixel - keep
            else:
                mask_data.append(0)    # Non-edge - might be background
        
        mask.putdata(mask_data)
        
        # Dilate the mask to include areas near edges
        mask = mask.filter(ImageFilter.MaxFilter(3))
        
        # Apply the mask to the original image
        result = Image.new('RGBA', image.size, (0, 0, 0, 0))
        result.paste(image, mask=mask)
        
        return result
    
    def _process_thread(self):
        """Background processing thread using PIL"""
        try:
            # Update progress
            Clock.schedule_once(lambda dt: self._update_progress(20, self.get_string('processing_step1')), 0)
            
            # Open image with PIL
            image = Image.open(self.image_path)
            
            Clock.schedule_once(lambda dt: self._update_progress(40, self.get_string('processing_step2')), 0)
            
            # Try advanced method first, fall back to simple if it fails
            try:
                result_image = self._remove_background_advanced(image)
            except:
                result_image = self._remove_background_pil(image)
            
            Clock.schedule_once(lambda dt: self._update_progress(70, self.get_string('processing_step3')), 0)
            
            # Further refine (optional)
            result_image = result_image.filter(ImageFilter.SMOOTH_MORE)
            
            Clock.schedule_once(lambda dt: self._update_progress(90, self.get_string('processing_step4')), 0)
            
            # Save temporary file
            temp_dir = self.app.get_storage_path('images')
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, 'temp_output.png')
            result_image.save(temp_path, 'PNG')
            
            Clock.schedule_once(lambda dt: self._process_complete(temp_path), 0)
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self._process_error(str(e)), 0)
    
    def _update_progress(self, value, text):
        """Update progress display"""
        self.progress_value = value
        self.status_text = text
    
    def _process_complete(self, result_path):
        """Handle processing completion"""
        self.result_path = result_path
        self.ids.result_image.source = result_path
        self.progress_value = 100
        self.progress_text = self.get_string('complete')
        self.status_text = self.get_string('complete')
        self.is_processing = False
        self.ids.process_btn.disabled = False
        self.show_popup(self.get_string('complete'))
    
    def _process_error(self, error):
        """Handle processing error"""
        self.progress_text = self.get_string('error')
        self.status_text = self.get_string('error')
        self.is_processing = False
        self.ids.process_btn.disabled = False
        self.show_popup(self.get_string('error') + f"\n{error}")
    
    def save_image(self):
        """Save processed image with user-friendly message"""
        if not self.result_path:
            return
        
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"output_{timestamp}.png"
            save_path = os.path.join(self.app.get_storage_path('images'), filename)
            
            # Copy file
            import shutil
            shutil.copy2(self.result_path, save_path)
            
            # User-friendly message
            friendly_message = f"✓ Saved in: eyoTools > Images\nFile: {filename}"
            self.show_popup(friendly_message)
            
        except Exception as e:
            self.show_popup(self.get_string('save_error'))
    
    def clear_all(self):
        """Clear all fields"""
        self.image_path = ''
        self.result_path = ''
        self.ids.preview_image.source = ''
        self.ids.result_image.source = ''
        self.progress_value = 0
        self.progress_text = ''
        self.status_text = self.get_string('select_image_prompt')
        self.is_processing = False
    
    def show_popup(self, message):
        """Show popup message"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Set font for label based on language
        label = Label(text=message, text_size=(self.width * 0.7, None), halign='center')
        if self.app and self.app.current_lang == 'am' and self.app.FONT_REGISTERED:
            label.font_name = 'Abyssinica'
        content.add_widget(label)
        
        btn_text = 'OK' if self.app.current_lang == 'en' else 'እሺ'
        btn = Button(text=btn_text, size_hint_y=0.3)
        if self.app and self.app.current_lang == 'am' and self.app.FONT_REGISTERED:
            btn.font_name = 'Abyssinica'
        content.add_widget(btn)
        
        popup_title = 'Message' if self.app.current_lang == 'en' else 'መልእክት'
        popup = Popup(title=popup_title, content=content, size_hint=(0.8, 0.4))
        btn.bind(on_release=popup.dismiss)
        popup.open()
    
    def go_back(self):
        """Return to home screen"""
        self.manager.current = 'home'
