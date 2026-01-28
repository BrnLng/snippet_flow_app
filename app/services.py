from app.models import Snippet, Task, Tag
from typing import List


class SnippetSerializer:
    
    @staticmethod
    def to_markdown(snippet: Snippet) -> str:
        md = []
        
        md.append(f"{snippet.title}\n")  # '\n' is to ensure double line at later join
        md.append(f"{snippet.body}\n")
        
        if snippet.tasks:
            md.append("```tasks")
            root_tasks = [t for t in snippet.tasks if t.parent_id is None]
            for task in root_tasks:
                md.append(SnippetSerializer._format_task_recursive(task))
            md.append("```\n")

        if snippet.tags:
            md.append("```tags")
            for tag in snippet.tags:
                simple_tag_list = []
                if tag.value:
                    md.append(f"{tag.name}: {tag.value}")
                else:
                    simple_tag_list.append(f"{tag.name}")
                md.append(", ".join(simple_tag_list))
            md.append("```\n")

        md.append("----")
        
        if snippet.updated_by:
            md.append(f"—{snippet.updated_by.username} @ {snippet.updated_at.strftime(r'%d/%m/%Y')}" \
                      f"( / Criado por {snippet.created_by.username} @ {snippet.created_at.strftime(r'%d/%m/%Y')} )")
        else:
            md.append(f"—{snippet.created_by.username} @ {snippet.created_at.strftime(r'%d/%m/%Y')}")
            
        return "\n".join(md)


    @staticmethod
    def _format_task_recursive(task: Task, level: int = 0) -> str:
        indent = "  " * level
        status = "x" if task.is_done else " "
        
        # Formata: "  - [x] Comprar leite"
        line = f"{indent}- [{status}] {task.text}"
        
        # Se tiver um responsável (Assignee), adiciona como anotação
        if task.assignee:
            line += f" —{task.assignee.username}"
            
        lines = [line]
        
        # proccess sub-tasks children
        if task.sub_tasks:
            for sub in task.sub_tasks:
                lines.append(SnippetSerializer._format_task_recursive(sub, level + 1))
                
        return "\n".join(lines)
