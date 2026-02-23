"""
Steganography Tool
Hide and reveal secret messages in images using Pure Python LSB
Bilingual: English and Amharic
"""

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.app import App
from threading import Thread
import os
from datetime import datetime

# Use Pillow for image manipulation
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Constants for LSB encoding
TERMINATOR = "1111111111111110"  # 16-bit terminator sequence

Builder.load_string('''
<SteganographyScreen>:
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
        
        # Mode Selection
        BoxLayout:
            size_hint_y: 0.1
            spacing: 10
            
            ToggleButton:
                id: hide_mode
                text: ''
                group: 'mode'
                state: 'down'
                on_release: root.set_mode('hide')
                background_normal: ''
                background_color: (0.2, 0.6, 0.8, 1) if self.state == 'down' else (0.5, 0.5, 0.5, 1)
                color: 1, 1, 1, 1
            
            ToggleButton:
                id: reveal_mode
                text: ''
                group: 'mode'
                on_release: root.set_mode('reveal')
                background_normal: ''
                background_color: (0.2, 0.8, 0.2, 1) if self.state == 'down' else (0.5, 0.5, 0.5, 1)
                color: 1, 1, 1, 1
        
        # Image Selection
        BoxLayout:
            size_hint_y: 0.12
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
        
        # Message Input/Output (Hide Mode)
        BoxLayout:
            id: message_box
            size_hint_y: 0.2
            orientation: 'vertical'
            spacing: 5
            opacity: 1 if root.mode == 'hide' else 0
            
            Label:
                id: message_label
                text: ''
                font_size: '16sp'
                color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
                size_hint_y: 0.2
            
            TextInput:
                id: message_input
                size_hint_y: 0.8
                multiline: True
                text: ''
                hint_text: ''
                background_color: (0.2, 0.2, 0.2, 1) if app.dark_mode else (1, 1, 1, 1)
                foreground_color: (1, 1, 1, 1) if app.dark_mode else (0, 0, 0, 1)
                hint_text_color: (0.6, 0.6, 0.6, 1) if app.dark_mode else (0.5, 0.5, 0.5, 1)
        
        # Message Output (Reveal Mode)
        BoxLayout:
            id: output_box
            size_hint_y: 0.2
            orientation: 'vertical'
            spacing: 5
            opacity: 1 if root.mode == 'reveal' else 0
            
            Label:
                id: output_label
                text: ''
                font_size: '16sp'
                color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
                size_hint_y: 0.2
            
            TextInput:
                id: output_text
                size_hint_y: 0.8
                multiline: True
                text: root.revealed_message
                readonly: True
                background_color: (0.2, 0.2, 0.2, 1) if app.dark_mode else (1, 1, 1, 1)
                foreground_color: (1, 1, 1, 1) if app.dark_mode else (0, 0, 0, 1)
        
        # Action Button
        Button:
            id: action_btn
            text: ''
            size_hint_y: 0.1
            background_normal: ''
            background_color: (0.2, 0.8, 0.2, 1)
            color: 1, 1, 1, 1
            on_release: root.process()
            disabled: not root.can_process
        
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
        
        # Save Button (for Hide mode)
        Button:
            id: save_btn
            text: ''
            size_hint_y: 0.05
            background_normal: ''
            background_color: (0.4, 0.4, 0.8, 1)
            color: 1, 1, 1, 1
            on_release: root.save_stego_image()
            opacity: 1 if root.mode == 'hide' and root.stego_path else 0
            disabled: not root.stego_path
        
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

class SteganographyScreen(Screen):
    """Steganography Screen using Pure Python LSB method"""
    
    mode = StringProperty('hide')
    image_path = StringProperty('')
    stego_path = StringProperty('')
    revealed_message = StringProperty('')
    can_process = False
    is_processing = False
    progress_value = NumericProperty(0)
    progress_text = StringProperty('')
    current_lang = StringProperty('en')
    
    strings = {
        'en': {
            'steganography': 'Steganography',
            'hide': 'Hide Message',
            'reveal': 'Reveal Message',
            'select_image': 'Select Image:',
            'choose_image': 'Choose Image',
            'preview': 'Preview:',
            'enter_message': 'Enter Secret Message:',
            'message_hint': 'Type your secret message...',
            'hidden_message': 'Hidden Message:',
            'save_stego': 'Save Stego Image',
            'clear': 'Clear',
            'select_image_first': 'Please select an image first',
            'enter_message_first': 'Please enter a message to hide',
            'no_pil': 'Image processing not available. Install Pillow',
            'processing_hide': 'Hiding message in image...',
            'processing_reveal': 'Revealing hidden message...',
            'hide_complete': 'Message hidden successfully!',
            'reveal_complete': 'Message revealed successfully!',
            'no_message_found': 'No hidden message found in image',
            'error': 'Error processing image',
            'saved': 'Stego image saved successfully!',
            'save_error': 'Error saving image',
            'ready': 'Ready'
        },
        'am': {
            'steganography': 'ስውር መልእክት',
            'hide': 'መልእክት ደብቅ',
            'reveal': 'መልእክት አውጣ',
            'select_image': 'ምስል ይምረጡ:',
            'choose_image': 'ምስል ምረጥ',
            'preview': 'ቅድመ እይታ:',
            'enter_message': 'ሚስጥራዊ መልእክት ያስገቡ:',
            'message_hint': 'ሚስጥራዊ መልእክትዎን ይተይቡ...',
            'hidden_message': 'የተደበቀ መልእክት:',
            'save_stego': 'ስውር ምስል አስቀምጥ',
            'clear': 'አጽዳ',
            'select_image_first': 'እባክዎ መጀመሪያ ምስል ይምረጡ',
            'enter_message_first': 'እባክዎ ለመደበቅ መልእክት ያስገቡ',
            'no_pil': 'የምስል ማስኬጃ አይገኝም። Pillow ይጫኑ',
            'processing_hide': 'መልእክት በምስል ውስጥ በመደበቅ ላይ...',
            'processing_reveal': 'የተደበቀ መልእክት በማውጣት ላይ...',
            'hide_complete': 'መልእክት በተሳካ ሁኔታ ተደብቋል!',
            'reveal_complete': 'መልእክት በተሳካ ሁኔታ ተገልጧል!',
            'no_message_found': 'በምስል ውስጥ ምንም የተደበቀ መልእክት አልተገኘም',
            'error': 'ምስል በማስኬድ ላይ ስህተት',
            'saved': 'ስውር ምስል በተሳካ ሁኔታ ተቀምጧል!',
            'save_error': 'ምስል በማስቀመጥ ላይ ስህተት',
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
        self.update_can_process()
        
        # Bind text input changes
        self.ids.message_input.bind(text=self.on_text_change)
    
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
        self.ids.title_label.text = self.get_string('steganography')
        self.ids.hide_mode.text = self.get_string('hide')
        self.ids.reveal_mode.text = self.get_string('reveal')
        self.ids.select_label.text = self.get_string('select_image')
        self.ids.select_btn.text = self.get_string('choose_image')
        self.ids.preview_label.text = self.get_string('preview')
        self.ids.message_label.text = self.get_string('enter_message')
        self.ids.message_input.hint_text = self.get_string('message_hint')
        self.ids.output_label.text = self.get_string('hidden_message')
        self.ids.save_btn.text = self.get_string('save_stego')
        self.ids.clear_btn.text = self.get_string('clear')
        self.update_action_button()
    
    def update_action_button(self):
        if self.mode == 'hide':
            self.ids.action_btn.text = self.get_string('hide')
        else:
            self.ids.action_btn.text = self.get_string('reveal')
    
    def set_mode(self, mode):
        """Set current mode (hide/reveal)"""
        self.mode = mode
        self.update_action_button()
        self.update_can_process()
        
        # Clear reveal output when switching to hide
        if mode == 'hide':
            self.revealed_message = ''
            self.ids.output_text.text = ''
    
    def on_text_change(self, instance, value):
        """Update can_process when text changes"""
        self.update_can_process()
    
    def update_can_process(self):
        """Update whether process button should be enabled"""
        if self.mode == 'hide':
            self.can_process = bool(self.image_path and self.ids.message_input.text.strip())
        else:
            self.can_process = bool(self.image_path)
        
        self.ids.action_btn.disabled = not self.can_process
    
    def choose_image(self):
        """Open file chooser to select image"""
        from kivy.uix.filechooser import FileChooserListView
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical')
        filechooser = FileChooserListView(path=os.path.expanduser('~'), 
                                         filters=['*.png', '*.jpg', '*.jpeg', '*.bmp'])
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
                self.update_can_process()
            popup.dismiss()
        
        select_btn.bind(on_release=on_select)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()
    
    def process(self):
        """Process based on current mode"""
        if not self.image_path:
            self.show_popup(self.get_string('select_image_first'))
            return
        
        if self.mode == 'hide' and not self.ids.message_input.text.strip():
            self.show_popup(self.get_string('enter_message_first'))
            return
        
        if not PIL_AVAILABLE:
            self.show_popup(self.get_string('no_pil'))
            return
        
        self.is_processing = True
        self.ids.action_btn.disabled = True
        self.progress_value = 0
        
        if self.mode == 'hide':
            self.progress_text = self.get_string('processing_hide')
            Thread(target=self._hide_thread).start()
        else:
            self.progress_text = self.get_string('processing_reveal')
            Thread(target=self._reveal_thread).start()
    
    def _text_to_binary(self, text):
        """Convert text to binary string"""
        binary = ''
        for char in text:
            binary += format(ord(char), '08b')
        binary += TERMINATOR
        return binary
    
    def _binary_to_text(self, binary):
        """Convert binary string to text"""
        # Find terminator
        terminator_pos = binary.find(TERMINATOR)
        if terminator_pos == -1:
            return None
        
        binary = binary[:terminator_pos]
        
        # Convert binary to text
        text = ''
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            if len(byte) == 8:
                text += chr(int(byte, 2))
        
        return text
    
    def _encode_lsb(self, img_path, message, output_path):
        """Hide message in image using LSB"""
        # Open image
        img = Image.open(img_path)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        pixels = list(img.getdata())
        width, height = img.size
        
        # Convert message to binary
        binary_message = self._text_to_binary(message)
        message_len = len(binary_message)
        
        # Check if image can hold the message
        if message_len > len(pixels) * 3:
            raise Exception("Message too long for this image")
        
        # Encode message in LSBs
        encoded_pixels = []
        message_index = 0
        
        for pixel in pixels:
            r, g, b = pixel
            
            # Modify LSB of each channel if we still have message bits
            if message_index < message_len:
                r = (r & 0xFE) | int(binary_message[message_index])
                message_index += 1
            
            if message_index < message_len:
                g = (g & 0xFE) | int(binary_message[message_index])
                message_index += 1
            
            if message_index < message_len:
                b = (b & 0xFE) | int(binary_message[message_index])
                message_index += 1
            
            encoded_pixels.append((r, g, b))
        
        # Create new image
        encoded_img = Image.new('RGB', (width, height))
        encoded_img.putdata(encoded_pixels)
        encoded_img.save(output_path, 'PNG')
        
        return output_path
    
    def _decode_lsb(self, img_path):
        """Reveal message from image using LSB"""
        # Open image
        img = Image.open(img_path)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        pixels = list(img.getdata())
        
        # Extract LSBs
        binary_message = ''
        
        for pixel in pixels:
            r, g, b = pixel
            
            # Extract LSB from each channel
            binary_message += str(r & 1)
            binary_message += str(g & 1)
            binary_message += str(b & 1)
        
        # Convert binary to text
        return self._binary_to_text(binary_message)
    
    def _hide_thread(self):
        """Background thread for hiding message"""
        try:
            message = self.ids.message_input.text
            
            Clock.schedule_once(lambda dt: self._update_progress(30), 0)
            
            # Hide message in image
            temp_path = os.path.join(self.app.get_storage_path('images'), 'temp_stego.png')
            self._encode_lsb(self.image_path, message, temp_path)
            
            Clock.schedule_once(lambda dt: self._update_progress(100), 0)
            Clock.schedule_once(lambda dt: self._hide_complete(temp_path), 0)
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self._process_error(str(e)), 0)
    
    def _reveal_thread(self):
        """Background thread for revealing message"""
        try:
            Clock.schedule_once(lambda dt: self._update_progress(50), 0)
            
            # Reveal message from image
            message = self._decode_lsb(self.image_path)
            
            Clock.schedule_once(lambda dt: self._update_progress(100), 0)
            Clock.schedule_once(lambda dt: self._reveal_complete(message if message else ''), 0)
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self._process_error(str(e)), 0)
    
    def _update_progress(self, value):
        self.progress_value = value
    
    def _hide_complete(self, stego_path):
        self.stego_path = stego_path
        self.ids.preview_image.source = stego_path
        self.progress_text = self.get_string('hide_complete')
        self.is_processing = False
        self.ids.action_btn.disabled = False
        self.show_popup(self.get_string('hide_complete'))
    
    def _reveal_complete(self, message):
        if message:
            self.revealed_message = message
            self.ids.output_text.text = message
            self.progress_text = self.get_string('reveal_complete')
            self.show_popup(self.get_string('reveal_complete'))
        else:
            self.progress_text = self.get_string('no_message_found')
            self.show_popup(self.get_string('no_message_found'))
        
        self.is_processing = False
        self.ids.action_btn.disabled = False
    
    def _process_error(self, error):
        print(f"Steganography error: {error}")
        self.progress_text = self.get_string('error')
        self.is_processing = False
        self.ids.action_btn.disabled = False
        self.show_popup(self.get_string('error'))
    
    def save_stego_image(self):
        """Save stego image with user-friendly message"""
        if not self.stego_path:
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"stego_{timestamp}.png"
            save_path = os.path.join(self.app.get_storage_path('images'), filename)
            
            import shutil
            shutil.copy2(self.stego_path, save_path)
            
            friendly_message = f"✓ Saved in: eyoTools > Images\nFile: {filename}"
            self.show_popup(friendly_message)
            
        except Exception as e:
            self.show_popup(self.get_string('save_error'))
    
    def clear_all(self):
        """Clear all fields"""
        self.image_path = ''
        self.stego_path = ''
        self.revealed_message = ''
        self.ids.preview_image.source = ''
        self.ids.message_input.text = ''
        self.ids.output_text.text = ''
        self.progress_value = 0
        self.progress_text = ''
        self.is_processing = False
        self.update_can_process()
    
    def show_popup(self, message):
        """Show popup message"""
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
        """Return to home screen"""
        self.manager.current = 'home'