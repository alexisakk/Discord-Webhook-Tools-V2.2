import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import requests
import queue
from io import BytesIO
from PIL import Image, ImageTk
import tkinter.font

stop_spam_flag = threading.Event()

def create_gui():
    root = tk.Tk()
    root.title("Discord Webhook Tools v2.2 by soul [BETA]")
    root.geometry("700x600")
    root.configure(bg="#2f3136")
    root.iconbitmap("assets/neww.ico")

        # Discord colors
    discord_blue = "#5865F2"
    dark_gray = "#555555"

    # Title text and settings
    title_text = "Discord Webhook Tools"
    font_name = "Segoe UI"
    font_size = 28
    font_weight = "bold"

    canvas = tk.Canvas(root, width=700, height=60, bg="#2f3136", highlightthickness=0)
    canvas.pack(pady=(20, 10))

    letters = []
    font_obj = tk.font.Font(family=font_name, size=font_size, weight=font_weight)

    total_width = sum([font_obj.measure(char) for char in title_text]) + (len(title_text) - 1) * 5
    start_x = (700 - total_width) / 2

    x = start_x
    y = 30
    for char in title_text:
        item = canvas.create_text(x, y, text=char, fill=dark_gray, font=(font_name, font_size, font_weight), anchor="w")
        letters.append(item)
        x += font_obj.measure(char) + 5

    # Gradient colors from dark_gray to discord_blue
    gradient_steps = [
        "#555555", "#6069A8", "#6C74B7", "#7880C6",
        "#848BCC", "#9097DB", "#9CA2E4", "#A8ADEB", "#5865F2"
    ]

    num_letters = len(title_text)
    grad_len = len(gradient_steps)

    def animate(step=0):
        for i, letter_id in enumerate(letters):
            color_pos = (i - step) % (num_letters + grad_len)
            if 0 <= color_pos < grad_len:
                color = gradient_steps[color_pos]
            else:
                color = dark_gray
            canvas.itemconfig(letter_id, fill=color)
        root.after(100, lambda: animate((step + 1) % (num_letters + grad_len)))

    animate()

    # Style
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(".", background="#2f3136", foreground="#ffffff", font=("Segoe UI", 10))
    style.configure("TEntry", fieldbackground="#40444b", background="#40444b", foreground="#ffffff", relief="flat")
    style.configure("TLabel", background="#2f3136", foreground="#ffffff")
    style.configure("TButton", background="#7289da", foreground="#ffffff", font=("Segoe UI", 10, "bold"), padding=6)
    style.map("TButton",
              background=[("active", "#5865f2"), ("!active", "#7289da")],
              foreground=[("!disabled", "#ffffff")])

    status_queue = queue.Queue()

    def post_status(text):
        status_queue.put(text)

    def update_status():
        try:
            while True:
                status_label.config(text=status_queue.get_nowait())
        except queue.Empty:
            pass
        root.after(100, update_status)

    def create_input_row(parent, label, widget):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=4)
        ttk.Label(frame, text=label).pack(anchor="w")
        widget.pack(fill="x", padx=2)
        return widget

    def create_input_row(parent, label, widget):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=4)
        ttk.Label(frame, text=label).pack(anchor="w")
        widget.pack(fill="x", padx=2)
        return widget

    input_frame = ttk.Frame(root)
    input_frame.pack(padx=30, pady=10, fill="both")

    webhook_entry = create_input_row(input_frame, "Webhook URL:", ttk.Entry(input_frame))
    message_text = create_input_row(input_frame, "Message:", tk.Text(input_frame, height=4, bg="#40444b", fg="white", insertbackground="white", relief="flat", wrap="word"))

    spam_count_entry = create_input_row(input_frame, "Spam Count:", ttk.Entry(input_frame))
    delay_entry = create_input_row(input_frame, "Delay (seconds):", ttk.Entry(input_frame))
    name_entry = create_input_row(input_frame, "Bot Name (Optional):", ttk.Entry(input_frame))
    avatar_entry = create_input_row(input_frame, "Bot Avatar URL (Optional):", ttk.Entry(input_frame))

    spam_count_entry.insert(0, "10")
    delay_entry.insert(0, "0.5")

    status_label = ttk.Label(root, text="Status: Idle", background="#2f3136", foreground="white", font=("Segoe UI", 10, "italic"))
    status_label.pack(pady=5)

    def post_status(text):
        status_label.config(text=f"Status: {text}")

    def spam_webhook_thread(url, message, count, delay, name, avatar):
        for i in range(count):
            if stop_spam_flag.is_set():
                post_status("Spamming stopped.")
                return
            try:
                data = {"content": message}
                if name: data["username"] = name
                if avatar: data["avatar_url"] = avatar
                response = requests.post(url, json=data)
                response.raise_for_status()
                post_status(f"Sent message {i+1}/{count}")
            except Exception as e:
                post_status(f"Error: {e}")
                return
            time.sleep(delay)
        post_status("Spamming finished.")

    def start_spamming():
        stop_spam_flag.clear()
        url = webhook_entry.get().strip()
        message = message_text.get("1.0", "end").strip()
        try:
            count = int(spam_count_entry.get())
            delay = float(delay_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Spam Count and Delay must be numbers.")
            return

        if not url or not message:
            messagebox.showerror("Missing Input", "Webhook URL and message are required.")
            return

        threading.Thread(target=spam_webhook_thread, args=(url, message, count, delay, name_entry.get(), avatar_entry.get()), daemon=True).start()

    def stop_spamming():
        stop_spam_flag.set()
        post_status("Stopping spamming...")

    def delete_webhook():
        url = webhook_entry.get().strip()
        if not url:
            messagebox.showerror("Missing Input", "Webhook URL is required.")
            return
        def delete_thread():
            try:
                res = requests.delete(url)
                res.raise_for_status()
                post_status("Webhook deleted successfully.")
            except Exception as e:
                post_status(f"Delete failed: {e}")
        threading.Thread(target=delete_thread, daemon=True).start()

    # Embed window with send/spam buttons
    def open_embed_window():
        embed_win = tk.Toplevel(root)
        embed_win.title("Create and Preview Embed")
        embed_win.configure(bg="#2f3136")
        embed_win.state('zoomed')
        embed_win.iconbitmap("assets/neww.ico")

        desc_label = ttk.Label(embed_win, text="Embed Description:")
        desc_label.pack(anchor="w", padx=10, pady=(10,0))
        desc_text = tk.Text(embed_win, height=6, bg="#40444b", fg="white", insertbackground="white", relief="flat", wrap="word")
        desc_text.pack(fill="x", padx=10, pady=(0,10))

        image_label = ttk.Label(embed_win, text="Embed Image URL:")
        image_label.pack(anchor="w", padx=10, pady=(10,0))
        image_entry = ttk.Entry(embed_win)
        image_entry.pack(fill="x", padx=10, pady=(0,10))

        spam_embed_count_entry = create_input_row(embed_win, "Spam Count:", ttk.Entry(embed_win))
        spam_embed_delay_entry = create_input_row(embed_win, "Delay (seconds):", ttk.Entry(embed_win))
        spam_embed_count_entry.insert(0, "5")
        spam_embed_delay_entry.insert(0, "0.5")

        preview_frame = ttk.Frame(embed_win, relief="groove", borderwidth=2)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=10)

        preview_title = tk.Label(preview_frame, text="Embed Preview", bg="#2f3136", fg="white", font=("Segoe UI", 14, "bold"))
        preview_title.pack(pady=(10,5))

        preview_desc = tk.Label(preview_frame, text="", bg="#2f3136", fg="white", wraplength=800, justify="left", font=("Segoe UI", 11))
        preview_desc.pack(padx=10, pady=5)

        preview_img_label = tk.Label(preview_frame, bg="#2f3136")
        preview_img_label.pack(pady=10)
        preview_img_label.image = None

        def update_preview(*args):
            desc = desc_text.get("1.0", "end").strip()
            img_url = image_entry.get().strip()
            preview_desc.config(text=desc if desc else "(No description)")

            if img_url:
                try:
                    response = requests.get(img_url, timeout=5)
                    response.raise_for_status()
                    img_data = response.content
                    pil_img = Image.open(BytesIO(img_data))
                    pil_img.thumbnail((700, 400))
                    tk_img = ImageTk.PhotoImage(pil_img)
                    preview_img_label.config(image=tk_img)
                    preview_img_label.image = tk_img
                except Exception:
                    preview_img_label.config(image="", text="Failed to load image, please enter correct image url or leave blank else your message won't be sent.")
                    preview_img_label.image = None
            else:
                preview_img_label.config(image="", text="")
                preview_img_label.image = None

        desc_text.bind("<<Modified>>", lambda e: (desc_text.edit_modified(0), update_preview()))
        image_entry.bind("<KeyRelease>", update_preview)

        update_preview()

        def send_embed_once():
            url = webhook_entry.get().strip()
            if not url:
                messagebox.showerror("Missing Input", "Webhook URL is required.")
                return
            desc = desc_text.get("1.0", "end").strip()
            img_url = image_entry.get().strip()

            embed = {}
            if desc: embed["description"] = desc
            if img_url: embed["image"] = {"url": img_url}

            data = {"embeds": [embed]}
            if name_entry.get(): data["username"] = name_entry.get()
            if avatar_entry.get(): data["avatar_url"] = avatar_entry.get()

            def send_thread():
                try:
                    response = requests.post(url, json=data)
                    response.raise_for_status()
                    post_status("Embed message sent successfully.")
                except Exception as e:
                    post_status(f"Failed to send embed: {e}")

            threading.Thread(target=send_thread, daemon=True).start()

        def spam_embed():
            try:
                count = int(spam_embed_count_entry.get())
                delay = float(spam_embed_delay_entry.get())
            except ValueError:
                messagebox.showerror("Invalid Input", "Spam Count and Delay must be numbers.")
                return

            def thread_func():
                for i in range(count):
                    if stop_spam_flag.is_set():
                        post_status("Embed spamming stopped.")
                        return
                    send_embed_once()
                    time.sleep(delay)
                post_status("Finished spamming embed.")

            stop_spam_flag.clear()
            threading.Thread(target=thread_func, daemon=True).start()

        button_frame = ttk.Frame(embed_win)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Send Once", command=send_embed_once).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Spam Embed", command=spam_embed).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=embed_win.destroy).pack(side="left", padx=5)

    buttons_frame = ttk.Frame(root)
    buttons_frame.pack(pady=10)

    ttk.Button(buttons_frame, text="Start Spamming", command=start_spamming).grid(row=0, column=0, padx=5, pady=5)
    ttk.Button(buttons_frame, text="Stop Spamming", command=stop_spamming).grid(row=0, column=1, padx=5, pady=5)
    ttk.Button(buttons_frame, text="Delete Webhook", command=delete_webhook).grid(row=0, column=2, padx=5, pady=5)
    ttk.Button(buttons_frame, text="Create Embed", command=open_embed_window).grid(row=0, column=3, padx=5, pady=5)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
