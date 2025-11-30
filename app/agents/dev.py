from pathlib import Path
from app.agents.base_agent import BaseAgent
from app.core.config import settings


class DevAgent(BaseAgent):
    def __init__(self):
        super().__init__("Dev Agent")
        self.output_dir = Path(settings.OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _ensure_unique_path(self, filename: str) -> Path:
        path = self.output_dir / filename
        if not path.exists():
            return path
        stem = path.stem
        suffix = path.suffix
        counter = 1
        while True:
            candidate = self.output_dir / f"{stem}_{counter}{suffix}"
            if not candidate.exists():
                return candidate
            counter += 1

    def _suggest_filename(self, task: str, llm_suggest: bool) -> str:
        # Quick heuristic based on common languages
        lower_task = task.lower()
        ext = "py"
        if "javascript" in lower_task or "node" in lower_task:
            ext = "js"
        elif "typescript" in lower_task:
            ext = "ts"
        elif "bash" in lower_task or "shell" in lower_task:
            ext = "sh"
        elif "powershell" in lower_task:
            ext = "ps1"
        elif "dockerfile" in lower_task:
            return "Dockerfile"

        if llm_suggest and self.llm:
            prompt = (
                "Suggest a concise filename (no directories) for this coding task. "
                "Use a relevant extension. Return only the filename.\n"
                f"Task: {task}"
            )
            suggestion = super().execute(prompt)
            if isinstance(suggestion, str):
                safe = Path(suggestion.strip()).name
                if safe:
                    return safe
        # Fallback slug from task text
        words = "".join(
            ch if ch.isalnum() else " " for ch in task
        ).split()
        slug = "-".join(words[:5]).lower() or "solution"
        return f"{slug}.{ext}"

    def write_file(self, filename: str, content: str) -> dict:
        try:
            if ".." in filename or filename.startswith(("/", "\\")):
                return {"message": "Invalid filename"}
            safe_name = Path(filename).name or "solution.txt"
            filepath = self._ensure_unique_path(safe_name)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return {
                "message": f"Successfully wrote to {filepath}",
                "file_path": str(filepath)
            }
        except Exception as e:
            return {"message": f"Failed to write file: {e}"}

    def execute(self, task: str) -> str:
        lower_task = task.lower()
        lang_keywords = ["python", "javascript", "typescript", "bash", "powershell", "dockerfile"]
        intent_keywords = ["create a file", "write a file", "code", "kod", "script", "dosya", "yaz"]
        mentions_lang = any(kw in lower_task for kw in lang_keywords)
        wants_file = mentions_lang or any(kw in lower_task for kw in intent_keywords)

        if not self.llm:
            if wants_file:
                filename = self._suggest_filename(task, llm_suggest=False)
                return self.write_file(filename, "# TODO: implement\n")
            return super().execute(task)
        
        # Check if task asks to create a file (Simple heuristic)
        if "create a file" in lower_task or "write a file" in lower_task:
            prompt = f"""
            Extract filename and content from this task: "{task}"
            Format output exactly as: FILENAME|CONTENT
            Example: test.py|print('hello')
            """
            response = super().execute(prompt)
            if "|" in response:
                filename, content = response.split("|", 1)
                return self.write_file(filename.strip(), content.strip())

        if wants_file:
            # Default to generating code and saving it
            filename = self._suggest_filename(task, llm_suggest=True)
            prompt = f"Write the full code for this request. Return only executable code, no prose.\nRequest: {task}"
            code = super().execute(prompt)
            return self.write_file(filename, code)
        
        return super().execute(task)
