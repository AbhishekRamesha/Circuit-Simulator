# Class used to store information for a wire
class Node(object):
    def __init__(self, name, value, gatetype, innames):
        self.name = name         # string
        self.value = value        # char: '0', '1', 'U' for unknown
        self.gatetype = gatetype    # string such as "AND", "OR" etc
        self.interms = []     # list of nodes (first as strings, then as nodes), each is a input wire to the gatetype
        self.innames = innames  # helper string to temperarily store the interms' names, useful to find all the interms nodes and link them
        self.is_input = False    # boolean: true if this wire is a primary input of the circuit
        self.is_output = False   # boolean: true if this wire is a primary output of the circuit
        self.is_fault = False   # boolean: true if this wire is a fault of the circuit

    def set_value(self, v):
        self.value = v 

    def display(self):     # print out the node nicely on one line
        
        if self.is_input:
            # nodeinfo = f"input:\t{str(self.name[4:]):5} = {self.value:^4}" 
            nodeinfo = f"input:\t{str(self.name):5} = {self.value:^4}" 
            print(nodeinfo)
            return 
        elif self.is_output:
            nodeinfo = f"output:\t{str(self.name):5} = {self.value:^4}"
        else:               # internal nodes   
            nodeinfo = f"wire:  \t{str(self.name):5} = {self.value:^4}"

        interm_str = " "
        interm_val_str = " "
        for i in self.interms:
            interm_str += str(i.name)+" "
            interm_val_str += str(i.value)+" "

        nodeinfo += f"as {self.gatetype:>5}"
        nodeinfo += f"  of   {interm_str:20} = {interm_val_str:20}"

        print(nodeinfo)
        return 

    # calculates the value of a node based on its gate type and values at interms
    def calculate_value(self):

        # for i in self.interms:  # skip calculating unless all interms have specific values 1 or 0
        #     if i.value != "0" and i.value !="1":
        #         return "U"

        if self.gatetype == "AND":
            val = "1"
            for i in self.interms:
                if i.value == "0":
                    val = "0"
                if val != "0":
                  if i.value == "U":
                    val = "U"
            self.value = val
            return val
        elif self.gatetype == "OR":
            val = "0"
            for i in self.interms:
                if i.value == '1':
                    val = "1"
                if val != "1":
                  if i.value == "U":
                    val = "U"
            self.value = val
            return val
        elif self.gatetype == "NAND":
            val = "0"
            for i in self.interms:
                if i.value == "0":
                    val = "1"
                if val!= "1":
                  if i.value == "U":
                    val = "U"
            self.value = val
            return val
        elif self.gatetype == "NOT":
            if self.interms[0].value == "0":
              val = "1"
            elif self.interms[0].value == "1":
              val = "0"
            elif self.interms[0].value == "U":
              val = "U"
            self.value = val
            return val
        elif self.gatetype == "XOR":
            val = "0"
            for i in self.interms:
                if i.value == "U":
                    val = "U"
                    self.value = val
                    return val
            if val != "U":
                num_of_1 = 0
                for i in self.interms:
                    if i.value == "1":
                        num_of_1 = num_of_1 + 1
                val = num_of_1 % 2
                val = str(val)
                self.value = val
                return val
        elif self.gatetype == "XNOR":
            val ="0"
            for i in self.interms:
                if i.value == "U":
                      val = "U"
                      self.value = val
                      return val
            if val != "U":
                num_of_1 = 0
                for i in self.interms:
                    if i.value == "1":
                        num_of_1 = num_of_1 + 1
                val = num_of_1 % 2
                self.value = str(1-val)
                return val
        elif self.gatetype == "NOR":
            val ="1"
            for i in self.interms:
                if i.value == "1":
                    val = "0"
                if val != "0":
                  if i.value == "U":
                      val = "U"
            self.value = val
            return val
        elif self.gatetype == "BUFF":
            val = self.interms[0].value
            self.value = val
            return val



# Take a line from the circuit file which represents a gatetype operation and returns a node that stores the gatetype

def parse_gate(rawline):
# example rawline is: a' = NAND(b', 256, c')

# should return: node_name = a',  node_gatetype = NAND,  node_innames = [b', 256, c']

    # get rid of all spaces
    line = rawline.replace(" ", "")
    # now line = a'=NAND(b',256,c')

    name_end_idx = line.find("=")
    node_name = line[0:name_end_idx]
    # now node_name = a'

    gt_start_idx = line.find("=") + 1
    gt_end_idx = line.find("(")
    node_gatetype = line[gt_start_idx:gt_end_idx]
    # now node_gatetype = NAND

    # get the string of interms between ( ) to build tp_list
    interm_start_idx = line.find("(") + 1
    end_position = line.find(")")
    temp_str = line[interm_start_idx:end_position]
    tp_list = temp_str.split(",")
    # now tp_list = [b', 256, c]

    node_innames = [i for i in tp_list]
    # now node_innames = [b', 256, c]

    return node_name, node_gatetype, node_innames


