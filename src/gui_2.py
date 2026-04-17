import tkinter as tk
import selection_layer_2 as controller


class SimpleGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("SXS Tools")
        self.geometry("300x240")
        self.resizable(False, False)

        self._build_ui()

    def _build_ui(self):
        tk.Label(
            self,
            text="Eines",
            font=("Arial", 14, "bold")
        ).pack(pady=15)

        tk.Button(
            self,
            text="Diagrama Sankey",
            width=25,
            command=lambda: controller.run_sankey(self)
        ).pack(pady=5)

        tk.Button(
            self,
            text="Mapa dels punts de mesura",
            width=25,
            command=lambda: controller.run_map(self)
        ).pack(pady=5)

        # NEW: Preview plot button
        tk.Button(
            self,
            text="Veure un gràfic",
            width=25,
            command=lambda: controller.run_preview_plot(self)
        ).pack(pady=5)

        # RENAMED: Batch plots
        tk.Button(
            self,
            text="Gràfics de tots els arxius",
            width=25,
            command=lambda: controller.run_batch_plots_folder(self)
        ).pack(pady=5)


if __name__ == "__main__":
    app = SimpleGUI()
    app.mainloop() 