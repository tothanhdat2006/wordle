from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, Line
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
import random
import math

from gacha import Gacha

class GachaBox(BoxLayout):
    """Individual box in the gacha animation"""
    def __init__(self, item_type, item_name, rarity_color, func, **kwargs):
        """
        Args:
            item_type (str): 'Bless' or 'Curse'
            item_name (str): Name of the gacha item
            rarity_color (tuple): RGBA color tuple for the box background
        """
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (None, 1)
        self.width = 150
        self.padding = 10
        self.spacing = 5
        
        self.item_type = item_type
        self.item_name = item_name
        self.rarity_color = rarity_color
        self.func = None
        
        with self.canvas.before:
            Color(rarity_color)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        icon = 'Bless' if item_type == 'Bless' else 'Curse'
        self.type_label = Label(
            text=f'[size=48sp]{icon}[/size]',
            markup=True,
            size_hint_y=0.5
        )
        
        self.name_label = Label(
            text=f'[b]{item_name}[/b]',
            markup=True,
            font_size='14sp',
            size_hint_y=0.3
        )
        
        self.add_widget(self.type_label)
        self.add_widget(self.name_label)
    
    def update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class GachaAnimationScreen(Screen):
    """Screen that shows the CSGO-style gacha animation"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.gacha_system = Gacha()
        self.gacha_items = [
            # Bless items (60% total)
            {'type': 'Bless', 'name': 'Remove Curse', 'func': self.gacha_system.remove_curse, 'weight': 0.4, 'color': (0.4, 0.7, 1.0, 1)},
            {'type': 'Bless', 'name': 'Add Tries', 'func': self.gacha_system.add_tries, 'weight': 0.19, 'color': (0.5, 0.8, 1.0, 1)},
            {'type': 'Bless', 'name': 'Instant Win', 'func': self.gacha_system.win_game, 'weight': 0.01, 'color': (1.0, 0.84, 0.0, 1)},

            # Curse items (40% total)
            {'type': 'Curse', 'name': 'Add Curse', 'func': self.gacha_system.add_curse, 'weight': 0.4, 'color': (0.8, 0.2, 0.2, 1)},
            {'type': 'Curse', 'name': 'Remove Tries', 'func': self.gacha_system.remove_tries, 'weight': 0.19, 'color': (0.6, 0.1, 0.1, 1)},
            {'type': 'Curse', 'name': 'Instant Lose', 'func': self.gacha_system.lose_game, 'weight': 0.01, 'color': (0.3, 0.0, 0.0, 1)},
        ]
        self.result_func = None
        self.setup_ui()
    
    def setup_ui(self):
        """
        Setup the UI elements
        """
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        with main_layout.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            self.main_bg = Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self.update_main_bg, size=self.update_main_bg)
        
        title = Label(
            text='[b][size=36sp]GACHA BOX OPENING[/size][/b]',
            markup=True,
            size_hint_y=0.1
        )
        main_layout.add_widget(title)
        
        self.animation_container = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.6
        )
        
        with self.animation_container.canvas:
            Color(1, 1, 0, 0.8)
            self.selector_line = Line(
                points=[0, 0, 0, 0],
                width=3
            )
        
        self.animation_container.bind(pos=self.update_selector, size=self.update_selector)
        
        # Scrollable container for gacha boxes
        self.scroll_container = BoxLayout(
            orientation='horizontal',
            size_hint=(None, 1),
            spacing=10
        )
        self.scroll_container.width = 0
        
        self.animation_container.add_widget(self.scroll_container)
        main_layout.add_widget(self.animation_container)
        
        self.result_label = Label(
            text='Press "Open Box" to start!',
            font_size='20sp',
            markup=True,
            size_hint_y=0.15
        )
        main_layout.add_widget(self.result_label)
        
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.15,
            spacing=20,
            padding=[100, 0]
        )
        
        self.open_button = Button(
            text='OPEN BOX',
            font_size='20sp',
            bold=True,
            background_color=(0.3, 0.7, 0.3, 1)
        )
        self.open_button.bind(on_press=self.start_animation)
        
        back_button = Button(
            text='BACK',
            font_size='20sp',
            bold=True,
            background_color=(0.7, 0.3, 0.3, 1)
        )
        back_button.bind(on_press=self.go_back_game_screen)
        
        button_layout.add_widget(self.open_button)
        button_layout.add_widget(back_button)
        main_layout.add_widget(button_layout)
        
        self.add_widget(main_layout)
    
    def update_main_bg(self, instance, value):
        self.main_bg.pos = instance.pos
        self.main_bg.size = instance.size
    
    def update_selector(self, *args):
        """
        Update the selector line position
        """
        center_x = self.animation_container.x + self.animation_container.width / 2
        bottom_y = self.animation_container.y
        top_y = self.animation_container.y + self.animation_container.height
        self.selector_line.points = [center_x, bottom_y, center_x, top_y]
    
    def generate_boxes(self):
        """
        Generate boxes for the animation with random items
        """
        self.scroll_container.clear_widgets()
        
        total_boxes = 50
        
        for _ in range(total_boxes):
            item = random.choices(
                self.gacha_items,
                weights=[it['weight'] for it in self.gacha_items],
                k=1
            )[0]
            
            box = GachaBox(
                item_type=item['type'],
                item_name=item['name'],
                rarity_color=item['color'],
                func=item['func']
            )
            box.item_data = item
            self.scroll_container.add_widget(box)
        
        total_width = (150 + 10) * total_boxes
        self.scroll_container.width = total_width
        
        self.initial_x = self.animation_container.center_x - 75
        
    
    def start_animation(self, *args):
        self.open_button.disabled = True
        self.result_label.text = 'Opening box...'
        
        self.generate_boxes()
        
        self.scroll_container.x = self.initial_x

        box_width = 160  # 10 for spacing
        min_boxes = 10
        max_boxes = 40
        random_boxes_to_scroll = random.uniform(min_boxes, max_boxes)
        
        random_offset = random.uniform(-box_width/2, box_width/2)
        scroll_distance = random_boxes_to_scroll * box_width + random_offset
        self.final_x = self.initial_x - scroll_distance # final position of the scroll container
        
        # Fast scroll (2.5 seconds)
        anim1 = Animation(
            x=self.final_x + box_width,
            duration=2.5,
            t='in_cubic'
        )
        
        # Slow down (2.5 seconds)
        anim2 = Animation(
            x=self.final_x,
            duration=2.5,
            t='out_quad'
        )
        
        anim1.bind(on_complete=lambda *x: anim2.start(self.scroll_container))
        anim2.bind(on_complete=lambda *x: self.reveal_result())

        anim1.start(self.scroll_container)
    
    def get_winning_box(self):
        """
        Find which box is closest to the center selector line
        """
        center_x = self.animation_container.center_x
        
        closest_box = None
        min_distance = float('inf')
        
        for box in self.scroll_container.children[::-1]: # Reverse to get left-to-right order
            box_center_x = box.x + box.width / 2
            distance = abs(box_center_x - center_x)
            
            if distance < min_distance:
                min_distance = distance
                closest_box = box
        
        return closest_box
    
    def reveal_result(self):
        """
        Reveal the final result by finding the box at the center
        """
        winning_box = self.get_winning_box()
        
        if winning_box:
            winning_item = winning_box.item_data
            icon = 'Bless' if winning_item['type'] == 'Bless' else 'Curse'
            color = '6ac764' if winning_item['type'] == 'Bless' else 'ff6b6b'
            
            self.result_label.text = (
                f'[b][size=24sp]You got: {icon} '
                f'[color={color}]{winning_item["name"]}[/color]![/size][/b]'
            )
            self.result_func = winning_item['func']
        
        self.open_button.disabled = False
    
    def go_back_game_screen(self, *args):
        game_screen = self.manager.get_screen('game_screen')
        
        # Apply the gacha result if one exists
        if self.result_func:
            game_screen.apply_gacha_result(self.result_func)
            self.result_func = None # reset
        
        self.manager.current = 'game_screen'


class GachaAnimationDemo(BoxLayout):
    """Standalone demo for testing"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        screen = GachaAnimationScreen()
        self.add_widget(screen)