# Create circuit node list from input file
def construct_nodelist():
    o_name_list = []

    for line in input_file_values:
        if line == "\n":
            continue

        if line.startswith("#"):
            continue

        # TODO: clean this up
        if line.startswith("INPUT"):
            index = line.find(")")
            # intValue = str(line[6:index])
            name = str(line[6:index])
            n = Node(name, "U", "PI", [])
            n.is_input = True
            node_list.append(n)


        elif line.startswith("OUTPUT"):
            index = line.find(")")
            name = line[7:index]
            o_name_list.append(name)


        else:   # majority of internal gates processed here
            node_name, node_gatetype, node_innames = parse_gate(line)
            n = Node(node_name, "U", node_gatetype, node_innames)
            node_list.append(n)

    # now mark all the gates that are output as is_output
    for n in node_list:
        if n.name in o_name_list:
            n.is_output = True


    # link the interm nodes from parsing the list of node names (string)
    # example: a = AND (b, c, d)
    # thus a.innames = [b, c, d]
    # node = a, want to search the entire node_list for b, c, d
    for node in node_list:
        for cur_name in node.innames:
            for target_node in node_list:
                if target_node.name == cur_name:
                    node.interms.append(target_node)

    return 

# OTDO: make a circuit class, containing a nodelist, display function, and simulation method.
class circuit(object):
    def __init__(self, node_list, is_fault):
        self.node_list = node_list        # char: '0', '1', 'U' for unknown
        self.is_fault = is_fault
        self.f_val = "U"
        self.f_node ="U"
        self.input_list = []
        self.input_val = []
        self.output_list = []
        self.output_val = []
        #self.node_name = []
               # boolean: true if this wire is a fault of the circuit
    
    def simulation(self):
      updated_count = 1       #initialize to 1 to enter while loop at least once
      iteration = 0
      while updated_count > 0:
        updated_count = 0
        iteration += 1
        flag = 0
        output = 0
        for n in node_list:
          if self.is_fault:
            if n.name == self.f_node:
              n.is_fault = True
              n.value = self.f_val
          if n.value == "U":
            n.calculate_value()
            if n.is_output == True:
              output += 1
              if n.value == "0" or n.value == "1":
                flag += 1
              else:
                flag += 0
            if n.value == "0" or n.value == "1":
              updated_count +=1
        if self.is_fault == True:
           print (f'Bad Circuit Simulation:--- iteration {iteration} finished: updated {updated_count} values--- ')
        else:
           print (f'Good Circuit Simulation:--- iteration {iteration} finished: updated {updated_count} values--- ') 
        if flag == output:
          break
    
    def display(self):     # print out the node nicely on one line
        

        self.input_list = [i.name for i in self.node_list if i.is_input]
        self.input_val = [i.value for i in self.node_list if i.is_input]



        self.output_list = [i.name for i in self.node_list if i.is_output]
        self.output_val = [i.value for i in self.node_list if i.is_output]


        return
# Main function starts

# Step 1: get circuit file name from command line
wantToInputCircuitFile = str(
    input("Provide a benchfile name (return to accept circuit.bench by default):\n"))

if len(wantToInputCircuitFile) != 0:
    circuitFile = wantToInputCircuitFile
    try:
        f = open(circuitFile)
        f.close()
    except FileNotFoundError:
        print('File does not exist, setting circuit file to default')
        circuitFile = "circuit.bench"
else:
    circuitFile = "circuit.bench"

# Constructing the circuit netlist
file1 = open(circuitFile, "r")
input_file_values = file1.readlines()
file1.close()
node_list = []
construct_nodelist()


print ("---------------")

while True:
    line_of_val = input("Enter the Input Vector:\n")
    if len(line_of_val)==0:
        break
    # Clear all nodes values to U in between simulation runs
    for node in node_list:
        node.set_value("U")

    flag = True
    while flag:
        line_of_fault = input("Which node is faulty? ")
        for n in node_list:
          if line_of_fault == n.name:
              flag = False
        if flag:
            print("enter a value from node list")
        
    while True:
      value_of_fault = None
      value_of_fault = input("stuck at 0 or 1? ")
      if value_of_fault == "0" or value_of_fault == "1":
          break
      else:
          print("Please enter either 0 or 1")
          value_of_fault = input("stuck at 0 or 1? ")
          break
        


    if len(line_of_fault) == 0:
        break

    strindex = 0
    # Set value of input node
    for node in node_list:
        if node.is_input:
            if strindex > len(line_of_val)-1:
                break
            node.set_value(line_of_val[strindex])
            strindex = strindex + 1

    print(f'simulating with the following fault:   {line_of_fault}-SA-{value_of_fault}')

    for node in node_list:
        if node.is_input:
            node.display()


    print("--- Begin simulation: ---")
    circuit1 = circuit(node_list, False)
    print("Start of simulation")
    circuit1.simulation()
    circuit1.display()
    for node in node_list:
        node.set_value("U")
    
    strindex = 0
    for node in node_list:
        if node.is_input:
            if strindex > len(line_of_val)-1:
                break
            node.set_value(line_of_val[strindex])
            strindex = strindex + 1
    circuit2 = circuit(node_list, True)
    circuit2.f_node = line_of_fault
    circuit2.f_val = value_of_fault
    circuit2.simulation()
    circuit2.display()
    print("\n--- Simulation results: ---")
    print("Input: \t", end="")
    print(*circuit1.input_list, end = "")
    print("\t = \t", end = "")
    print(*circuit1.input_val)
    print("Output:")
    x = len(circuit1.output_val)
    for i in range (x):
        print(f'{circuit1.output_list[i]} = {circuit1.output_val[i]} / {circuit2.output_val[i]}')
    
    if circuit1.output_val == circuit2.output_val:
      print("Fault is not detected\n")
    else:
      l = len(circuit1.output_val)
      print("Fault is detected at:")
      for i in range (l):
          if circuit1.output_val[i] != circuit2.output_val[i]:
              print(f'{circuit1.output_list[i]} = {circuit1.output_val[i]} / {circuit2.output_val[i]}\n')
    

print(f"Finished - bye!")
