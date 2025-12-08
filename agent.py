from mesa import Agent

class UserAgent(Agent):
    def __init__(self, unique_id, model, agent_type="normal", critical_thinking=None, misinformation=False):
        super().__init__(unique_id, model)
        self.agent_type = agent_type
        self.critical_thinking = critical_thinking if critical_thinking is not None else model.random.random()
        self.believes_misinformation = misinformation
        self.belief = "misinformed" if misinformation else "informed"
        self.influence_count = 0
        self.correction_count = 0  # Track corrections made by fact checkers
        
        
        
        if agent_type == "fact_checker":
            self.critical_thinking = 1.0
            self.believes_misinformation = False
            self.belief = "informed"
            self.correction_strength = 0.95 
            self.search_radius = 3  
            self.correction_attempts = 0
            self.successful_corrections = 0
            self.correction_cooldown = 0
            self.movement_speed = 1  
            self.last_position = None  # Track last position for movement
        elif agent_type == "influencer":


            self.influence_radius = 3  
            self.influence_strength = 0.9  
            self.influence_count = 0
            self.movement_speed = 2
            self.influence_decay = 0.98  
            self.influence_cooldown = 0  
        elif agent_type == "echo_chamber":
            self.only_similar = True
            self.belief_strength = 0.7  
            self.critical_thinking = max(0.1, self.critical_thinking)  # Lower minimum critical thinking
            self.cluster_radius = 3 

            self.cluster_center = None  
            self.belief_reinforcement = 0.15  
            self.reinforcement_cooldown = 0  


            
        elif agent_type == "political":
            self.political_side = None  # Will be set during creation
            self.influence_strength = 0.8
            self.polarization = 0.7  
            self.conversion_chance = 0.3  # Chance to convert others
            self.movement_speed = 1
            self.influence_radius = 2 

    def calculate_cluster_center(self):
        """Calculate the center of the cluster this agent belongs to"""
        if not hasattr(self, 'pos'):
            return (self.model.grid.width // 2, self.model.grid.height // 2)
            
        if self.pos[0] < self.model.grid.width // 2:
            center_x = self.model.grid.width // 4
        else:
            center_x = 3 * self.model.grid.width // 4
            
        if self.pos[1] < self.model.grid.height // 2:
            center_y = self.model.grid.height // 4
        else:
            center_y = 3 * self.model.grid.height // 4
            
        return (center_x, center_y)

    def step(self):
        # Initialize cluster center for echo chamber agents if not set
        if self.agent_type == "echo_chamber" and self.cluster_center is None:
            self.cluster_center = self.calculate_cluster_center()
            
        if self.agent_type == "fact_checker":
            self.fact_checker_step()
        elif self.agent_type == "influencer":
            self.influencer_step()
        elif self.agent_type == "echo_chamber":
            self.echo_chamber_step()
        elif self.agent_type == "political":
            self.political_step()
        else:
            self.normal_step()

    def normal_step(self):
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        misinformation_count = sum(1 for n in neighbors if n.believes_misinformation)
        total_neighbors = len(neighbors)

        if not self.believes_misinformation:
            chance = misinformation_count / total_neighbors if total_neighbors > 0 else 0
            adjusted_chance = chance * (1 - self.critical_thinking)
            if self.random.random() < adjusted_chance:
                self.believes_misinformation = True
                self.belief = "misinformed"
        else:
            informed_count = total_neighbors - misinformation_count
            if informed_count > misinformation_count and self.random.random() < self.critical_thinking:
                self.believes_misinformation = False
                self.belief = "informed"

    def fact_checker_step(self):
        """Execute fact checker's step"""
        # Apply cooldown
        if self.correction_cooldown > 0:
            self.correction_cooldown -= 1
          
            self.move_towards_misinformation()
            return

       
        extended_neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False, radius=self.search_radius
        )
        
      
        misinformed_neighbors = [n for n in extended_neighbors if n.believes_misinformation]
        if misinformed_neighbors:
            
            misinformed_neighbors.sort(key=lambda x: x.critical_thinking, reverse=True)
            
            for neighbor in misinformed_neighbors:
                self.correction_attempts += 1
                
                adjusted_strength = self.correction_strength * (0.8 + neighbor.critical_thinking * 0.2)
                
                if self.random.random() < adjusted_strength:
                    neighbor.believes_misinformation = False
                    neighbor.belief = "informed"
                    self.correction_count += 1
                    self.successful_corrections += 1
                    
                   
                    neighbor.critical_thinking = min(1.0, neighbor.critical_thinking + 0.4)
                    self.correction_cooldown = 1  # Reduced cooldown
                    break  # Only correct one agent per step
        else:
            # Move towards areas with more misinformed agents
            self.move_towards_misinformation()

    def influencer_step(self):
        # Apply influence decay
        self.influence_count *= self.influence_decay
        
        # Apply cooldown
        if self.influence_cooldown > 0:
            self.influence_cooldown -= 1
            return
        
        for _ in range(self.movement_speed):
            self.move_to_center()
        
        extended_neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False, radius=self.influence_radius
        )
        
        extended_neighbors.sort(key=lambda x: x.critical_thinking)
        
        for neighbor in extended_neighbors:
            if neighbor.believes_misinformation != self.believes_misinformation:
                
                adjusted_strength = self.influence_strength * (1.0 - neighbor.critical_thinking * 0.5)
                
                if self.random.random() < adjusted_strength:
                    neighbor.believes_misinformation = self.believes_misinformation
                    neighbor.belief = self.belief
                    self.influence_count += 1
                    
                  
                    if neighbor.agent_type == "echo_chamber":
                        neighbor.belief_strength = max(0.1, neighbor.belief_strength - 0.3)
                    
                    self.influence_cooldown = 1  
                    break  

    def echo_chamber_step(self):
        # Apply cooldown
        if self.reinforcement_cooldown > 0:
            self.reinforcement_cooldown -= 1
            return

      
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False, radius=self.cluster_radius
        )
        
        similar_neighbors = [n for n in neighbors if n.believes_misinformation == self.believes_misinformation]
        
        if similar_neighbors:
            # Reinforce belief within echo chamber more frequently
            if self.random.random() < 0.4:  
                self.belief_strength = min(1.0, self.belief_strength + self.belief_reinforcement)
                self.critical_thinking = max(0.1, self.critical_thinking - 0.08)  
                
                # Try to influence similar neighbors to strengthen their belief
                for neighbor in similar_neighbors:
                    if neighbor.agent_type == "echo_chamber":
                        neighbor.belief_strength = min(1.0, neighbor.belief_strength + self.belief_reinforcement * 0.7)  
                        neighbor.critical_thinking = max(0.1, neighbor.critical_thinking - 0.05)
                
                self.reinforcement_cooldown = 1  # Add cooldown after reinforcement
            
            if len(similar_neighbors) < len(neighbors) * 0.7:  
                self.move_towards_similar(similar_neighbors)
        else:
            # Return to cluster center if too far
            self.return_to_cluster()

    def move_towards_misinformation(self):
        """Move towards areas with higher concentration of misinformed agents"""
        # Get all agents in search radius
        extended_neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False, radius=self.search_radius * 2
        )
        
        if extended_neighbors:
            # Calculate direction with most misinformed agents
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]
            best_direction = None
            max_misinfo = -1
            
            for dx, dy in directions:
                new_x = (self.pos[0] + dx) % self.model.grid.width
                new_y = (self.pos[1] + dy) % self.model.grid.height
                cell_agents = self.model.grid.get_cell_list_contents([(new_x, new_y)])
                misinfo_count = sum(1 for a in cell_agents if a.believes_misinformation)
                
                if misinfo_count > max_misinfo:
                    max_misinfo = misinfo_count
                    best_direction = (dx, dy)
            
            if best_direction:
                # Move one step in the best direction
                new_x = (self.pos[0] + best_direction[0]) % self.model.grid.width
                new_y = (self.pos[1] + best_direction[1]) % self.model.grid.height
                self.model.grid.move_agent(self, (new_x, new_y))
            else:
                # If no direction has misinformed agents, move randomly
                possible_steps = self.model.grid.get_neighborhood(
                    self.pos, moore=True, include_center=False
                )
                if possible_steps:
                    new_position = self.random.choice(possible_steps)
                    self.model.grid.move_agent(self, new_position)

    def move_to_center(self):
        center_x = self.model.grid.width // 2
        center_y = self.model.grid.height // 2
        current_x, current_y = self.pos
        
        if current_x < center_x:
            new_x = min(self.model.grid.width - 1, current_x + 1)
        elif current_x > center_x:
            new_x = max(0, current_x - 1)
        else:
            new_x = current_x
            
        if current_y < center_y:
            new_y = min(self.model.grid.height - 1, current_y + 1)
        elif current_y > center_y:
            new_y = max(0, current_y - 1)
        else:
            new_y = current_y
            
        self.model.grid.move_agent(self, (new_x, new_y))

    def move_towards_similar(self, similar_neighbors):
        if similar_neighbors:
            target = self.random.choice(similar_neighbors)
            # Move towards target's position instead of the agent itself
            target_x, target_y = target.pos
            current_x, current_y = self.pos
            
            # Calculate direction to move
            dx = 1 if target_x > current_x else -1 if target_x < current_x else 0
            dy = 1 if target_y > current_y else -1 if target_y < current_y else 0
            
            # Calculate new position
            new_x = (current_x + dx) % self.model.grid.width
            new_y = (current_y + dy) % self.model.grid.height
            
            self.model.grid.move_agent(self, (new_x, new_y))

    def return_to_cluster(self):
        
        current_x, current_y = self.pos
        center_x, center_y = self.cluster_center
        
        new_x = current_x + (1 if current_x < center_x else -1 if current_x > center_x else 0)
        new_y = current_y + (1 if current_y < center_y else -1 if current_y > center_y else 0)
        
       
        new_x = max(0, min(self.model.grid.width - 1, new_x))
        new_y = max(0, min(self.model.grid.height - 1, new_y))
        
        self.model.grid.move_agent(self, (new_x, new_y))

  
    def move_towards_agent(self, target):
        """Move towards another agent"""
        target_x, target_y = target.pos
        current_x, current_y = self.pos
        
        # Calculate direction to move
        dx = 1 if target_x > current_x else -1 if target_x < current_x else 0
        dy = 1 if target_y > current_y else -1 if target_y < current_y else 0
        
        # Calculate new position
        new_x = (current_x + dx) % self.model.grid.width
        new_y = (current_y + dy) % self.model.grid.height
        
        self.model.grid.move_agent(self, (new_x, new_y))

    def move_randomly(self):
        """Move randomly"""
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        if possible_steps:
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)
