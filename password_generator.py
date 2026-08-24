"""
Random Password Generator — Advanced Tier
Oasis Infobyte SIP — Python Programming Track, Task 3

Features:
- tkinter GUI with length slider and character-type checkboxes
- Cryptographically secure generation using the `secrets` module
- Guarantees at least one character from each selected type
- Password strength indicator (Weak / Medium / Strong)
- "Copy to Clipboard" button using pyperclip
- Option to exclude ambiguous characters (0, O, l, 1, I, etc.)
- Option to exclude specific user-defined characters from selected pools
- Session-only generation history (last 5 passwords) — NOT persisted to disk
"""

import secrets
import string
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

AMBIGUOUS_CHARS = "0Ol1I|`'\""
SYMBOL_POOL = "!@#$%^&*()-_=+[]{};:,.?/"


def normalize_exclude_chars(text: str) -> str:
    """Strip whitespace and duplicate characters from the exclude field."""
    seen = set()
    result = []
    for ch in text:
        if ch.isspace():
            continue
        if ch not in seen:
            seen.add(ch)
            result.append(ch)
    return "".join(result)


def build_character_pools(
    use_upper: bool,
    use_lower: bool,
    use_digits: bool,
    use_symbols: bool,
    exclude_ambiguous: bool,
    exclude_specific: str,
) -> list[str]:
    """Return filtered character pools for each selected type."""
    pools = []
    ambiguous = set(AMBIGUOUS_CHARS) if exclude_ambiguous else set()
    specific = set(normalize_exclude_chars(exclude_specific))
    excluded = ambiguous | specific

    def clean(pool: str) -> str:
        if excluded:
            return "".join(c for c in pool if c not in excluded)
        return pool

    if use_upper:
        pools.append(clean(string.ascii_uppercase))
    if use_lower:
        pools.append(clean(string.ascii_lowercase))
    if use_digits:
        pools.append(clean(string.digits))
    if use_symbols:
        pools.append(clean(SYMBOL_POOL))

    return pools


