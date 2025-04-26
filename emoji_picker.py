'''
from tkinter import *
from styles import Styles

class EmojiPicker:
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        self.styles = Styles(parent.winfo_toplevel())
        
        self.popup = Toplevel(parent)
        self.popup.configure(bg=self.styles.bg_light, bd=1)
        self.popup.wm_overrideredirect(True)
        self.popup.attributes('-topmost', True)
        self.popup.lift()

        # Proper position above input or anywhere
        btn_x = parent.winfo_rootx() + parent.winfo_width() - 300
        btn_y = parent.winfo_rooty() - 160
        self.popup.geometry(f"250x200+{btn_x}+{btn_y}")  # Height increased for scroll

        # Canvas and scrollbar inside Toplevel
        self.canvas = Canvas(self.popup, bg=self.styles.bg_light, highlightthickness=0)
        self.scrollbar = Scrollbar(self.popup, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Scrollable frame inside the canvas
        self.scroll_frame = Frame(self.canvas, bg=self.styles.bg_light)
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw", tags="scroll_window")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig("scroll_window", width=e.width))


        # Pack everything
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        
        # Title for emoji picker
        Label(
            self.scroll_frame,
            text="Emojis",
            bg=self.styles.bg_light,
            fg=self.styles.text_secondary,
            font=self.styles.font_small
        ).grid(row=0, column=0, columnspan=5, sticky="w", padx=5, pady=2)
        
        # Popular emoji categories in more compact 5-column grid
        emoji_groups = [
            # Smileys
            "😀 😃 😄 😁 😆",
            "😅 😂 🤣 😊 😇",
            # Face-with-hand
            "🙂 🙃 😉 😌 😍",
            "😘 😗 😙 😚 😋",
            # Face-with-tongue
            "😛 😝 😜 🤪 🤨",
            "🧐 🤓 😎 🤩 🥳",
            # Face-neutral-skeptical
            "😏 😒 😞 😔 😟",
            "😕 🙁 😣 😖 😫",
            # Hands
            "👍 👎 👌 🤝 👏",
            "🙌 🤲 👐 🙏 💪",
            # Hearts
            "❤️ 🧡 💛 💚 💙",
            "💜 🖤 🤍 💯 💢"
        ]
        
        # Display first 2 rows by default (10 emojis)
        visible_groups = emoji_groups[:4]  # Show 4 rows (20 emojis) in the default view
        
        # Display emojis in 5-column grid with proper sizing
        for row, emoji_row in enumerate(visible_groups, start=1):
            emojis = emoji_row.split()
            for col, emoji_char in enumerate(emojis):
                btn = Button(
                    self.scroll_frame,
                    text=emoji_char,
                    font=("Segoe UI Emoji", 14),  # Reduced font size for better fit
                    bg=self.styles.bg_light,
                    fg=self.styles.text_primary,
                    borderwidth=0,
                    padx=3,  # Reduced padding
                    pady=3,  # Reduced padding
                    width=2,  # Fixed width
                    height=1,  # Fixed height
                    command=lambda e=emoji_char: self.select_emoji(e)
                )
                btn.grid(row=row, column=col, padx=2, pady=2)
        
        # Show more button
        self.show_more_btn = Button(
            self.scroll_frame,
            text="More...",
            font=self.styles.font_small,
            bg=self.styles.bg_light,
            fg=self.styles.accent,
            borderwidth=0,
            command=lambda: self.show_more_emojis(emoji_groups)
        )
        self.show_more_btn.grid(row=len(visible_groups)+1, column=0, columnspan=5, pady=3)
        
        # Close button
        close_btn = Button(
            self.scroll_frame,
            text="×",
            font=self.styles.font_bold,
            bg=self.styles.bg_light,
            fg=self.styles.text_secondary,
            borderwidth=0,
            command=self.close
        )
        close_btn.grid(row=0, column=4, sticky="e", padx=5)
        
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

    
    def show_more_emojis(self, emoji_groups):
        # Remove the "More..." button
        self.show_more_btn.destroy()
        
        # Add the rest of the emoji groups
        for row, emoji_row in enumerate(emoji_groups[4:], start=5):  # Continue from row 5
            emojis = emoji_row.split()
            for col, emoji_char in enumerate(emojis):
                btn = Button(
                    self.scroll_frame,
                    text=emoji_char,
                    font=("Segoe UI Emoji", 14),
                    bg=self.styles.bg_light,
                    fg=self.styles.text_primary,
                    borderwidth=0,
                    padx=3,
                    pady=3,
                    width=2,
                    height=1,
                    command=lambda e=emoji_char: self.select_emoji(e)
                )
                btn.grid(row=row, column=col, padx=2, pady=2)
        
        # Update scrollregion
        self.scroll_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
    
    def select_emoji(self, emoji_char):
        self.callback(emoji_char)
        self.close()
    
    def close(self):
        self.popup.destroy()
'''

