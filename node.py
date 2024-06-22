import re
import json
import os
import random


class PromptFromTemplate:
    PROMPT_LISTS_DIR = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "prompt-lists"
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "template": (
                    "STRING",
                    {"default": "", "multiline": True, "dynamicPrompts": True},
                ),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
            }
        }

    def __init__(self):
        self.all_lists = {}
        for list_name in self.get_all_available_lists():
            self.all_lists[list_name] = self.load_list(list_name)

    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate_prompt_from_template"
    CATEGORY = "Prompter"

    def generate_prompt_from_template(self, template, seed=0):
        random.seed(seed)

        def replace_match(match):
            list_name = match.group(1)
            list_name_parts = list_name.split(",")
            list_name = list_name_parts[0].strip()
            item_count = int(list_name_parts[1]) if len(list_name_parts) == 2 else 1
            item_count = min(item_count, 50)

            if list_name == "random":
                random_items = [self.get_random_list()(1) for _ in range(item_count)]
                return ", ".join(random_items)

            if list_name not in self.all_lists:
                return f"[{list_name}]"

            return ", ".join(self.get_random_items_from_list(list_name, item_count))

        prompt = re.sub(r"\[(.*?)\]", replace_match, template)
        print(prompt)
        return (prompt,)

    def get_all_available_lists(self):
        lists_path = os.path.join(self.PROMPT_LISTS_DIR, "lists.json")
        with open(lists_path, "r") as file:
            lists = json.load(file)
        return lists

    def get_random_list(self):
        return random.choice(list(self.all_lists.keys()))

    def get_random_items_from_list(self, list_name, item_count):
        return random.sample(self.all_lists[list_name], item_count)

    def load_list(self, list_name):
        hyphenated_list = re.sub(r"([a-z])([A-Z])", r"\1-\2", list_name).lower()
        category, name = hyphenated_list.split(".")
        lists_path = os.path.join(self.PROMPT_LISTS_DIR, f"lists/{category}/{name}.yml")
        with open(lists_path, "r") as file:
            content = file.read()
            list_data = content.split("---")[2].strip().split("\n")

        return list_data


NODE_CLASS_MAPPINGS = {
    "Prompt from template 🪴": PromptFromTemplate,
}
