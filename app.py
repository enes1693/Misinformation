import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class MisinformationSimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("Misinformation Simulation")
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scenario selection
        ttk.Label(self.main_frame, text="Select Scenario:").grid(row=0, column=0, sticky=tk.W)
        self.scenario_var = tk.StringVar(value="natural")
        scenarios = [
            ("Natural Spread", "natural"),
            ("Fact Checkers", "fact_checkers"),
            ("Influencers", "influencers"),
            ("Echo Chambers", "echo_chamber"),
            ("Political Influence", "political")
        ]
        for i, (text, value) in enumerate(scenarios):
            ttk.Radiobutton(
                self.main_frame,
                text=text,
                value=value,
                variable=self.scenario_var
            ).grid(row=0, column=i+1, padx=5)

    def create_graphs(self):
        """Create and update graphs"""
        # Create figure with subplots
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Plot 1: Misinformation spread
        self.line1, = self.ax1.plot([], [], 'b-', label='Informed')
        self.line2, = self.ax1.plot([], [], 'r-', label='Misinformed')
        self.ax1.set_title('Misinformation Spread Over Time')
        self.ax1.set_xlabel('Step')
        self.ax1.set_ylabel('Number of Agents')
        self.ax1.legend()
        self.ax1.grid(True)
        
        # Plot 2: Agent types
        self.line3, = self.ax2.plot([], [], 'g-', label='Fact Checkers')
        self.line4, = self.ax2.plot([], [], 'm-', label='Influencers')
        self.line5, = self.ax2.plot([], [], 'c-', label='Echo Chambers')
        self.line6, = self.ax2.plot([], [], 'y-', label='Political')
        self.ax2.set_title('Agent Types Over Time')
        self.ax2.set_xlabel('Step')
        self.ax2.set_ylabel('Number of Agents')
        self.ax2.legend()
        self.ax2.grid(True)
        
        # Adjust layout
        plt.tight_layout()
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=3, column=0, columnspan=6, pady=10)

    def update_graphs(self):
        """Update graphs with new data"""
        # Get data from model
        model_data = self.model.datacollector.get_model_vars_dataframe()
        
        # Update misinformation spread plot
        self.line1.set_data(range(len(model_data)), model_data['Informed'])
        self.line2.set_data(range(len(model_data)), model_data['Misinformed'])
        self.ax1.relim()
        self.ax1.autoscale_view()
        
        # Update agent types plot
        self.line3.set_data(range(len(model_data)), model_data['Fact_Checkers'])
        self.line4.set_data(range(len(model_data)), model_data['Influencers'])
        self.line5.set_data(range(len(model_data)), model_data['Echo_Chambers'])
        self.line6.set_data(range(len(model_data)), model_data['Left_Leaning'] + model_data['Right_Leaning'] + model_data['Neutral'])
        self.ax2.relim()
        self.ax2.autoscale_view()
        
        # Redraw canvas
        self.canvas.draw() 

        