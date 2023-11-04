import json
import sys


EMAIL_QID = '2153e95f'

def parse_json(input_json):
    try:
        # Parse JSON from input string
        json_data = json.loads(input_json)
        
        # Extract relevant data from JSON
        responses = json_data.get("responses", [])
        people = []
        days = {}
        email = "ERROR@didnt-find-email.com"
        for response in responses:
            answers = response.get("answers", {})
            for question_id, answer in answers.items():
                
                if question_id == EMAIL_QID:
                    email = answer["textAnswers"]["answers"]
                    continue
                if "textAnswers" in answer: 
                    values = answer["textAnswers"]["answers"]
                    if len(values) < 1 or ":" not in values[0]["value"]:
                        continue
                    day = []
                    for value in values:
                        if ":" not in value["value"]:
                            continue
                        time_slot = value["value"]
                        # Extract hour from the time slot (e.g., "XX:00")
                        hour = time_slot.split(":")[0]
                        day.append(int(hour))
                    days[question_id] = day
            people.append({ "email": email, "times": days })
            days = {}
            email = "ERROR@didnt-find-email.com"
         
        return json.dumps(people) 
         
    except json.JSONDecodeError:
        print("Invalid JSON input")
        sys.exit(1)

if __name__ == "__main__":
    # Raad JSON input from stdin
    json_input = sys.stdin.read()
    print(parse_json(json_input))