def generate_password_from_pools(pools: list[str], length: int) -> str:
    """Generate a password from pre-built pools (no GUI dependencies)."""
    password_chars = [secrets.choice(pool) for pool in pools]
    combined = "".join(pools)
    while len(password_chars) < length:
        password_chars.append(secrets.choice(combined))

    for i in range(len(password_chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        password_chars[i], password_chars[j] = password_chars[j], password_chars[i]

    return "".join(password_chars)


class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Generator")
        self.root.geometry("460x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        # Session-only history (never written to a file, per spec)
        self.history = []

        self._build_ui()

    # ---------- UI CONSTRUCTION ----------
    def _build_ui(self):
        pad = {"padx": 20, "pady": 6}

        title = tk.Label(
            self.root, text="🔐 Secure Password Generator",
            font=("Segoe UI", 16, "bold"), bg="#1e1e2e", fg="#cdd6f4"
        )
        title.pack(pady=(20, 10))

        # ---- Length control ----
        length_frame = tk.Frame(self.root, bg="#1e1e2e")
        length_frame.pack(fill="x", **pad)

        tk.Label(
            length_frame, text="Password Length:", bg="#1e1e2e",
            fg="#cdd6f4", font=("Segoe UI", 10)
        ).pack(anchor="w")

        self.length_var = tk.IntVar(value=12)
        slider_row = tk.Frame(length_frame, bg="#1e1e2e")
        slider_row.pack(fill="x")

        self.length_slider = ttk.Scale(
            slider_row, from_=8, to=64, orient="horizontal",
            variable=self.length_var, command=self._on_slider_move
        )
        self.length_slider.pack(side="left", fill="x", expand=True)

        self.length_label = tk.Label(
            slider_row, text="12", width=3, bg="#1e1e2e",
            fg="#a6e3a1", font=("Segoe UI", 10, "bold")
        )
        self.length_label.pack(side="left", padx=(8, 0))

        # ---- Character type checkboxes ----
        types_frame = tk.LabelFrame(
            self.root, text=" Character Types ", bg="#1e1e2e",
            fg="#cdd6f4", font=("Segoe UI", 10, "bold"),
            labelanchor="nw", bd=1, relief="solid"
        )
        types_frame.pack(fill="x", **pad)

        self.use_upper = tk.BooleanVar(value=True)
        self.use_lower = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        self.exclude_ambiguous = tk.BooleanVar(value=False)

        checks = [
            ("Uppercase (A-Z)", self.use_upper),
            ("Lowercase (a-z)", self.use_lower),
            ("Numbers (0-9)", self.use_digits),
            ("Symbols (!@#$...)", self.use_symbols),
        ]
        for label, var in checks:
            cb = tk.Checkbutton(
                types_frame, text=label, variable=var,
                bg="#1e1e2e", fg="#cdd6f4", selectcolor="#313244",
                activebackground="#1e1e2e", activeforeground="#cdd6f4",
                font=("Segoe UI", 10), anchor="w"
            )
            cb.pack(fill="x", padx=10, pady=2)

        tk.Checkbutton(
            types_frame, text="Exclude ambiguous characters (0, O, l, 1, I)",
            variable=self.exclude_ambiguous,
            bg="#1e1e2e", fg="#f9e2af", selectcolor="#313244",
            activebackground="#1e1e2e", activeforeground="#f9e2af",
            font=("Segoe UI", 9, "italic"), anchor="w"
        ).pack(fill="x", padx=10, pady=(6, 4))

        exclude_row = tk.Frame(types_frame, bg="#1e1e2e")
        exclude_row.pack(fill="x", padx=10, pady=(0, 8))

        tk.Label(
            exclude_row, text="Exclude specific characters:",
            bg="#1e1e2e", fg="#cdd6f4", font=("Segoe UI", 9)
        ).pack(anchor="w")

        self.exclude_chars_var = tk.StringVar(value="")
        tk.Entry(
            exclude_row, textvariable=self.exclude_chars_var,
            bg="#313244", fg="#cdd6f4", insertbackground="#cdd6f4",
            font=("Consolas", 10), relief="flat", bd=4
        ).pack(fill="x", pady=(2, 0))

        # ---- Generate button ----
        gen_btn = tk.Button(
            self.root, text="Generate Password", command=self.generate_password,
            bg="#89b4fa", fg="#1e1e2e", font=("Segoe UI", 11, "bold"),
            relief="flat", cursor="hand2", pady=8
        )
        gen_btn.pack(fill="x", **pad)

        # ---- Result display ----
        result_frame = tk.Frame(self.root, bg="#1e1e2e")
        result_frame.pack(fill="x", **pad)

        self.result_var = tk.StringVar(value="")
        self.result_entry = tk.Entry(
            result_frame, textvariable=self.result_var, font=("Consolas", 13),
            justify="center", state="readonly", readonlybackground="#313244",
            fg="#a6e3a1", relief="flat", bd=8
        )
        self.result_entry.pack(fill="x", ipady=6)

        # ---- Strength indicator ----
        self.strength_label = tk.Label(
            self.root, text="", font=("Segoe UI", 10, "bold"), bg="#1e1e2e"
        )
        self.strength_label.pack(pady=(4, 0))

        self.strength_bar = ttk.Progressbar(
            self.root, orient="horizontal", length=400, mode="determinate", maximum=100
        )
        self.strength_bar.pack(pady=(4, 10))

        # ---- Copy button ----
        copy_btn = tk.Button(
            self.root, text="📋 Copy to Clipboard", command=self.copy_to_clipboard,
            bg="#a6e3a1", fg="#1e1e2e", font=("Segoe UI", 10, "bold"),
            relief="flat", cursor="hand2", pady=6
        )
        copy_btn.pack(fill="x", **pad)

        # ---- History ----
        history_label = tk.Label(
            self.root, text="Recent Passwords (this session only):",
            bg="#1e1e2e", fg="#cdd6f4", font=("Segoe UI", 9)
        )
        history_label.pack(anchor="w", padx=20, pady=(10, 2))

        self.history_box = tk.Listbox(
            self.root, height=5, bg="#313244", fg="#bac2de",
            font=("Consolas", 9), relief="flat", selectbackground="#89b4fa"
        )
        self.history_box.pack(fill="x", padx=20, pady=(0, 10))

    # ---------- LOGIC ----------
    def _on_slider_move(self, value):
        self.length_label.config(text=str(int(float(value))))

    def _selected_pools(self):
        """Return list of (pool_string) for each checked character type."""
        return build_character_pools(
            self.use_upper.get(),
            self.use_lower.get(),
            self.use_digits.get(),
            self.use_symbols.get(),
            self.exclude_ambiguous.get(),
            self.exclude_chars_var.get(),
        )

    def generate_password(self):
        length = int(self.length_var.get())

        if length < 8:
            messagebox.showerror("Invalid Length", "Password length must be at least 8 characters.")
            return

        pools = self._selected_pools()
        if len(pools) < 2:
            messagebox.showerror(
                "Selection Required",
                "Please select at least 2 character types to generate a strong password."
            )
            return

        if any(not pool for pool in pools):
            messagebox.showerror(
                "Invalid Exclusions",
                "Your excluded characters remove all characters from one or more "
                "selected types. Please adjust your exclusions or character types."
            )
            return

        password = generate_password_from_pools(pools, length)
        self.result_var.set(password)

        self._update_strength(password)
        self._add_to_history(password)

    def _update_strength(self, password):
        length = len(password)
        variety = sum([
            any(c.isupper() for c in password),
            any(c.islower() for c in password),
            any(c.isdigit() for c in password),
            any(not c.isalnum() for c in password),
        ])

        score = min(100, length * 2 + variety * 15)

        if score < 50:
            label, color = "Weak", "#f38ba8"
        elif score < 75:
            label, color = "Medium", "#f9e2af"
        else:
            label, color = "Strong", "#a6e3a1"

        self.strength_label.config(text=f"Strength: {label}", fg=color)
        self.strength_bar["value"] = score

    def _add_to_history(self, password):
        self.history.insert(0, password)
        self.history = self.history[:5]  # keep only last 5, session memory only

        self.history_box.delete(0, tk.END)
        for pw in self.history:
            self.history_box.insert(tk.END, pw)

    def copy_to_clipboard(self):
        password = self.result_var.get()
        if not password:
            messagebox.showwarning("Nothing to Copy", "Generate a password first.")
            return

        if CLIPBOARD_AVAILABLE:
            pyperclip.copy(password)
            messagebox.showinfo("Copied", "Password copied to clipboard!")
        else:
            messagebox.showwarning(
                "Clipboard Unavailable",
                "pyperclip is not installed. Run: pip install pyperclip"
            )


def run_exclude_tests():
    """Simple tests for exclude-specific-characters behavior."""
    # (3) Whitespace and duplicate handling
    assert normalize_exclude_chars("  a A a \t1\n1  ") == "aA1"

    # (2) Exclusions that wipe out an entire selected pool
    wiped_pools = build_character_pools(
        use_upper=False,
        use_lower=True,
        use_digits=True,
        use_symbols=False,
        exclude_ambiguous=False,
        exclude_specific=string.ascii_lowercase,
    )
    assert wiped_pools[0] == "", "Lowercase pool should be empty when all letters excluded"
    assert any(not pool for pool in wiped_pools)

    # (1) Excluded characters never appear in generated output
    exclude = "aA1"
    pools = build_character_pools(
        use_upper=True,
        use_lower=True,
        use_digits=True,
        use_symbols=False,
        exclude_ambiguous=False,
        exclude_specific=exclude,
    )
    assert all(pools), "Pools should remain non-empty for this exclusion set"
    excluded = set(exclude)
    for _ in range(200):
        password = generate_password_from_pools(pools, length=24)
        assert not any(ch in excluded for ch in password), (
            f"Excluded character found in password: {password!r}"
        )

    print("All exclude-character tests passed.")


def main():
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_exclude_tests()
    else:
        main()