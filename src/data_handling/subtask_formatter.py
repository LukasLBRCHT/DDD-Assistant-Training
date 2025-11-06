import os

user_story_dir = "../../res/base_data/stories"
subtask_format_url = "../util/subtask_format.txt"
list_of_done_domains = [
    "g02-federalspending",
    "g03-loudoun",
    "g26-racdam",
    "g04-recycling",
    "g05-openspending",
    "g12-camperplus",
    "g19-alfred",
    "g13-planningpoker",
    "g21-badcamp",
    "30-communityaggriculture"
]


def load_tasks_from_stories():
    for file in os.scandir(user_story_dir):
        with open(file, 'r') as f:

            new_file_name = os.path.basename(f.name).removesuffix(".txt")
            if new_file_name in list_of_done_domains:
                print(new_file_name)
                continue

            # go over lines, add every one into a list
            stories = "["

            for line in f.readlines():
                line = line.replace('"', '\\"')
                stories += f'\t"{line.strip()}",\n'
            stories = stories.removesuffix(",\n")
            stories += "\n]"

            with open(subtask_format_url,'r') as format_file:
                subtask_format = format_file.read()

            json_data = subtask_format.format(stories)

            print(json_data)

            # put json into new file
            with open(f"../../res/task_data/{new_file_name}.json", "w") as json_file:
                json_file.write(json_data)


if __name__ == "__main__":
    load_tasks_from_stories()
