#correct  input- "list" +make pizza in 1min - 10 sept 2024 at 1:00
import re
from todoist_api_python.api import TodoistAPI
from langchain.agents import load_tools
from langchain.llms import OpenAI

llm = OpenAI(model_name="text-curie-001", temperature=0.7, openai_api_key="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")
api = TodoistAPI("2226b61266e3ef2b6d28f92a34b893a4fa7bc7cd")

# # Get user input for section name and task content
# section_name = input("Enter the section name: ")
# task_content = input("Enter the task content: ")

input_string = input("Enter the input string: ")

# Define a regular expression pattern to match section names, combined task names and values, and alarms
pattern = r'"(.*?)"\s\+([\w\s]+)\s\-([\w\s]+)'

# Find the first match in the input string
match = re.search(pattern, input_string)

if match:
    section_name = match.group(1).strip()
    task_content = match.group(2).strip()  # Combined task name and value
    alarm = match.group(3).strip()

else:
    print("No valid pattern found in the input string.")

# Load langchain tools
tool_names = ["llm-math"]
tools = load_tools(tool_names, llm=llm)

try:
    projects = api.get_projects()
    project_id = next((p.id for p in projects if p.name == section_name), None)

    if not project_id:
        new_project = api.add_project(name=section_name)
        project_id = new_project.id

    sections = api.get_sections(project_id=project_id)
    section_id = next((s.id for s in sections if s.name == section_name), None)

    if not section_id:
        new_section = api.add_section(name=section_name, project_id=project_id)
        section_id = new_section.id
        print("Section created:", new_section)
    else:
        updated_section = api.update_section(section_id, name=section_name)
        print("Section updated:", updated_section)

    result = llm.generate([f"Create a task to {task_content}"])
    print(result)
    # task_content = result.choices[0].text.strip()  # Extract the generated content from LLMResult
    # Add a task within the specified section
    task = api.add_task(
        content=task_content,
        project_id=project_id,
        section_id=section_id,
        due_string=alarm,
        due_lang='en',
        priority=4,
    )
    print("Task added to the 'what list' section in Todoist:", task)
except Exception as error:
    print("Error:", error)
