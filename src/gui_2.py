import tkinter as tk
import selection_layer as controller


class SimpleGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("SXS Tools")
        self.geometry("300x200")
        self.resizable(False, False)

        self._build_ui()

    def _build_ui(self):
        tk.Label(
            self,
            text="Processing Tools",
            font=("Arial", 14, "bold")
        ).pack(pady=15)

        tk.Button(
            self,
            text="Sankey Diagram",
            width=25,
            command=lambda: controller.run_sankey(self)
        ).pack(pady=5)

        tk.Button(
            self,
            text="Map Visualizer",
            width=25,
            command=lambda: controller.run_map(self)
        ).pack(pady=5)

        tk.Button(
            self,
            text="Batch Plots",
            width=25,
            command=lambda: controller.run_plots(self)
        ).pack(pady=5)


if __name__ == "__main__":
    app = SimpleGUI()
    app.mainloop()