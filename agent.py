#correct  input- "list" +make pizza in 1min - 10 sept 2024 at 1:00
import re
from todoist_api_python.api import TodoistAPI
from langchain.agents import load_tools
from langchain.llms import OpenAI

llm = OpenAI(model_name="text-curie-001", temperature=0.7, openai_api_key="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")
api = TodoistAPI("2226b61266e3ef2b6d28f92a34b893a4fa7bc7cd")

input_string = input("Enter the input string: ")

pattern = r'"(.*?)"\s\+([\w\s]+)\s\-([\w\s]+)'

match = re.search(pattern, input_string)

if match:
    section_name = match.group(1).strip()
    task_content = match.group(2).strip()  # Combined task name and value
    alarm = match.group(3).strip()

else:
    print("No valid pattern found in the input string.")

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
    result_str = str(result)
    print(result_str)
    generated_text = result_str.split("text='")[1].split("'")[0]
    generated = generated_text.replace('\n\n', '')

    print(generated)
    # Extract the generated content by joining the tokens
    # generated_content = result[0].text.strip() 

    # Add a task within the specified section
    task = api.add_task(
        content=task_content,  # Use the generated content as the task content
        project_id=project_id,
        section_id=section_id,
        due_string=alarm,
        due_lang='en',
        priority=4,
    )
    print("Task added to the 'what list' section in Todoist:", task)

    subtask = api.add_task(
        content=generated,
        project_id=project_id,
        parent_id=task.id,  
        due_string=alarm,  
        due_lang='en',
        priority=4,
    )
    print("Subtask added to the task:", subtask)

except Exception as error:
    print("Error:", error)
