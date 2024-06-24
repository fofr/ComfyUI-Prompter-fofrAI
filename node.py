import re
import json
import os
import random


class BasePrompt:
    PROMPT_LISTS_DIR = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "prompt-lists"
    )

    def __init__(self):
        self.all_lists = {}
        for list_name in self.get_all_available_lists():
            self.all_lists[list_name] = self.load_list(list_name)

    @classmethod
    def get_all_available_lists(cls):
        lists_path = os.path.join(cls.PROMPT_LISTS_DIR, "lists.json")
        with open(lists_path, "r", encoding="utf-8") as file:
            lists = json.load(file)
        return lists

    def load_list(self, list_name):
        hyphenated_list = re.sub(r"([a-z])([A-Z])", r"\1-\2", list_name).lower()
        category, name = hyphenated_list.split(".")
        lists_path = os.path.join(self.PROMPT_LISTS_DIR, f"lists/{category}/{name}.yml")
        with open(lists_path, "r", encoding="utf-8") as file:
            content = file.read()
            list_data = content.split("---")[2].strip().split("\n")

        return list_data


class PromptFromTemplate(BasePrompt):
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
                random_list_names = [self.get_random_list() for _ in range(item_count)]
                random_items = [
                    self.get_random_items_from_list(list_name, 1)[0]
                    for list_name in random_list_names
                ]
                return ", ".join(random_items)

            if list_name not in self.all_lists:
                return f"[{list_name}]"

            return ", ".join(self.get_random_items_from_list(list_name, item_count))

        prompt = re.sub(r"\[(.*?)\]", replace_match, template)
        print(prompt)
        return (prompt,)

    def get_random_list(self):
        return random.choice(list(self.all_lists.keys()))

    def get_random_items_from_list(self, list_name, item_count):
        return random.sample(self.all_lists[list_name], item_count)


class PromptListSampler(BasePrompt):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "list_name": (cls.get_all_available_lists(),),
                "mode": (["random", "sequential"], {"default": "sequential"}),
                "number_of_items": ("INT", {"default": 1, "min": 1}),
                "join_with": ("STRING", {"default": ", "}),
                "index": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 0xFFFFFFFFFFFFFFFF,
                        "control_after_generate": True,
                    },
                ),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_item_from_list"
    CATEGORY = "Prompter"

    def get_item_from_list(
        self,
        list_name,
        index=0,
        number_of_items=1,
        mode="sequential",
        join_with=", ",
        seed=0,
    ):
        random.seed(seed)

        if list_name not in self.all_lists:
            return f"[{list_name}]"

        if mode == "random":
            items = random.sample(
                self.all_lists[list_name],
                min(number_of_items, len(self.all_lists[list_name])),
            )
        else:
            index = index % len(self.all_lists[list_name])
            items = self.all_lists[list_name][index : index + number_of_items]

        return (join_with.join(items),)


NODE_CLASS_MAPPINGS = {
    "Prompt from template 🪴": PromptFromTemplate,
    "List sampler 🪴": PromptListSampler,
}
