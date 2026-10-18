import flet as ft

class CursorControlPage(ft.Container):
    def __init__(self, mouse_controller):
        super().__init__()
        self.mouse_controller = mouse_controller
        self.expand = True
        self.padding = 30

        # Update sensitivity and deadzone values in the mouse controller based on user input
        def set_sens_x(level):
            val = level * 10.0
            self.mouse_controller.sensitivity_x = val
            text_sens_x.value = f"Horizontal Sensitivity (X): Level {level} (Value: {val})"
            self.update()

        def set_sens_y(level):
            val = level * 10.0
            self.mouse_controller.sensitivity_y = val
            text_sens_y.value = f"Vertical Speed (Y): Level {level} (Value: {val})"
            self.update()

        def set_deadzone(level):
            
            val = (level - 1) * 0.25 
            self.mouse_controller.deadzone_yaw = val
            self.mouse_controller.deadzone_pitch = val
            text_deadzone.value = f"Dead Zone (Stability): Level {level} (Value: {val:.2f}°)"
            self.update()
            
        def set_smoothing(level):
            
            val = level * 0.05
            self.mouse_controller.smoothing_factor = val
            text_smoothing.value = f"Smoothing (Smoothness): Level {level} (Value: {val:.2f})"
            self.update()

        # Button creation function for sensitivity, deadzone, and smoothing levels
        def create_level_buttons(action_func):
            buttons = []
            for i in range(1, 21):
                buttons.append(
                    ft.Button(
                        str(i), 
                        width=60,  # Button width
                        height= 60, # Button height
                        style=ft.ButtonStyle(
                            padding=0, 
                            shape=ft.RoundedRectangleBorder(radius=6),
                            bgcolor=ft.Colors.BLUE_50,
                            color=ft.Colors.BLUE_900
                        ),
                        
                        on_click=lambda e, level=i: action_func(level)
                    )
                )
            return ft.Row(buttons, wrap=True, spacing=5, run_spacing=5)


        # Text components to display current values
        text_sens_x = ft.Text(f"Horizontal Sensitivity (X): Current Value ({self.mouse_controller.sensitivity_x})", weight=ft.FontWeight.BOLD)
        text_sens_y = ft.Text(f"Vertical Sensitivity (Y): Current Value ({self.mouse_controller.sensitivity_y})", weight=ft.FontWeight.BOLD)
        text_deadzone = ft.Text(f"Dead Zone (Stability): Current Value ({self.mouse_controller.deadzone_yaw:.2f}°)", weight=ft.FontWeight.BOLD)
        text_smoothing = ft.Text(f"Smoothing (Smoothness): Current Value ({self.mouse_controller.smoothing_factor:.2f})", weight=ft.FontWeight.BOLD)

        #  Page content layout
        self.content = ft.Column([
            ft.Text("Cursor Control Settings", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("Select a level between 1 (Lowest) and 20 (Highest) to adjust sensitivity.", color=ft.Colors.GREY_600),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            
            # Speed and Sensitivity 
            
            ft.Container(
                content=ft.Column([
                    ft.Text("Speed and Sensitivity", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                    
                    text_sens_x,
                    create_level_buttons(set_sens_x), # Horizontal Sensitivity Buttons (1-20)
                    
                    ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                    
                    text_sens_y,
                    create_level_buttons(set_sens_y), # Vertical Sensitivity Buttons (1-20)
                ]),
                padding=25, bgcolor=ft.Colors.WHITE, border_radius=10,
                border=ft.Border(left=ft.BorderSide(4, ft.Colors.BLUE)),
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK_12)
            ),
            
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            
            # stability and filtering
            ft.Container(
                content=ft.Column([
                    ft.Text("Filtering and Stability", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_700),
                    
                    text_deadzone,
                    create_level_buttons(set_deadzone), # Dead Zone Buttons (1-20)
                    ft.Text("Prevents cursor tremor when looking straight ahead. (20 = Most sensitive)", size=12, color=ft.Colors.GREY_500),
                    
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    text_smoothing,
                    create_level_buttons(set_smoothing), # Smoothing Buttons (1-20)
                    ft.Text("Smoothing Factor: 1-Instant response, rigid.", size=12, color=ft.Colors.GREY_500),
                ]),
                padding=20, bgcolor=ft.Colors.WHITE, border_radius=10,
                border=ft.Border(left=ft.BorderSide(4, ft.Colors.ORANGE)),
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK_12)
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.START, scroll=ft.ScrollMode.AUTO)