import json
import sys

def create_adjacency_matrix(input_data):
    try:
        # Parse JSON from input string
        json_data = json.loads(input_data)
        
        # Extract email and times for each person
        people = []
        timeslots = {}
        
        for person in json_data:
            email = person.get("email", [])[0].get("value", "")
            timeslots = person.get("times", {})
            people.append({"email": email, "times": timeslots})
       
        
        slots = set(timeslots.keys())

        # Initialize the adjacency matrix with zeros
        num_people = len(people)
        adjacency_matrix = [[0] * num_people for _ in range(num_people)]
        
        # Fill the adjacency matrix based on common time slots
        for i in range(num_people):
            for j in range(i + 1, num_people): 
                common_slots = 0

                for k in slots:
                    p1 = list(people[i]["times"])
                    p2 = list(people[i]["times"])
                    try:
                        i1 = p1.index(k)
                        i2 = p2.index(k)

                        s1, s2 = set(p1[i1]), set(p2[i2])

                        common_slots += len(s1.intersection(s2))
                    except ValueError:
                        continue
                
                adjacency_matrix[i][j] = common_slots
                adjacency_matrix[j][i] = common_slots
        
        return adjacency_matrix, people

    except json.JSONDecodeError:
        print("Invalid JSON input")
        sys.exit(1)

def form_pairs(adjacency_matrix, people):
    num_people = len(people)
    paired_indices = set()
    pairs = []
    while len(pairs) < num_people // 2:
        max_score = 0
        pair = None
        for i in range(num_people):
            for j in range(i + 1, num_people):
                if i not in paired_indices and j not in paired_indices and adjacency_matrix[i][j] > max_score:
                    max_score = adjacency_matrix[i][j]
                    pair = (i, j)
        if pair:
            paired_indices.add(pair[0])
            paired_indices.add(pair[1])
            pairs.append(pair)
        else:
            break
    
    unpaired_emails = [people[i]["email"] for i in range(num_people) if i not in paired_indices]
    return [(people[i]["email"], people[j]["email"]) for i, j in pairs], unpaired_emails

if __name__ == "__main__":
    # Read JSON input from stdin and create adjacency matrix
    json_input = sys.stdin.read()
    adjacency_matrix, people = create_adjacency_matrix(json_input)
    
    # Form pairs and get unpaired emails based on the adjacency matrix
    pairs, unpaired_emails = form_pairs(adjacency_matrix, people)
    result = {}
    result["Paired_emails"] = pairs
    result["Unpaired_emails"] = unpaired_emails

    print(json.dumps(result, indent=2))
