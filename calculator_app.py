"""
Calculator Application Module
Presents a modern, sleek CustomTkinter interface with support for:
- Modes: Standard, Scientific, Logic / Programmer
- History drawer with recall and clear capabilities
- Settings panel for themes, colors, angle units, precision, always-on-top
- Keyboard navigation and smooth animations
"""

import math
import customtkinter as ctk
from typing import Dict, Any, List

from calculator_engine import CalculatorEngine
from history_manager import HistoryManager
from settings_manager import SettingsManager


class CalculatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Managers & Engine
        self.settings_manager = SettingsManager()
        self.history_manager = HistoryManager()
        self.engine = CalculatorEngine(
            angle_unit=self.settings_manager.get("angle_unit", "DEG"),
            precision=self.settings_manager.get("precision", 10)
        )

        # Apply settings
        ctk.set_appearance_mode(self.settings_manager.get("appearance_mode", "dark"))
        ctk.set_default_color_theme(self.settings_manager.get("color_theme", "blue"))

        # Window setup
        self.title("Calculatrice Graphique Moderne - Ultra Calculator")
        self.geometry("850x600")
        self.minsize(750, 520)

        if self.settings_manager.get("always_on_top", False):
            self.attributes("-topmost", True)

        # State Variables
        self.current_expression = ""
        self.last_result = ""
        self.current_mode = self.settings_manager.get("default_mode", "Standard")
        self.angle_unit_var = ctk.StringVar(value=self.engine.angle_unit)
        self.memory = 0.0

        # UI Components Build
        self._build_layout()
        self._bind_keyboard()
        self.switch_mode(self.current_mode)

    def _build_layout(self):
        # Main Grid setup
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Sidebar (Navigation & Controls)
        self.sidebar_frame = ctk.CTkFrame(self, width=180, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        # Logo / Title in Sidebar
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="🧮 CALCULATRICE",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 20))

        # Mode Buttons
        self.btn_std = ctk.CTkButton(
            self.sidebar_frame,
            text="Standard",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
            command=lambda: self.switch_mode("Standard")
        )
        self.btn_std.grid(row=1, column=0, padx=15, pady=5, sticky="ew")

        self.btn_sci = ctk.CTkButton(
            self.sidebar_frame,
            text="Scientifique",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
            command=lambda: self.switch_mode("Scientific")
        )
        self.btn_sci.grid(row=2, column=0, padx=15, pady=5, sticky="ew")

        self.btn_logic = ctk.CTkButton(
            self.sidebar_frame,
            text="Logique / Prog",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
            command=lambda: self.switch_mode("Logic")
        )
        self.btn_logic.grid(row=3, column=0, padx=15, pady=5, sticky="ew")

        # Sidebar Divider
        self.divider = ctk.CTkFrame(self.sidebar_frame, height=2, fg_color="gray30")
        self.divider.grid(row=4, column=0, padx=15, pady=15, sticky="ew")

        # History & Settings Toggle Buttons
        self.btn_history = ctk.CTkButton(
            self.sidebar_frame,
            text="📜 Historique",
            fg_color="transparent",
            border_width=1,
            anchor="w",
            command=self.toggle_history_drawer
        )
        self.btn_history.grid(row=5, column=0, padx=15, pady=5, sticky="ew")

        self.btn_settings = ctk.CTkButton(
            self.sidebar_frame,
            text="⚙️ Paramètres",
            fg_color="transparent",
            border_width=1,
            anchor="w",
            command=self.open_settings_panel
        )
        self.btn_settings.grid(row=7, column=0, padx=15, pady=(5, 20), sticky="ew")

        # Main Calculator Center Frame
        self.main_container = ctk.CTkFrame(self, corner_radius=10)
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(2, weight=1)

        # Top Display Area (Screen)
        self.display_frame = ctk.CTkFrame(self.main_container, fg_color=("gray85", "gray15"), corner_radius=10)
        self.display_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        self.display_frame.grid_columnconfigure(0, weight=1)

        # Status Line (Angle Mode / Base Info)
        self.status_label = ctk.CTkLabel(
            self.display_frame,
            text=f"Mode: {self.current_mode} | Angle: {self.engine.angle_unit}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="gray60",
            anchor="e"
        )
        self.status_label.grid(row=0, column=0, padx=15, pady=(5, 0), sticky="ew")

        # Expression Entry / Display
        self.expr_label = ctk.CTkLabel(
            self.display_frame,
            text="",
            font=ctk.CTkFont(size=16),
            text_color="gray50",
            anchor="e"
        )
        self.expr_label.grid(row=1, column=0, padx=15, pady=(0, 0), sticky="ew")

        # Result Display Entry
        self.result_entry = ctk.CTkEntry(
            self.display_frame,
            font=ctk.CTkFont(size=32, weight="bold"),
            justify="right",
            border_width=0,
            fg_color="transparent"
        )
        self.result_entry.grid(row=2, column=0, padx=15, pady=(0, 10), sticky="ew")
        self.result_entry.insert(0, "0")

        # Angle Selection segmented button bar (visible in Scientific mode)
        self.angle_segmented = ctk.CTkSegmentedButton(
            self.main_container,
            values=["DEG", "RAD", "GRAD"],
            command=self.change_angle_unit
        )
        self.angle_segmented.set(self.engine.angle_unit)

        # Logic bases info bar (HEX, DEC, BIN, OCT)
        self.logic_bases_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.logic_bases_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.hex_label = ctk.CTkLabel(self.logic_bases_frame, text="HEX: 0x0", font=ctk.CTkFont(size=11, family="monospace"))
        self.hex_label.grid(row=0, column=0, padx=5, sticky="w")
        self.dec_label = ctk.CTkLabel(self.logic_bases_frame, text="DEC: 0", font=ctk.CTkFont(size=11, family="monospace"))
        self.dec_label.grid(row=0, column=1, padx=5, sticky="w")
        self.bin_label = ctk.CTkLabel(self.logic_bases_frame, text="BIN: 0b0", font=ctk.CTkFont(size=11, family="monospace"))
        self.bin_label.grid(row=0, column=2, padx=5, sticky="w")
        self.oct_label = ctk.CTkLabel(self.logic_bases_frame, text="OCT: 0o0", font=ctk.CTkFont(size=11, family="monospace"))
        self.oct_label.grid(row=0, column=3, padx=5, sticky="w")

        # Keypad Area Frame
        self.keypad_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.keypad_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=10)

        # History Drawer Side Panel (Initially hidden or on right)
        self.history_frame = ctk.CTkFrame(self, width=240, corner_radius=10)
        self.history_visible = False

    def change_angle_unit(self, value):
        self.engine.set_angle_unit(value)
        self.settings_manager.set("angle_unit", value)
        self.update_status_line()

    def update_status_line(self):
        self.status_label.configure(text=f"Mode: {self.current_mode} | Angle: {self.engine.angle_unit}")

    def switch_mode(self, mode: str):
        self.current_mode = mode
        self.update_status_line()

        # Update button highlights
        btn_fg = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        self.btn_std.configure(fg_color=btn_fg if mode == "Standard" else "transparent")
        self.btn_sci.configure(fg_color=btn_fg if mode == "Scientific" else "transparent")
        self.btn_logic.configure(fg_color=btn_fg if mode == "Logic" else "transparent")

        # Hide extra bars
        self.angle_segmented.grid_forget()
        self.logic_bases_frame.grid_forget()

        if mode == "Scientific":
            self.angle_segmented.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))
        elif mode == "Logic":
            self.logic_bases_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))

        self.render_keypad()

    def render_keypad(self):
        # Clear existing buttons in keypad_frame
        for child in self.keypad_frame.winfo_children():
            child.destroy()

        if self.current_mode == "Standard":
            self._render_standard_keypad()
        elif self.current_mode == "Scientific":
            self._render_scientific_keypad()
        elif self.current_mode == "Logic":
            self._render_logic_keypad()

    def _render_standard_keypad(self):
        buttons = [
            ["MC", "MR", "M+", "M-", "C", "⌫"],
            ["%", "(", ")", "1/x", "x²", "÷"],
            ["7", "8", "9", "×", "√x", "−"],
            ["4", "5", "6", "+", "±", "x³"],
            ["1", "2", "3", "=", "", ""],
            ["0", ".", "", "", "", ""]
        ]

        # Standard grid layout (5x4 primary keypad + memory row)
        grid_buttons = [
            ["MC", "MR", "M+", "M-", "C", "⌫"],
            ["(", ")", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "−"],
            ["1", "2", "3", "+"],
            ["±", "0", ".", "="]
        ]

        for r, row in enumerate(grid_buttons):
            self.keypad_frame.grid_rowconfigure(r, weight=1)
            for c, btn_text in enumerate(row):
                self.keypad_frame.grid_columnconfigure(c, weight=1)
                btn = self._create_calc_button(btn_text)
                btn.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")

    def _render_scientific_keypad(self):
        grid_buttons = [
            ["sin", "cos", "tan", "deg/rad", "C", "⌫"],
            ["asin", "acos", "atan", "π", "e", "÷"],
            ["x²", "x³", "x^y", "10^x", "√x", "×"],
            ["7", "8", "9", "(", ")", "−"],
            ["4", "5", "6", "ln", "log", "+"],
            ["1", "2", "3", "n!", "abs", "="],
            ["±", "0", ".", "1/x", "mod", ""]
        ]

        for r, row in enumerate(grid_buttons):
            self.keypad_frame.grid_rowconfigure(r, weight=1)
            for c, btn_text in enumerate(row):
                if not btn_text:
                    continue
                self.keypad_frame.grid_columnconfigure(c, weight=1)
                # Span equal button if last empty
                colspan = 2 if btn_text == "=" and c == 4 else 1
                btn = self._create_calc_button(btn_text)
                btn.grid(row=r, column=c, columnspan=colspan, padx=3, pady=3, sticky="nsew")

    def _render_logic_keypad(self):
        grid_buttons = [
            ["AND", "OR", "XOR", "NOT", "C", "⌫"],
            ["LSH", "RSH", "MOD", "(", ")", "÷"],
            ["A", "B", "7", "8", "9", "×"],
            ["C", "D", "4", "5", "6", "−"],
            ["E", "F", "1", "2", "3", "+"],
            ["HEX", "DEC", "BIN", "0", ".", "="]
        ]

        for r, row in enumerate(grid_buttons):
            self.keypad_frame.grid_rowconfigure(r, weight=1)
            for c, btn_text in enumerate(row):
                if not btn_text:
                    continue
                self.keypad_frame.grid_columnconfigure(c, weight=1)
                btn = self._create_calc_button(btn_text)
                btn.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")

    def _create_calc_button(self, text: str) -> ctk.CTkButton:
        # Determine styling by function
        fg_color = None
        hover_color = None
        text_color = None

        if text == "=":
            fg_color = ("#1f538d", "#2fa572")
            hover_color = ("#14375e", "#1e6f4c")
        elif text in ("C", "⌫"):
            fg_color = ("#d9534f", "#c9302c")
            hover_color = ("#c9302c", "#a02622")
        elif text in ("+", "−", "×", "÷", "AND", "OR", "XOR", "NOT", "LSH", "RSH", "MOD", "%"):
            fg_color = ("#e6e6e6", "#2b2b2b")
            hover_color = ("#d0d0d0", "#3a3a3a")
        elif text.isdigit() or text in (".", "±"):
            fg_color = ("#f9f9f9", "#333333")
            hover_color = ("#e5e5e5", "#444444")

        return ctk.CTkButton(
            self.keypad_frame,
            text=text,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color,
            corner_radius=8,
            command=lambda t=text: self.on_button_click(t)
        )

    def on_button_click(self, char: str):
        current_text = self.result_entry.get()

        if char == "C":
            self.current_expression = ""
            self.expr_label.configure(text="")
            self.result_entry.delete(0, "end")
            self.result_entry.insert(0, "0")
            self._update_logic_bases(0)
            return

        if char == "⌫":
            if len(current_text) > 1:
                self.result_entry.delete(len(current_text) - 1, "end")
            else:
                self.result_entry.delete(0, "end")
                self.result_entry.insert(0, "0")
            return

        if char == "=":
            expr = self.current_expression + current_text if self.current_expression else current_text
            self.calculate_result(expr)
            return

        # Trigonometric / Scientific quick action functions
        if char in ("sin", "cos", "tan", "asin", "acos", "atan", "log", "ln", "sqrt"):
            self.current_expression = f"{char}({current_text})"
            self.calculate_result(self.current_expression)
            return

        if char == "x²":
            self.current_expression = f"({current_text})^2"
            self.calculate_result(self.current_expression)
            return

        if char == "x³":
            self.current_expression = f"({current_text})^3"
            self.calculate_result(self.current_expression)
            return

        if char == "1/x":
            self.current_expression = f"1/({current_text})"
            self.calculate_result(self.current_expression)
            return

        if char == "√x":
            self.current_expression = f"sqrt({current_text})"
            self.calculate_result(self.current_expression)
            return

        if char == "10^x":
            self.current_expression = f"10^({current_text})"
            self.calculate_result(self.current_expression)
            return

        if char == "n!":
            self.current_expression = f"({current_text})!"
            self.calculate_result(self.current_expression)
            return

        if char == "abs":
            self.current_expression = f"abs({current_text})"
            self.calculate_result(self.current_expression)
            return

        if char == "±":
            if current_text.startswith("-"):
                self.result_entry.delete(0, 1)
            elif current_text != "0":
                self.result_entry.insert(0, "-")
            return

        if char in ("MC", "MR", "M+", "M-"):
            self.handle_memory(char)
            return

        if char == "deg/rad":
            new_unit = "RAD" if self.engine.angle_unit == "DEG" else ("GRAD" if self.engine.angle_unit == "RAD" else "DEG")
            self.change_angle_unit(new_unit)
            self.angle_segmented.set(new_unit)
            return

        # Operators
        if char in ("+", "−", "×", "÷", "x^y", "%", "AND", "OR", "XOR", "LSH", "RSH", "MOD"):
            op = "^" if char == "x^y" else char
            self.current_expression = f"{current_text} {op} "
            self.expr_label.configure(text=self.current_expression)
            self.result_entry.delete(0, "end")
            self.result_entry.insert(0, "0")
            return

        # Append digit or token
        if current_text == "0" and char not in (".", ")"):
            self.result_entry.delete(0, "end")
            self.result_entry.insert(0, char)
        else:
            self.result_entry.insert("end", char)

    def calculate_result(self, expression: str):
        try:
            res = self.engine.evaluate(expression)
            self.expr_label.configure(text=f"{expression} =")
            self.result_entry.delete(0, "end")
            self.result_entry.insert(0, str(res))

            # Add to history
            self.history_manager.add_entry(expression, str(res), self.current_mode)
            if self.history_visible:
                self.render_history_items()

            self._update_logic_bases(res)
            self.current_expression = ""
        except Exception as err:
            self.expr_label.configure(text=f"Erreur: {expression}")
            self.result_entry.delete(0, "end")
            self.result_entry.insert(0, str(err))

    def _update_logic_bases(self, value):
        try:
            val_int = int(float(value))
            self.hex_label.configure(text=f"HEX: {CalculatorEngine.to_hex(val_int)}")
            self.dec_label.configure(text=f"DEC: {val_int}")
            self.bin_label.configure(text=f"BIN: {CalculatorEngine.to_bin(val_int)}")
            self.oct_label.configure(text=f"OCT: {CalculatorEngine.to_oct(val_int)}")
        except Exception:
            self.hex_label.configure(text="HEX: -")
            self.dec_label.configure(text="DEC: -")
            self.bin_label.configure(text="BIN: -")
            self.oct_label.configure(text="OCT: -")

    def handle_memory(self, action: str):
        try:
            val = float(self.result_entry.get())
            if action == "MC":
                self.memory = 0.0
            elif action == "MR":
                self.result_entry.delete(0, "end")
                self.result_entry.insert(0, str(self.memory))
            elif action == "M+":
                self.memory += val
            elif action == "M-":
                self.memory -= val
        except ValueError:
            pass

    def toggle_history_drawer(self):
        if self.history_visible:
            self.history_frame.grid_forget()
            self.history_visible = False
        else:
            self.history_frame.grid(row=0, column=2, sticky="nsew", padx=(0, 15), pady=15)
            self.history_visible = True
            self.render_history_items()

    def render_history_items(self):
        for child in self.history_frame.winfo_children():
            child.destroy()

        # Header
        title = ctk.CTkLabel(self.history_frame, text="📜 Historique", font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(padx=10, pady=(10, 5), anchor="w")

        btn_clear = ctk.CTkButton(
            self.history_frame,
            text="Effacer tout",
            fg_color="transparent",
            border_width=1,
            height=24,
            font=ctk.CTkFont(size=11),
            command=self.clear_history
        )
        btn_clear.pack(padx=10, pady=(0, 10), fill="x")

        # Scrollable area
        scroll = ctk.CTkScrollableFrame(self.history_frame, width=200)
        scroll.pack(fill="both", expand=True, padx=5, pady=5)

        items = self.history_manager.get_history()
        if not items:
            lbl = ctk.CTkLabel(scroll, text="Aucun historique", text_color="gray50")
            lbl.pack(pady=20)
            return

        for item in items:
            item_card = ctk.CTkFrame(scroll, fg_color=("gray90", "gray20"), corner_radius=6)
            item_card.pack(fill="x", pady=4, padx=2)

            expr_lbl = ctk.CTkLabel(item_card, text=item['expression'], font=ctk.CTkFont(size=12), anchor="w")
            expr_lbl.pack(padx=8, pady=(4, 0), fill="x")

            res_lbl = ctk.CTkLabel(item_card, text=f"= {item['result']}", font=ctk.CTkFont(size=14, weight="bold"), anchor="e", text_color="#1f538d")
            res_lbl.pack(padx=8, pady=(0, 4), fill="x")

            # Click to recall expression or result
            item_card.bind("<Button-1>", lambda e, r=item['result']: self.recall_history(r))
            expr_lbl.bind("<Button-1>", lambda e, r=item['result']: self.recall_history(r))
            res_lbl.bind("<Button-1>", lambda e, r=item['result']: self.recall_history(r))

    def recall_history(self, val: str):
        self.result_entry.delete(0, "end")
        self.result_entry.insert(0, val)

    def clear_history(self):
        self.history_manager.clear_history()
        self.render_history_items()

    def open_settings_panel(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Paramètres - Calculator")
        dialog.geometry("380x420")
        dialog.transient(self)
        dialog.grab_set()

        lbl_title = ctk.CTkLabel(dialog, text="⚙️ Configuration", font=ctk.CTkFont(size=18, weight="bold"))
        lbl_title.pack(pady=15)

        # Appearance mode setting
        lbl_theme = ctk.CTkLabel(dialog, text="Thème d'affichage:")
        lbl_theme.pack(anchor="w", padx=20, pady=(10, 2))
        theme_opt = ctk.CTkOptionMenu(
            dialog,
            values=["dark", "light", "system"],
            command=self._change_theme
        )
        theme_opt.set(self.settings_manager.get("appearance_mode", "dark"))
        theme_opt.pack(fill="x", padx=20)

        # Precision setting
        lbl_prec = ctk.CTkLabel(dialog, text="Précision des décimales:")
        lbl_prec.pack(anchor="w", padx=20, pady=(15, 2))
        prec_slider = ctk.CTkSlider(
            dialog,
            from_=2,
            to=15,
            number_of_steps=13,
            command=self._change_precision
        )
        prec_slider.set(self.engine.precision)
        prec_slider.pack(fill="x", padx=20)

        # Always on top
        top_check = ctk.CTkCheckBox(
            dialog,
            text="Toujours au-dessus (Always on Top)",
            command=lambda: self._toggle_always_on_top(top_check.get())
        )
        if self.settings_manager.get("always_on_top", False):
            top_check.select()
        top_check.pack(anchor="w", padx=20, pady=20)

        # Close button
        btn_close = ctk.CTkButton(dialog, text="Fermer", command=dialog.destroy)
        btn_close.pack(pady=15)

    def _change_theme(self, val: str):
        ctk.set_appearance_mode(val)
        self.settings_manager.set("appearance_mode", val)

    def _change_precision(self, val: float):
        p = int(val)
        self.engine.set_precision(p)
        self.settings_manager.set("precision", p)

    def _toggle_always_on_top(self, val: int):
        is_top = bool(val)
        self.attributes("-topmost", is_top)
        self.settings_manager.set("always_on_top", is_top)

    def _bind_keyboard(self):
        self.bind("<Key>", self._on_key_press)

    def _on_key_press(self, event):
        char = event.char
        keysym = event.keysym

        if keysym == "Return":
            self.on_button_click("=")
        elif keysym == "BackSpace":
            self.on_button_click("⌫")
        elif keysym == "Escape":
            self.on_button_click("C")
        elif char in "0123456789.+-*/()":
            if char == "*":
                self.on_button_click("×")
            elif char == "/":
                self.on_button_click("÷")
            elif char == "-":
                self.on_button_click("−")
            else:
                self.on_button_click(char)