from tkinter import *
from styles import Styles

class EmojiPicker:
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        self.styles = Styles(parent.winfo_toplevel())

        self.current_group_index = 0
        self.emoji_groups = [
            "😀 😃 😄 😁 😆",
            "😅 😂 🤣 😊 😇",
            "🙂 🙃 😉 😌 😍",
            "😘 😗 😙 😚 😋",
            "😛 😝 😜 🤪 🤨",
            "🧐 🤓 😎 🤩 🥳",
            "😏 😒 😞 😔 😟",
            "😕 🙁 😣 😖 😫",
            "👍 👎 👌 🤝 👏",
            "🙌 🤲 👐 🙏 💪",
            "❤️ 🧡 💛 💚 💙",
            "💜 🖤 🤍 💯 💢"
        ]

        self.popup = Toplevel(parent)
        self.popup.configure(bg=self.styles.bg_light, bd=1)
        self.popup.wm_overrideredirect(True)
        self.popup.attributes('-topmost', True)
        self.popup.lift()

        x = parent.winfo_rootx() + parent.winfo_width() - 300
        y = parent.winfo_rooty() - 160
        self.popup.geometry(f"250x200+{x}+{y}")

        self.container = Frame(self.popup, bg=self.styles.bg_light)
        self.container.pack(expand=True, fill="both")

        Label(
            self.container,
            text="Emojis",
            bg=self.styles.bg_light,
            fg=self.styles.text_secondary,
            font=self.styles.font_small
        ).pack(pady=(5, 0))

        self.emoji_frame = Frame(self.container, bg=self.styles.bg_light)
        self.emoji_frame.pack(pady=5)

        nav_frame = Frame(self.container, bg=self.styles.bg_light)
        nav_frame.pack()

        self.prev_btn = Button(
            nav_frame, text="←", command=self.prev_group,
            font=self.styles.font_bold, bg=self.styles.bg_medium,
            fg=self.styles.text_primary, width=3
        )
        self.prev_btn.grid(row=0, column=0, padx=5)

        self.next_btn = Button(
            nav_frame, text="→", command=self.next_group,
            font=self.styles.font_bold, bg=self.styles.bg_medium,
            fg=self.styles.text_primary, width=3
        )
        self.next_btn.grid(row=0, column=1, padx=5)

        close_btn = Button(
            self.container, text="×", command=self.close,
            font=self.styles.font_bold, bg=self.styles.bg_light,
            fg=self.styles.text_secondary, borderwidth=0
        )
        close_btn.pack(pady=2)

        self.render_emojis()

    def render_emojis(self):
        for widget in self.emoji_frame.winfo_children():
            widget.destroy()

        emojis = self.emoji_groups[self.current_group_index].split()
        for i, emoji_char in enumerate(emojis):
            btn = Button(
                self.emoji_frame,
                text=emoji_char,
                font=("Segoe UI Emoji", 14),
                bg=self.styles.bg_light,
                fg=self.styles.text_primary,
                borderwidth=0,
                padx=3, pady=3, width=2, height=1,
                command=lambda e=emoji_char: self.select_emoji(e)
            )
            btn.grid(row=0, column=i, padx=2, pady=2)

    def next_group(self):
        self.current_group_index = (self.current_group_index + 1) % len(self.emoji_groups)
        self.render_emojis()

    def prev_group(self):
        self.current_group_index = (self.current_group_index - 1) % len(self.emoji_groups)
        self.render_emojis()

    def select_emoji(self, emoji_char):
        self.callback(emoji_char)
        self.close()

    def close(self):
        self.popup.destroy()