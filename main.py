
import hjson
import os
import sys
import subprocess
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.core.window import Window

Window.size=(1000,500)

BASE_KEY_SIZE =14  # Size of a 1U key in pixels

class KeyboardLayout(FloatLayout):
    def __init__(self, keymap_file, qmk_dir, keycode_file, keycode_extra_file, **kwargs):
        super(KeyboardLayout, self).__init__(**kwargs)
        self.layer = 0

        # Load keymap and info from files
        with open(keymap_file, 'r') as file:
            self.keymap_data = hjson.load(file)

        keyboard = self.keymap_data['keyboard']
        info_file = f"{qmk_dir}/keyboards/{keyboard}/info.json"

        with open(info_file, 'r') as file:
            self.info_data = hjson.load(file)

        with open(keycode_file, 'r') as file:
            self.keycode_data = hjson.load(file)

        with open(keycode_extra_file, 'r') as file:
            self.keycode_extra = hjson.load(file)

        self.render_layout()

    def get_keylabel(self, keycode):
        prefix = None
        keylabel = None
        if '(' in keycode:
            prefix = keycode.split('(')[0]
            keycode = keycode.split('(')[1].split(')')[0]
            if keycode in ["0", "1", "2", "3", "4"]:
                keylabel = int(keycode)

        for key, v in self.keycode_data['keycodes'].items():
            if v['key'] == keycode:
                keylabel = v['label']
                break
            if 'aliases' in v.keys():
                if keycode in v['aliases']:
                    keylabel = v['label']
                    break
        if not keylabel:
            for key, v in self.keycode_extra['aliases'].items():
                if v['key'] == keycode:
                    keylabel = v['label']
                    break
                if 'aliases' in v.keys():
                    if keycode in v['aliases']:
                        keylabel = v['label']
                        break
        if prefix:
            return f"{prefix}\n({keylabel})"
        if not keylabel and keycode != "KC_NO":
            return keycode
        return keylabel

    def render_layout(self, layer=0):
        layout_name = self.keymap_data['layout']
        # layout_name = "LAYOUT_split_3x6_3"
        layout_info = self.info_data["layouts"][layout_name]["layout"]

        keys = self.keymap_data['layers'][layer]
        for idx, key_info in enumerate(layout_info):
            x, y, w, h = key_info["x"], key_info["y"], key_info.get('w', 1), key_info.get('h', 1)

            keylabel = self.get_keylabel(keys[idx])
            
            btn = Button(
                text=keylabel,
                color=(1,1,1,1),
                halign='center',
                font_size="12dp",
                size_hint=(w/BASE_KEY_SIZE, h/BASE_KEY_SIZE),
                pos_hint={'x': x/BASE_KEY_SIZE, 'y': 1 - (y + h) / BASE_KEY_SIZE},
                on_release=self.switch_layout
            )
            self.add_widget(btn)           

    def clear_layout(self):
        self.clear_widgets()

    def switch_layout(self, *args):
        if self.layer + 1 < len(self.keymap_data['layers']):
            self.layer += 1
        else:
            self.layer = 0
        self.clear_widgets()
        self.render_layout(layer=self.layer)

class KeyboardApp(App):
    def __init__(self, keymap_file="", **kwargs):
        super(KeyboardApp, self).__init__(**kwargs)
        self.keymap_file = keymap_file
        # Get qmk directory with qmk env command

        self.run()

    def build(self):
        qmk_dir = subprocess.check_output(['qmk', 'env']).decode('utf-8').split('\n')[0].split(' ')[-1]
        qmk_dir = qmk_dir.replace('"', '').split('=')[1]
        keycode_file = os.path.join(qmk_dir, 'data', 'constants', 'keycodes', 'keycodes_0.0.1_basic.hjson')
        keycode_extra_file = os.path.join(qmk_dir, 'data', 'constants', 'keycodes', 'extras', 'keycodes_us_0.0.1.hjson')
        return KeyboardLayout(
            keymap_file=self.keymap_file,
            qmk_dir=qmk_dir,
            keycode_file=keycode_file,
            keycode_extra_file=keycode_extra_file)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please provide a keymap file")
        sys.exit(1)

    keymap_file = sys.argv[1]
    # app.run()

    app = KeyboardApp(keymap_file=keymap_file)
